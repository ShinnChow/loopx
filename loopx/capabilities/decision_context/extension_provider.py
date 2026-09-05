from __future__ import annotations

import math
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from ...control_plane.runtime.public_safety import public_safe_compact_text
from ...extensions.manifest import validate_extension_id
from ...extensions.runtime import (
    default_extension_state_file,
    execute_extension_runtime_binding,
    extension_catalog_entries,
    resolve_extension_binding,
)
from ..context_providers.base import (
    ContextProviderItem,
    ContextProviderRetrieval,
    ContextProviderSync,
)


EXTENSION_CONTEXT_PROVIDER_ID = "extension"
DECISION_CONTEXT_CAPABILITY_ID = "decision-context"
DECISION_CONTEXT_ADVISORY_PROVIDER_PROTOCOL = (
    "decision_context_advisory_provider_v0"
)
DECISION_CONTEXT_ADVISORY_PERMISSION = "decision_context.read"
DECISION_CONTEXT_ADVISORY_REQUEST_SCHEMA = (
    "decision_context_advisory_retrieve_request_v0"
)
DECISION_CONTEXT_ADVISORY_RESPONSE_SCHEMA = (
    "decision_context_advisory_retrieve_response_v0"
)
DECISION_CONTEXT_PROVIDER_READINESS_SCHEMA = (
    "decision_context_provider_readiness_v0"
)
MAX_EXTENSION_CONTEXT_ITEMS = 8
MAX_EXTENSION_CONTEXT_CONTENT_CHARS = 16_000
MAX_EXTENSION_CONTEXT_REF_CHARS = 512
_RESPONSE_FIELDS = {
    "schema_version",
    "ok",
    "status",
    "reason_code",
    "items",
}
_ITEM_FIELDS = {"resource_ref", "summary", "content", "score"}


def _provider_readiness(
    *,
    extension_id: str | None,
    status: str,
    installed: bool | None,
    enabled: bool | None,
    doctor_verified: bool | None,
    next_action: str | None,
) -> dict[str, Any]:
    return {
        "schema_version": DECISION_CONTEXT_PROVIDER_READINESS_SCHEMA,
        "provider_kind": "extension",
        "extension_id": extension_id,
        "status": status,
        "installed": installed,
        "enabled": enabled,
        "doctor_verified": doctor_verified,
        "next_action": next_action,
    }


def _state_file(
    config: Mapping[str, Any],
    runtime_root: str | Path | None,
) -> Path:
    value = config.get("extension_state_file")
    if value is None:
        return default_extension_state_file(runtime_root)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "extension context provider extension_state_file must be a non-empty path"
        )
    return Path(value).expanduser()


def _extension_id(config: Mapping[str, Any]) -> str | None:
    value = config.get("extension_id")
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(
            "extension context provider extension_id must be a string"
        )
    return validate_extension_id(value)


def _bounded_text(value: object, *, field: str, maximum: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > maximum:
        raise ValueError(f"extension context provider {field} is invalid")
    return value.strip()


def _public_safe_text(value: object, *, field: str, maximum: int) -> str:
    text = public_safe_compact_text(value, limit=maximum)
    if text is None:
        raise ValueError(
            f"extension context provider {field} is not public safe"
        )
    return text


def _reason_code(value: object) -> str | None:
    if value is None:
        return None
    reason = public_safe_compact_text(value, limit=120)
    if reason is None or any(character.isspace() for character in reason):
        raise ValueError(
            "extension context provider reason_code must be a public-safe token"
        )
    return reason


def _score(value: object) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("extension context provider score must be numeric")
    score = float(value)
    if not math.isfinite(score):
        raise ValueError("extension context provider score must be finite")
    return score


class DecisionContextExtensionProvider:
    """Adapt one lifecycle-gated extension to Decision Context recall.

    The extension owns transcript discovery and retrieval. This adapter owns the
    bounded wire contract and converts provider output into transient evidence; it
    never promotes that evidence into Goal, Todo, lease, or lifecycle authority.
    """

    def __init__(
        self,
        *,
        state_file: Path,
        extension_id: str,
    ) -> None:
        self.state_file = state_file
        self.extension_id = extension_id
        self.provider_id = extension_id
        self.readiness = _provider_readiness(
            extension_id=extension_id,
            status="ready",
            installed=True,
            enabled=True,
            doctor_verified=True,
            next_action=None,
        )

    def _binding(self) -> dict[str, Any]:
        return resolve_extension_binding(
            self.extension_id,
            state_file=self.state_file,
            capability_id=DECISION_CONTEXT_CAPABILITY_ID,
            protocol=DECISION_CONTEXT_ADVISORY_PROVIDER_PROTOCOL,
            permission=DECISION_CONTEXT_ADVISORY_PERMISSION,
        )

    def retrieve(
        self,
        *,
        namespace: str,
        scope_ref: str,
        query: str,
        query_summary: str,
        max_results: int,
        timeout_seconds: float,
        observed_at: str,
    ) -> ContextProviderRetrieval:
        started = time.monotonic()
        namespace = _public_safe_text(
            namespace, field="namespace", maximum=120
        )
        scope_ref = _bounded_text(scope_ref, field="scope_ref", maximum=2_048)
        query = _bounded_text(query, field="query", maximum=1_000)
        query_summary = _public_safe_text(
            query_summary, field="query_summary", maximum=220
        )
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError(
                "extension context provider max_results must be an integer"
            )
        requested_limit = min(max(1, max_results), MAX_EXTENSION_CONTEXT_ITEMS)
        binding = self._binding()
        requested_timeout = float(timeout_seconds)
        if (
            not math.isfinite(requested_timeout)
            or requested_timeout < 1
            or not requested_timeout.is_integer()
        ):
            raise ValueError(
                "extension context provider timeout_seconds must be a whole "
                "number of at least 1"
            )
        effective_timeout = min(
            int(requested_timeout),
            int(binding["timeout_seconds"]),
        )
        execution_binding = dict(binding)
        execution_binding["timeout_seconds"] = effective_timeout
        response = execute_extension_runtime_binding(
            execution_binding,
            request={
                "schema_version": DECISION_CONTEXT_ADVISORY_REQUEST_SCHEMA,
                "operation": "retrieve",
                "namespace": namespace,
                "scope_ref": scope_ref,
                "query": query,
                "query_summary": query_summary,
                "max_results": requested_limit,
                "timeout_seconds": effective_timeout,
                "observed_at": observed_at,
            },
        )
        response_fields = set(response)
        unexpected = sorted(response_fields - _RESPONSE_FIELDS)
        missing = sorted(_RESPONSE_FIELDS - response_fields)
        if unexpected or missing:
            details = []
            if unexpected:
                details.append("unsupported: " + ", ".join(unexpected))
            if missing:
                details.append("missing: " + ", ".join(missing))
            raise ValueError(
                "extension context provider response fields are invalid: "
                + "; ".join(details)
            )
        if (
            response.get("schema_version")
            != DECISION_CONTEXT_ADVISORY_RESPONSE_SCHEMA
            or response.get("ok") is not True
        ):
            raise ValueError(
                "extension context provider response has an invalid envelope"
            )
        status = str(response.get("status") or "")
        if status not in {"completed", "unavailable"}:
            raise ValueError("extension context provider status is invalid")
        raw_items = response.get("items", [])
        if (
            not isinstance(raw_items, list)
            or len(raw_items) > requested_limit
            or len(raw_items) > MAX_EXTENSION_CONTEXT_ITEMS
        ):
            raise ValueError(
                "extension context provider items must be a bounded list"
            )
        if status == "unavailable" and raw_items:
            raise ValueError(
                "an unavailable extension context provider cannot return items"
            )

        items: list[ContextProviderItem] = []
        for raw_item in raw_items:
            if not isinstance(raw_item, Mapping):
                raise ValueError(
                    "extension context provider items must be objects"
                )
            item_fields = set(raw_item)
            item_unexpected = sorted(item_fields - _ITEM_FIELDS)
            item_missing = sorted(_ITEM_FIELDS - item_fields)
            if item_unexpected or item_missing:
                details = []
                if item_unexpected:
                    details.append(
                        "unsupported: " + ", ".join(item_unexpected)
                    )
                if item_missing:
                    details.append("missing: " + ", ".join(item_missing))
                raise ValueError(
                    "extension context provider item fields are invalid: "
                    + "; ".join(details)
                )
            resource_ref = _bounded_text(
                raw_item.get("resource_ref"),
                field="resource_ref",
                maximum=MAX_EXTENSION_CONTEXT_REF_CHARS,
            )
            summary = public_safe_compact_text(
                raw_item.get("summary"), limit=220
            )
            if summary is None:
                raise ValueError(
                    "extension context provider item summary is not public safe"
                )
            content = _bounded_text(
                raw_item.get("content"),
                field="content",
                maximum=MAX_EXTENSION_CONTEXT_CONTENT_CHARS,
            )
            items.append(
                ContextProviderItem(
                    resource_ref=resource_ref,
                    summary=summary,
                    content=content,
                    score=_score(raw_item.get("score")),
                )
            )

        reason_code = _reason_code(response.get("reason_code"))
        if status == "completed" and reason_code is not None:
            raise ValueError(
                "a completed extension context provider cannot return reason_code"
            )
        if status == "unavailable" and reason_code is None:
            raise ValueError(
                "an unavailable extension context provider requires reason_code"
            )

        return ContextProviderRetrieval(
            provider=self.provider_id,
            namespace=namespace,
            status=status,
            query_summary=query_summary,
            observed_at=observed_at,
            search_performed=True,
            read_performed=bool(items),
            items=tuple(items),
            reason_code=reason_code,
            provider_version=str(binding.get("provider_version") or "") or None,
            latency_ms=int((time.monotonic() - started) * 1_000),
            requested_limit=requested_limit,
        )

    def sync(
        self,
        *,
        namespace: str,
        resources: Sequence[tuple[str, str]],
        timeout_seconds: float,
        observed_at: str,
        execute: bool,
    ) -> ContextProviderSync:
        del timeout_seconds, execute
        return ContextProviderSync(
            provider=self.provider_id,
            namespace=namespace,
            status="unavailable",
            observed_at=observed_at,
            requested_count=len(resources),
            completed_count=0,
            reason_code="read_only_provider",
        )


class _UnavailableDecisionContextExtensionProvider:
    """Represent optional extension readiness without failing the capability."""

    def __init__(
        self,
        *,
        extension_id: str | None,
        reason_code: str,
        installed: bool | None,
        enabled: bool | None,
        doctor_verified: bool | None,
        next_action: str,
    ) -> None:
        self.provider_id = extension_id or "context-provider"
        self.reason_code = reason_code
        self.readiness = _provider_readiness(
            extension_id=extension_id,
            status=reason_code,
            installed=installed,
            enabled=enabled,
            doctor_verified=doctor_verified,
            next_action=next_action,
        )

    def retrieve(
        self,
        *,
        namespace: str,
        scope_ref: str,
        query: str,
        query_summary: str,
        max_results: int,
        timeout_seconds: float,
        observed_at: str,
    ) -> ContextProviderRetrieval:
        del scope_ref, query, timeout_seconds
        namespace = _public_safe_text(
            namespace, field="namespace", maximum=120
        )
        query_summary = _public_safe_text(
            query_summary, field="query_summary", maximum=220
        )
        if isinstance(max_results, bool) or not isinstance(max_results, int):
            raise ValueError(
                "extension context provider max_results must be an integer"
            )
        requested_limit = min(max(1, max_results), MAX_EXTENSION_CONTEXT_ITEMS)
        return ContextProviderRetrieval(
            provider=self.provider_id,
            namespace=namespace,
            status="unavailable",
            query_summary=query_summary,
            observed_at=observed_at,
            search_performed=False,
            read_performed=False,
            reason_code=self.reason_code,
            requested_limit=requested_limit,
        )

    def sync(
        self,
        *,
        namespace: str,
        resources: Sequence[tuple[str, str]],
        timeout_seconds: float,
        observed_at: str,
        execute: bool,
    ) -> ContextProviderSync:
        del timeout_seconds, execute
        namespace = _public_safe_text(namespace, field="namespace", maximum=120)
        return ContextProviderSync(
            provider=self.provider_id,
            namespace=namespace,
            status="unavailable",
            observed_at=observed_at,
            requested_count=len(resources),
            completed_count=0,
            reason_code=self.reason_code,
        )


def _implements_advisory_context(entry: Mapping[str, Any]) -> bool:
    implementations = entry.get("implementations")
    return isinstance(implementations, list) and any(
        isinstance(item, Mapping)
        and item.get("capability_id") == DECISION_CONTEXT_CAPABILITY_ID
        and item.get("protocol") == DECISION_CONTEXT_ADVISORY_PROVIDER_PROTOCOL
        for item in implementations
    )


def _unavailable_provider(
    *,
    extension_id: str | None,
    reason_code: str,
    installed: bool | None,
    enabled: bool | None,
    doctor_verified: bool | None,
    next_action: str,
) -> _UnavailableDecisionContextExtensionProvider:
    return _UnavailableDecisionContextExtensionProvider(
        extension_id=extension_id,
        reason_code=reason_code,
        installed=installed,
        enabled=enabled,
        doctor_verified=doctor_verified,
        next_action=next_action,
    )


def build_extension_context_provider(
    config: Mapping[str, Any],
    *,
    runtime_root: str | Path | None = None,
) -> DecisionContextExtensionProvider | _UnavailableDecisionContextExtensionProvider:
    supported = {"provider", "extension_id", "extension_state_file"}
    unexpected = sorted(set(config) - supported)
    if unexpected:
        raise ValueError(
            "extension context provider config contains unsupported fields: "
            + ", ".join(unexpected)
        )
    state_file = _state_file(config, runtime_root)
    configured_extension_id = _extension_id(config)
    try:
        catalog = extension_catalog_entries(state_file=state_file)
    except ValueError:
        return _unavailable_provider(
            extension_id=configured_extension_id,
            reason_code="extension_state_unavailable",
            installed=None,
            enabled=None,
            doctor_verified=None,
            next_action="repair_extension_state",
        )

    candidates = [entry for entry in catalog if _implements_advisory_context(entry)]
    if configured_extension_id is not None:
        selected = next(
            (
                entry
                for entry in catalog
                if isinstance(entry.get("provider"), Mapping)
                and entry["provider"].get("id") == configured_extension_id
            ),
            None,
        )
        if selected is None:
            return _unavailable_provider(
                extension_id=configured_extension_id,
                reason_code="extension_not_installed",
                installed=False,
                enabled=False,
                doctor_verified=False,
                next_action="install_extension",
            )
        if not _implements_advisory_context(selected):
            return _unavailable_provider(
                extension_id=configured_extension_id,
                reason_code="extension_incompatible",
                installed=True,
                enabled=bool(selected["provider"].get("enabled")),
                doctor_verified=bool(selected["provider"].get("ready")),
                next_action="install_compatible_extension",
            )
    else:
        ready = [
            entry
            for entry in candidates
            if isinstance(entry.get("provider"), Mapping)
            and entry["provider"].get("ready") is True
        ]
        if len(ready) > 1:
            return _unavailable_provider(
                extension_id=None,
                reason_code="extension_provider_ambiguous",
                installed=True,
                enabled=True,
                doctor_verified=True,
                next_action="select_extension_id",
            )
        if len(ready) == 1:
            selected = ready[0]
        elif len(candidates) == 1:
            selected = candidates[0]
        else:
            return _unavailable_provider(
                extension_id=None,
                reason_code=(
                    "extension_provider_not_installed"
                    if not candidates
                    else "extension_provider_not_ready"
                ),
                installed=bool(candidates),
                enabled=any(
                    bool(entry["provider"].get("enabled"))
                    for entry in candidates
                ),
                doctor_verified=False,
                next_action=(
                    "install_or_select_extension"
                    if not candidates
                    else "select_or_repair_extension"
                ),
            )

    provider = selected["provider"]
    extension_id = str(provider["id"])
    if provider.get("enabled") is not True:
        return _unavailable_provider(
            extension_id=extension_id,
            reason_code="extension_disabled",
            installed=True,
            enabled=False,
            doctor_verified=False,
            next_action="enable_extension",
        )
    if provider.get("ready") is not True:
        return _unavailable_provider(
            extension_id=extension_id,
            reason_code="extension_doctor_not_ready",
            installed=True,
            enabled=True,
            doctor_verified=False,
            next_action="run_extension_doctor",
        )
    return DecisionContextExtensionProvider(
        state_file=state_file,
        extension_id=extension_id,
    )
