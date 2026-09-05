import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import { spawn } from "node:child_process";
import test from "node:test";

import {
  canonicalCoordinationRecord,
  canonicalTodoDomainRecord,
  canonicalCoordinationTodoRecord,
  COORDINATION_STATE_CONTRACT,
  TODO_CANONICAL_READ_RECORD_FIELDS,
  TODO_CANONICAL_READ_RECORD_SCHEMA,
  TODO_DOMAIN_ITEM_SCHEMA,
  TODO_DOMAIN_RECORD_CONTRACT,
} from "../../loopx/control_plane/coordination/coordination_state_contract.ts";
import {
  LOCAL_AUTHORITY_SHADOW_EVIDENCE_SCHEMA as GENERATED_SHADOW_EVIDENCE_SCHEMA,
  LOCAL_AUTHORITY_SHADOW_OUTBOX_ENTRY_SCHEMA as GENERATED_SHADOW_OUTBOX_ENTRY_SCHEMA,
  LOCAL_AUTHORITY_SHADOW_REQUEST_SCHEMA as GENERATED_SHADOW_REQUEST_SCHEMA,
  LOCAL_COORDINATION_TODO_LIST_REQUEST_SCHEMA as GENERATED_LIST_REQUEST_SCHEMA,
} from "../../loopx/control_plane/coordination/coordination_state_contract.generated.ts";
import {
  LOCAL_AUTHORITY_SHADOW_EVIDENCE_SCHEMA as RUNTIME_SHADOW_EVIDENCE_SCHEMA,
  LOCAL_AUTHORITY_SHADOW_REQUEST_SCHEMA as RUNTIME_SHADOW_REQUEST_SCHEMA,
} from "../../loopx/control_plane/coordination/local_authority_shadow.ts";
import {
  LOCAL_AUTHORITY_SHADOW_OUTBOX_ENTRY_SCHEMA as RUNTIME_SHADOW_OUTBOX_ENTRY_SCHEMA,
} from "../../loopx/control_plane/coordination/local_authority_shadow_outbox.ts";
import {
  LOCAL_COORDINATION_TODO_LIST_REQUEST_SCHEMA as RUNTIME_LIST_REQUEST_SCHEMA,
} from "../../loopx/control_plane/coordination/local_authority_runtime.ts";

const TODO = {
  schema_version: "todo_item_v0",
  todo_id: "todo_contract",
  role: "agent",
  status: "open",
  done: false,
  text: "Keep one cross-language state contract.",
  archive_state: "active",
  source_section: "Agent Todo",
  priority: "P0",
  evidence: "contract:test",
};

function pythonContract(): Promise<Record<string, unknown>> {
  return new Promise((resolve, reject) => {
    const child = spawn("python3", ["-c", [
      "import json",
      "from loopx.control_plane.coordination.coordination_state_contract import COORDINATION_STATE_CONTRACT",
      "print(json.dumps(COORDINATION_STATE_CONTRACT, default=dict, sort_keys=True, separators=(',', ':')))",
    ].join("; ")], { cwd: process.cwd() });
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8").on("data", (chunk: string) => stdout += chunk);
    child.stderr.setEncoding("utf8").on("data", (chunk: string) => stderr += chunk);
    child.on("error", reject);
    child.on("close", (code) => code === 0
      ? resolve(JSON.parse(stdout) as Record<string, unknown>)
      : reject(new Error(stderr)));
  });
}

test("coordination state contract generates identical cross-language bindings", async () => {
  const bundled = JSON.parse(await readFile(
    new URL("../../loopx/control_plane/coordination/coordination_state_contract_v0.json", import.meta.url),
    "utf8",
  ));
  assert.deepEqual(COORDINATION_STATE_CONTRACT, bundled);
  assert.deepEqual(await pythonContract(), bundled);
  assert.equal(TODO_CANONICAL_READ_RECORD_SCHEMA, "loopx_todo_canonical_read_record_v0");
  assert.equal(new Set(TODO_CANONICAL_READ_RECORD_FIELDS).size,
    TODO_CANONICAL_READ_RECORD_FIELDS.length);
});

test("generated coordination bindings are current", async () => {
  await new Promise<void>((resolve, reject) => {
    const child = spawn(
      "python3",
      ["scripts/generate_coordination_state_contract.py", "--check"],
      { cwd: process.cwd() },
    );
    let stderr = "";
    child.stderr.setEncoding("utf8").on("data", (chunk: string) => stderr += chunk);
    child.on("error", reject);
    child.on("close", (code) => code === 0 ? resolve() : reject(new Error(stderr)));
  });
});

test("TypeScript runtime re-exports generated local-authority protocol schemas", () => {
  assert.equal(RUNTIME_LIST_REQUEST_SCHEMA, GENERATED_LIST_REQUEST_SCHEMA);
});

test("TypeScript shadow runtimes re-export generated protocol schemas", () => {
  assert.equal(RUNTIME_SHADOW_REQUEST_SCHEMA, GENERATED_SHADOW_REQUEST_SCHEMA);
  assert.equal(RUNTIME_SHADOW_EVIDENCE_SCHEMA, GENERATED_SHADOW_EVIDENCE_SCHEMA);
  assert.equal(RUNTIME_SHADOW_OUTBOX_ENTRY_SCHEMA, GENERATED_SHADOW_OUTBOX_ENTRY_SCHEMA);
});

test("provider-bound Todo records preserve every declared field", () => {
  assert.deepEqual(canonicalCoordinationTodoRecord(TODO), TODO);
});

test("generated and derived contracts are deeply immutable at runtime", () => {
  function verify(value: unknown): void {
    if (value === null || typeof value !== "object") return;
    assert.ok(Object.isFrozen(value));
    for (const child of Object.values(value)) verify(child);
    assert.throws(() => Object.assign(value, {injected: true}), TypeError);
  }
  verify(COORDINATION_STATE_CONTRACT);
  verify(TODO_DOMAIN_RECORD_CONTRACT);
  assert.equal(Reflect.set(COORDINATION_STATE_CONTRACT.todo_read_record.fields,
    "0", "mutated"), false);
  assert.deepEqual(canonicalCoordinationTodoRecord(TODO), TODO);
});

test("domain and projection fields are disjoint without weakening legacy v0", () => {
  const { source_section: _section, ...fields } = TODO;
  const domain = { ...fields, schema_version: TODO_DOMAIN_ITEM_SCHEMA };
  assert.deepEqual(canonicalTodoDomainRecord(domain), domain);
  assert.ok(TODO_DOMAIN_RECORD_CONTRACT.fields.includes("archive_state"));
  for (const field of COORDINATION_STATE_CONTRACT.todo_projection_metadata.fields) {
    assert.ok(!TODO_DOMAIN_RECORD_CONTRACT.fields.includes(field));
    assert.throws(() => canonicalTodoDomainRecord({ ...domain, [field]: "fake" }), /unversioned fields/);
  }
  assert.throws(() => canonicalCoordinationTodoRecord(fields), /omits required fields: source_section/);
  assert.throws(() => canonicalTodoDomainRecord({ ...domain, archive_state: "deferred" }), /invalid required semantics/);
  assert.throws(() => canonicalTodoDomainRecord({ ...domain, archive_state: null }), /invalid required semantics/);
  assert.throws(() => canonicalTodoDomainRecord({ ...domain, status: ["open"] }), /invalid required semantics/);
});

test("provider-bound Todo records reject silent data loss", () => {
  assert.throws(
    () => canonicalCoordinationTodoRecord({ ...TODO, new_machine_field: true }),
    /unversioned fields: new_machine_field/,
  );
  const { text: _text, ...incomplete } = TODO;
  assert.throws(
    () => canonicalCoordinationTodoRecord(incomplete),
    /omits required fields: text/,
  );
});

test("record validation rejects a required field outside the declared schema", () => {
  assert.throws(
    () => canonicalCoordinationRecord(
      { todo_id: "todo_contract" },
      { fields: ["todo_id"], required_fields: ["todo_id", "role"] },
      "test record",
    ),
    /required fields are absent from fields: role/,
  );
});
