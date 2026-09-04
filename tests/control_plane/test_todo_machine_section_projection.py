from __future__ import annotations

from copy import deepcopy

import pytest

from loopx.control_plane.todos.machine_section_projection import (
    TodoSectionProjectionError,
    inspect_todo_section_projection,
    render_canonical_todo_sections,
)
from loopx.cli import build_parser
from loopx.cli_commands import todo as todo_command


SOURCE = """---
status: active
---

# Goal

Human rationale stays here.

## User Todo / Owner Review Reading Queue

- [ ] stale user text
  <!-- loopx:todo todo_id=todo_stale status=open -->

## Notes

Do not rewrite this paragraph.

## Agent Todo

- [ ] stale agent text
  <!-- loopx:todo todo_id=todo_old status=open -->

## Next Action

- Continue the approved migration.
"""


def _records() -> list[dict[str, object]]:
    return [
        {
            "schema_version": "todo_item_v0",
            "todo_id": "todo_agent",
            "role": "agent",
            "status": "open",
            "done": False,
            "text": "[P0] Move one complete transaction.",
            "archive_state": "active",
            "source_section": "Agent Todo",
            "index": 1,
            "priority": "P0",
            "title": "Move one complete transaction.",
            "task_class": "advancement_task",
            "action_kind": "migrate_transaction",
            "required_capabilities": ["filesystem_write"],
            "claimed_by": "codex-worker",
            "updated_at": "2026-09-05T00:00:00Z",
        },
        {
            "schema_version": "todo_item_v0",
            "todo_id": "todo_user",
            "role": "user",
            "status": "blocked",
            "done": False,
            "text": "Approve the bounded cutover.",
            "archive_state": "active",
            "source_section": "User Todo / Owner Review Reading Queue",
            "index": 1,
            "task_class": "user_gate",
            "decision_scope": {
                "schema_version": "decision_scope_v0",
                "kind": "direction",
                "granularity": "action",
                "scope_key": "authority_cutover",
            },
            "global_gate": True,
        },
    ]


def test_projection_replaces_only_machine_sections_and_is_idempotent() -> None:
    projected = render_canonical_todo_sections(
        SOURCE,
        _records(),
        provider_revision="sha256:abc123",
    )

    assert projected.changed is True
    assert "Human rationale stays here." in projected.markdown
    assert "Do not rewrite this paragraph." in projected.markdown
    assert "Continue the approved migration." in projected.markdown
    assert "stale user text" not in projected.markdown
    assert "todo_agent" in projected.markdown
    assert "todo_user" in projected.markdown
    markers = inspect_todo_section_projection(projected.markdown)
    assert markers["section_count"] == 2
    assert {item["revision"] for item in markers["sections"]} == {"sha256:abc123"}

    replay = render_canonical_todo_sections(
        projected.markdown,
        _records(),
        provider_revision="sha256:abc123",
    )
    assert replay.changed is False
    assert replay.markdown == projected.markdown
    assert replay.rendered_sha256 == projected.rendered_sha256


def test_projection_rejects_missing_role_section() -> None:
    source = "# Goal\n\nHuman introduction.\n\n## Agent Todo\n\n- [ ] old\n\n## Next Action\n\n- Continue.\n"
    with pytest.raises(TodoSectionProjectionError, match="required Todo sections: user"):
        render_canonical_todo_sections(
            source,
            [_records()[0]],
            provider_revision="rev-9",
        )


def test_projection_rejects_unknown_or_derived_field_loss() -> None:
    unknown = deepcopy(_records())
    unknown[0]["future_field"] = "must-not-disappear"
    with pytest.raises(ValueError, match="unversioned fields: future_field"):
        render_canonical_todo_sections(SOURCE, unknown, provider_revision="rev-1")

    derived = deepcopy(_records())
    derived[0]["resume_ready"] = True
    with pytest.raises(TodoSectionProjectionError, match="resume_ready"):
        render_canonical_todo_sections(SOURCE, derived, provider_revision="rev-1")


def test_projection_rejects_duplicate_sections_and_unsafe_revision() -> None:
    duplicate = SOURCE + "\n## Agent Todo\n\n- [ ] duplicate\n"
    with pytest.raises(TodoSectionProjectionError, match="multiple agent"):
        render_canonical_todo_sections(duplicate, _records(), provider_revision="rev-1")
    with pytest.raises(TodoSectionProjectionError, match="public-safe token"):
        render_canonical_todo_sections(SOURCE, _records(), provider_revision="rev 1")


def test_project_markdown_cli_requires_promoted_exact_revision(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    state_path = tmp_path / "ACTIVE_GOAL_STATE.md"
    state_path.write_text(SOURCE, encoding="utf-8")
    parser = build_parser()

    def run(
        extra: list[str], payload: dict[str, object] | None
    ) -> tuple[int, dict[str, object]]:
        captured: dict[str, object] = {}
        monkeypatch.setattr(
            todo_command,
            "load_registry",
            lambda _path: {"common_runtime_root": str(tmp_path / "runtime")},
        )
        monkeypatch.setattr(
            todo_command,
            "read_canonical_todos_if_promoted",
            lambda **_kwargs: payload,
        )
        monkeypatch.setattr(
            todo_command,
            "resolve_todo_state_path",
            lambda **_kwargs: (tmp_path, state_path),
        )
        result = todo_command.handle_todo_command(
            parser.parse_args(
                [
                    "todo",
                    "project-markdown",
                    "--goal-id",
                    "goal-a",
                    "--provider-revision",
                    "rev-1",
                    *extra,
                ]
            ),
            registry_path=tmp_path / "registry.json",
            runtime_root_arg=None,
            print_payload=lambda value, *_args: captured.update(value),
            append_cli_rollout_event=lambda *_args, **_kwargs: None,
        )
        return result, captured

    failed, failure = run([], None)
    assert failed == 1
    assert "requires promoted canonical authority" in str(failure["error"])
    assert state_path.read_text(encoding="utf-8") == SOURCE

    canonical_payload = {
        "todos": _records(),
        "source_authority": "file_v0",
        "provider_revision": "rev-1",
        "cursor": "7",
    }
    preview_result, preview = run([], canonical_payload)
    assert preview_result == 0
    assert preview["dry_run"] is True
    assert preview["parse_render_parity"] is True
    assert state_path.read_text(encoding="utf-8") == SOURCE

    mismatch_result, mismatch = run(
        [], {**canonical_payload, "provider_revision": "rev-2"}
    )
    assert mismatch_result == 1
    assert "does not match" in str(mismatch["error"])
    assert state_path.read_text(encoding="utf-8") == SOURCE

    write_result, written = run(["--execute"], canonical_payload)
    assert write_result == 0
    assert written["executed"] is True
    assert written["narrative_preserved"] is True
    assert "todo_agent" in state_path.read_text(encoding="utf-8")


def test_project_markdown_cli_uses_raw_provider_records(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    state_path = tmp_path / "ACTIVE_GOAL_STATE.md"
    state_path.write_text(SOURCE, encoding="utf-8")
    raw_records = _records()
    monkeypatch.setattr(
        todo_command,
        "load_registry",
        lambda _path: {"common_runtime_root": str(tmp_path / "runtime")},
    )
    monkeypatch.setattr(
        todo_command,
        "read_canonical_todos_if_promoted",
        lambda **_kwargs: {
            "todos": raw_records,
            "source_authority": "file_v0",
            "provider_revision": "rev-1",
        },
    )
    monkeypatch.setattr(
        todo_command,
        "list_goal_todos",
        lambda **_kwargs: pytest.fail("projection must not consume the enriched list view"),
    )
    monkeypatch.setattr(
        todo_command,
        "resolve_todo_state_path",
        lambda **_kwargs: (tmp_path, state_path),
    )
    captured: dict[str, object] = {}

    result = todo_command.handle_todo_command(
        build_parser().parse_args(
            [
                "todo",
                "project-markdown",
                "--goal-id",
                "goal-a",
                "--provider-revision",
                "rev-1",
            ]
        ),
        registry_path=tmp_path / "registry.json",
        runtime_root_arg=None,
        print_payload=lambda value, *_args: captured.update(value),
        append_cli_rollout_event=lambda *_args, **_kwargs: None,
    )

    assert result == 0
    assert captured["todo_count"] == len(raw_records)


def test_project_markdown_cli_publishes_with_atomic_replace(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    state_path = tmp_path / "ACTIVE_GOAL_STATE.md"
    state_path.write_text(SOURCE, encoding="utf-8")
    monkeypatch.setattr(
        todo_command,
        "load_registry",
        lambda _path: {"common_runtime_root": str(tmp_path / "runtime")},
    )
    monkeypatch.setattr(
        todo_command,
        "read_canonical_todos_if_promoted",
        lambda **_kwargs: {
            "todos": _records(),
            "source_authority": "file_v0",
            "provider_revision": "rev-1",
        },
    )
    monkeypatch.setattr(
        todo_command,
        "resolve_todo_state_path",
        lambda **_kwargs: (tmp_path, state_path),
    )
    replacements: list[tuple[object, object]] = []
    real_replace = todo_command.os.replace

    def record_replace(source, target) -> None:
        replacements.append((source, target))
        real_replace(source, target)

    monkeypatch.setattr(todo_command.os, "replace", record_replace)

    result = todo_command.handle_todo_command(
        build_parser().parse_args(
            [
                "todo",
                "project-markdown",
                "--goal-id",
                "goal-a",
                "--provider-revision",
                "rev-1",
                "--execute",
            ]
        ),
        registry_path=tmp_path / "registry.json",
        runtime_root_arg=None,
        print_payload=lambda *_args: None,
        append_cli_rollout_event=lambda *_args, **_kwargs: None,
    )

    assert result == 0
    assert len(replacements) == 1
    temporary, target = replacements[0]
    assert target == state_path
    assert temporary != target
    assert "todo_agent" in state_path.read_text(encoding="utf-8")
