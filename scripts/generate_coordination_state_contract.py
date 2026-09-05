#!/usr/bin/env python3
"""Generate Python and TypeScript bindings for the coordination contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from pprint import pformat
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = (
    ROOT
    / "loopx"
    / "control_plane"
    / "coordination"
    / "coordination_state_contract_v0.json"
)
PYTHON_PATH = CONTRACT_PATH.with_name("coordination_state_contract_generated.py")
TYPESCRIPT_PATH = CONTRACT_PATH.with_name("coordination_state_contract.generated.ts")

EXPECTED_TOP_LEVEL_KEYS = {
    "schema_version", "todo_read_record", "todo_domain_record",
    "todo_projection_metadata", "compatibility",
    "local_authority_protocol",
    "runtime_shadow_protocol",
    "local_authority_shadow_protocol",
    "legacy_writer_fence_protocol",
}
EXPECTED_TODO_KEYS = {
    "schema_version",
    "item_schema_version",
    "fields",
    "required_fields",
}
EXPECTED_COMPATIBILITY = {
    "unknown_field_policy": "reject",
    "field_removal_policy": "maintainer_approval_required",
    "markdown_role": "human_workbench_and_compatibility_projection",
}
LOCAL_AUTHORITY_PROTOCOL_KEYS = (
    "mutation_request_schema",
    "mutation_result_schema",
    "todo_read_request_schema",
    "todo_read_result_schema",
    "todo_list_request_schema",
    "todo_list_result_schema",
    "promotion_request_schema",
    "promotion_result_schema",
    "promotion_receipt_schema",
)
RUNTIME_SHADOW_PROTOCOL_KEYS = (
    "commit_request_schema",
    "commit_result_schema",
    "receipt_schema",
    "inspect_request_schema",
    "inspect_result_schema",
    "bootstrap_request_schema",
    "bootstrap_result_schema",
    "rollback_request_schema",
    "rollback_result_schema",
    "qualify_request_schema",
    "qualify_result_schema",
    "todo_read_request_schema",
    "todo_read_result_schema",
)
LOCAL_AUTHORITY_SHADOW_PROTOCOL_KEYS = (
    "binding_schema",
    "config_schema",
    "request_schema",
    "projection_schema",
    "evidence_schema",
    "observation_receipt_schema",
    "outbox_entry_schema",
    "outbox_commit_schema",
    "drain_cursor_schema",
    "transaction_projection_schema",
    "commit_entry_request_schema",
    "commit_entry_result_schema",
    "read_request_schema",
    "read_result_schema",
    "event_schema",
    "transaction_receipt_schema",
    "transaction_evidence_schema",
)
LEGACY_WRITER_FENCE_PROTOCOL_KEYS = (
    "fence_schema",
    "engage_request_schema",
    "result_schema",
    "write_check_request_schema",
    "write_check_result_schema",
)
LEGACY_WRITER_FENCE_CONSTANT_NAMES = {
    "fence_schema": "LEGACY_COORDINATION_WRITER_FENCE_SCHEMA",
    "engage_request_schema": "LEGACY_COORDINATION_WRITER_FENCE_ENGAGE_REQUEST_SCHEMA",
    "result_schema": "LEGACY_COORDINATION_WRITER_FENCE_RESULT_SCHEMA",
    "write_check_request_schema": "LEGACY_COORDINATION_WRITE_CHECK_REQUEST_SCHEMA",
    "write_check_result_schema": "LEGACY_COORDINATION_WRITE_CHECK_RESULT_SCHEMA",
}


def _string_list(value: object, *, label: str) -> list[str]:
    if (
        not isinstance(value, list)
        or not value
        or any(not isinstance(item, str) or not item for item in value)
    ):
        raise ValueError(f"{label} must contain non-empty strings")
    if len(set(value)) != len(value):
        raise ValueError(f"{label} must not contain duplicates")
    return value


def load_contract() -> dict[str, Any]:
    raw: object = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or set(raw) != EXPECTED_TOP_LEVEL_KEYS:
        raise ValueError("coordination contract has unexpected top-level fields")
    if raw.get("schema_version") != "loopx_coordination_state_contract_v0":
        raise ValueError("coordination contract schema mismatch")
    todo = raw.get("todo_read_record")
    if not isinstance(todo, dict) or set(todo) != EXPECTED_TODO_KEYS:
        raise ValueError("Todo record contract has unexpected fields")
    for field in ("schema_version", "item_schema_version"):
        if not isinstance(todo.get(field), str) or not todo[field]:
            raise ValueError(f"todo_read_record.{field} must be a non-empty string")
    fields = _string_list(todo.get("fields"), label="todo_read_record.fields")
    required = _string_list(
        todo.get("required_fields"), label="todo_read_record.required_fields"
    )
    missing = sorted(set(required).difference(fields))
    if missing:
        raise ValueError(
            "todo_read_record.required_fields are absent from fields: "
            + ", ".join(missing)
        )
    protocol = raw.get("local_authority_protocol")
    if not isinstance(protocol, dict) or tuple(protocol) != LOCAL_AUTHORITY_PROTOCOL_KEYS:
        raise ValueError("local authority protocol has unexpected fields or order")
    if any(
        not isinstance(protocol.get(key), str) or not protocol[key]
        for key in LOCAL_AUTHORITY_PROTOCOL_KEYS
    ):
        raise ValueError("local authority protocol schemas must be non-empty strings")
    if len(set(protocol.values())) != len(protocol):
        raise ValueError("local authority protocol schemas must be unique")
    runtime_shadow = raw.get("runtime_shadow_protocol")
    if (
        not isinstance(runtime_shadow, dict)
        or tuple(runtime_shadow) != RUNTIME_SHADOW_PROTOCOL_KEYS
    ):
        raise ValueError("runtime shadow protocol has unexpected fields or order")
    if any(
        not isinstance(runtime_shadow.get(key), str) or not runtime_shadow[key]
        for key in RUNTIME_SHADOW_PROTOCOL_KEYS
    ):
        raise ValueError("runtime shadow protocol schemas must be non-empty strings")
    if len(set(runtime_shadow.values())) != len(runtime_shadow):
        raise ValueError("runtime shadow protocol schemas must be unique")
    if set(protocol.values()) & set(runtime_shadow.values()):
        raise ValueError("protocol schemas must be unique across families")
    local_shadow = raw.get("local_authority_shadow_protocol")
    if (
        not isinstance(local_shadow, dict)
        or tuple(local_shadow) != LOCAL_AUTHORITY_SHADOW_PROTOCOL_KEYS
    ):
        raise ValueError("local authority shadow protocol has unexpected fields or order")
    if any(
        not isinstance(local_shadow.get(key), str) or not local_shadow[key]
        for key in LOCAL_AUTHORITY_SHADOW_PROTOCOL_KEYS
    ):
        raise ValueError("local authority shadow protocol schemas must be non-empty strings")
    if len(set(local_shadow.values())) != len(local_shadow):
        raise ValueError("local authority shadow protocol schemas must be unique")
    writer_fence = raw.get("legacy_writer_fence_protocol")
    if (
        not isinstance(writer_fence, dict)
        or tuple(writer_fence) != LEGACY_WRITER_FENCE_PROTOCOL_KEYS
    ):
        raise ValueError("legacy writer fence protocol has unexpected fields or order")
    if any(
        not isinstance(writer_fence.get(key), str) or not writer_fence[key]
        for key in LEGACY_WRITER_FENCE_PROTOCOL_KEYS
    ):
        raise ValueError("legacy writer fence protocol schemas must be non-empty strings")
    if len(set(writer_fence.values())) != len(writer_fence):
        raise ValueError("legacy writer fence protocol schemas must be unique")
    if raw.get("compatibility") != EXPECTED_COMPATIBILITY:
        raise ValueError("coordination contract compatibility policy mismatch")
    projection = raw["todo_projection_metadata"]
    if not isinstance(projection, dict) or set(projection) != {"fields", "required_fields"}:
        raise ValueError("Todo projection contract has unexpected fields")
    projection_fields = _string_list(projection["fields"], label="projection.fields")
    projection_required = _string_list(projection["required_fields"], label="projection.required_fields")
    if not set(projection_required) <= set(projection_fields) <= set(fields):
        raise ValueError("Todo projection fields are not declared")
    domain = raw["todo_domain_record"]
    if not isinstance(domain, dict) or set(domain) != {
        "schema_version", "item_schema_version", "fields_from", "exclude_fields_from", "required_fields",
    }:
        raise ValueError("Todo domain contract has unexpected fields")
    if domain["fields_from"] != "todo_read_record" or domain["exclude_fields_from"] != "todo_projection_metadata":
        raise ValueError("Todo domain field sources are invalid")
    for field in ("schema_version", "item_schema_version"):
        if not isinstance(domain[field], str) or not domain[field]:
            raise ValueError("Todo domain schema versions must be non-empty strings")
    domain_required = _string_list(domain["required_fields"], label="domain.required_fields")
    if not set(domain_required) <= set(fields) - set(projection_fields):
        raise ValueError("Todo domain required fields are not declared")
    return raw


def render_python(contract: dict[str, Any]) -> str:
    literal = pformat(contract, width=88, sort_dicts=False)
    protocol = contract["local_authority_protocol"]
    local_constants = "\n".join(
        f"LOCAL_COORDINATION_{key.upper()}: Final[str] = {protocol[key]!r}"
        for key in LOCAL_AUTHORITY_PROTOCOL_KEYS
    )
    runtime_shadow = contract["runtime_shadow_protocol"]
    shadow_constants = "\n".join(
        f"COORDINATION_RUNTIME_SHADOW_{key.upper()}: Final[str] = "
        f"{runtime_shadow[key]!r}"
        for key in RUNTIME_SHADOW_PROTOCOL_KEYS
    )
    local_shadow = contract["local_authority_shadow_protocol"]
    local_shadow_constants = "\n".join(
        f"LOCAL_AUTHORITY_SHADOW_{key.upper()}: Final[str] = {local_shadow[key]!r}"
        for key in LOCAL_AUTHORITY_SHADOW_PROTOCOL_KEYS
    )
    writer_fence = contract["legacy_writer_fence_protocol"]
    writer_fence_constants = "\n".join(
        f"{LEGACY_WRITER_FENCE_CONSTANT_NAMES[key]}: Final[str] = "
        f"{writer_fence[key]!r}"
        for key in LEGACY_WRITER_FENCE_PROTOCOL_KEYS
    )
    return (
        '"""Generated from coordination_state_contract_v0.json; do not edit."""\n\n'
        "from __future__ import annotations\n\n"
        "from types import MappingProxyType\n"
        "from typing import Any, Final\n\n"
        "def _freeze(value: Any) -> Any:\n"
        "    if isinstance(value, dict):\n"
        "        return MappingProxyType({key: _freeze(item) for key, item in value.items()})\n"
        "    if isinstance(value, list):\n"
        "        return tuple(_freeze(item) for item in value)\n"
        "    return value\n\n"
        f"COORDINATION_STATE_CONTRACT: Final = _freeze({literal})\n"
        f"{local_constants}\n\n"
        f"{shadow_constants}\n\n"
        f"{local_shadow_constants}\n\n"
        f"{writer_fence_constants}\n"
    )


def render_typescript(contract: dict[str, Any]) -> str:
    literal = json.dumps(contract, indent=2, ensure_ascii=False)
    local_constants = "\n".join(
        f"export const LOCAL_COORDINATION_{key.upper()} = "
        f"COORDINATION_STATE_CONTRACT.local_authority_protocol.{key};"
        for key in LOCAL_AUTHORITY_PROTOCOL_KEYS
    )
    shadow_constants = "\n".join(
        f"export const COORDINATION_RUNTIME_SHADOW_{key.upper()} = "
        f"COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.{key};"
        for key in RUNTIME_SHADOW_PROTOCOL_KEYS
    )
    local_shadow_constants = "\n".join(
        f"export const LOCAL_AUTHORITY_SHADOW_{key.upper()} = "
        f"COORDINATION_STATE_CONTRACT.local_authority_shadow_protocol.{key};"
        for key in LOCAL_AUTHORITY_SHADOW_PROTOCOL_KEYS
    )
    writer_fence_constants = "\n".join(
        f"export const {LEGACY_WRITER_FENCE_CONSTANT_NAMES[key]} = "
        f"COORDINATION_STATE_CONTRACT.legacy_writer_fence_protocol.{key};"
        for key in LEGACY_WRITER_FENCE_PROTOCOL_KEYS
    )
    return (
        "// Generated from coordination_state_contract_v0.json; do not edit.\n\n"
        "function deepFreeze<T>(value: T): T {\n"
        "  if (value !== null && typeof value === 'object') {\n"
        "    for (const child of Object.values(value)) deepFreeze(child);\n"
        "    Object.freeze(value);\n"
        "  }\n"
        "  return value;\n"
        "}\n\n"
        f"export const COORDINATION_STATE_CONTRACT = deepFreeze({literal} as const);\n"
        f"{local_constants}\n\n"
        f"{shadow_constants}\n\n"
        f"{local_shadow_constants}\n\n"
        f"{writer_fence_constants}\n"
    )


def update(path: Path, content: str, *, check: bool) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return True
    if check:
        print(f"stale generated coordination contract: {path.relative_to(ROOT)}", file=sys.stderr)
        return False
    path.write_text(content, encoding="utf-8")
    print(f"generated {path.relative_to(ROOT)}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    contract = load_contract()
    current = [
        update(PYTHON_PATH, render_python(contract), check=args.check),
        update(TYPESCRIPT_PATH, render_typescript(contract), check=args.check),
    ]
    return 0 if all(current) else 1


if __name__ == "__main__":
    raise SystemExit(main())
