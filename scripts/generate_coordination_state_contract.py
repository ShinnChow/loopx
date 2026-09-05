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

EXPECTED_TOP_LEVEL_KEYS = {"schema_version", "todo_read_record", "compatibility"}
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
    if raw.get("compatibility") != EXPECTED_COMPATIBILITY:
        raise ValueError("coordination contract compatibility policy mismatch")
    return raw


def render_python(contract: dict[str, Any]) -> str:
    literal = pformat(contract, width=88, sort_dicts=False)
    return (
        '"""Generated from coordination_state_contract_v0.json; do not edit."""\n\n'
        "from __future__ import annotations\n\n"
        "from typing import Final\n\n"
        f"COORDINATION_STATE_CONTRACT: Final = {literal}\n"
    )


def render_typescript(contract: dict[str, Any]) -> str:
    literal = json.dumps(contract, indent=2, ensure_ascii=False)
    return (
        "// Generated from coordination_state_contract_v0.json; do not edit.\n\n"
        f"export const COORDINATION_STATE_CONTRACT = {literal} as const;\n"
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
