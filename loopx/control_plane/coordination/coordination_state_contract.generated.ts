// Generated from coordination_state_contract_v0.json; do not edit.

function deepFreeze<T>(value: T): T {
  if (value !== null && typeof value === 'object') {
    for (const child of Object.values(value)) deepFreeze(child);
    Object.freeze(value);
  }
  return value;
}

export const COORDINATION_STATE_CONTRACT = deepFreeze({
  "schema_version": "loopx_coordination_state_contract_v0",
  "todo_read_record": {
    "schema_version": "loopx_todo_canonical_read_record_v0",
    "item_schema_version": "todo_item_v0",
    "fields": [
      "index",
      "done",
      "text",
      "schema_version",
      "todo_id",
      "role",
      "status",
      "priority",
      "title",
      "archive_state",
      "source_section",
      "task_class",
      "action_kind",
      "task_domain",
      "capability_binding_ref",
      "task_repository",
      "continuation_policy",
      "removed_continuation_policy",
      "required_write_scopes",
      "required_capabilities",
      "target_capabilities",
      "explore_result_node_refs",
      "decision_scope",
      "required_decision_scopes",
      "decision_outcome",
      "decision_scope_outcomes",
      "claimed_by",
      "created_by",
      "last_actor_agent_id",
      "bound_agent",
      "goal_bound",
      "blocks_agent",
      "excluded_agents",
      "global_gate",
      "unblocks_todo_id",
      "resume_when",
      "resume_monitor_generation",
      "resume_condition",
      "resume_ready",
      "no_followup",
      "successor_todo_ids",
      "completion_continuation",
      "completion_recovery",
      "replan_obligation_id",
      "target_key",
      "cadence",
      "next_due_at",
      "expires_at",
      "watch_only",
      "last_checked_at",
      "result_hash",
      "consecutive_no_change",
      "material_change",
      "material_change_generation",
      "max_no_change_before_replan",
      "monitor_effect_id",
      "note",
      "evidence",
      "reason",
      "completed_at",
      "completion_turn_key",
      "updated_at",
      "superseded_by",
      "completion_validation_required",
      "handoff_note"
    ],
    "required_fields": [
      "schema_version",
      "todo_id",
      "role",
      "status",
      "done",
      "text",
      "archive_state",
      "source_section"
    ]
  },
  "todo_domain_record": {
    "schema_version": "loopx_todo_domain_read_record_v0",
    "item_schema_version": "todo_domain_record_v0",
    "fields_from": "todo_read_record",
    "exclude_fields_from": "todo_projection_metadata",
    "required_fields": [
      "schema_version",
      "todo_id",
      "role",
      "status",
      "done",
      "text",
      "archive_state"
    ]
  },
  "todo_projection_metadata": {
    "fields": [
      "source_section",
      "index"
    ],
    "required_fields": [
      "source_section"
    ]
  },
  "local_authority_protocol": {
    "mutation_request_schema": "loopx_local_coordination_mutation_request_v0",
    "mutation_result_schema": "loopx_local_coordination_mutation_result_v0",
    "todo_read_request_schema": "loopx_local_coordination_todo_read_request_v0",
    "todo_read_result_schema": "loopx_local_coordination_todo_read_result_v0",
    "todo_list_request_schema": "loopx_local_coordination_todo_list_request_v0",
    "todo_list_result_schema": "loopx_local_coordination_todo_list_result_v0",
    "promotion_request_schema": "loopx_local_coordination_promotion_request_v0",
    "promotion_result_schema": "loopx_local_coordination_promotion_result_v0",
    "promotion_receipt_schema": "loopx_local_coordination_promotion_receipt_v0"
  },
  "runtime_shadow_protocol": {
    "commit_request_schema": "loopx_coordination_runtime_shadow_commit_v0",
    "commit_result_schema": "loopx_coordination_runtime_shadow_result_v0",
    "receipt_schema": "loopx_coordination_runtime_shadow_receipt_v0",
    "inspect_request_schema": "loopx_coordination_runtime_shadow_inspect_v0",
    "inspect_result_schema": "loopx_coordination_runtime_shadow_inspection_v0",
    "bootstrap_request_schema": "loopx_coordination_runtime_shadow_bootstrap_v0",
    "bootstrap_result_schema": "loopx_coordination_runtime_shadow_bootstrap_result_v0",
    "rollback_request_schema": "loopx_coordination_runtime_shadow_rollback_v0",
    "rollback_result_schema": "loopx_coordination_runtime_shadow_rollback_result_v0",
    "qualify_request_schema": "loopx_coordination_runtime_shadow_qualify_v0",
    "qualify_result_schema": "loopx_coordination_runtime_shadow_qualification_v0",
    "todo_read_request_schema": "loopx_coordination_runtime_shadow_todo_read_v0",
    "todo_read_result_schema": "loopx_coordination_runtime_shadow_todo_read_result_v0"
  },
  "compatibility": {
    "unknown_field_policy": "reject",
    "field_removal_policy": "maintainer_approval_required",
    "markdown_role": "human_workbench_and_compatibility_projection"
  }
} as const);
export const LOCAL_COORDINATION_MUTATION_REQUEST_SCHEMA = COORDINATION_STATE_CONTRACT.local_authority_protocol.mutation_request_schema;
export const LOCAL_COORDINATION_MUTATION_RESULT_SCHEMA = COORDINATION_STATE_CONTRACT.local_authority_protocol.mutation_result_schema;
export const LOCAL_COORDINATION_TODO_READ_REQUEST_SCHEMA = COORDINATION_STATE_CONTRACT.local_authority_protocol.todo_read_request_schema;
export const LOCAL_COORDINATION_TODO_READ_RESULT_SCHEMA = COORDINATION_STATE_CONTRACT.local_authority_protocol.todo_read_result_schema;
export const LOCAL_COORDINATION_TODO_LIST_REQUEST_SCHEMA = COORDINATION_STATE_CONTRACT.local_authority_protocol.todo_list_request_schema;
export const LOCAL_COORDINATION_TODO_LIST_RESULT_SCHEMA = COORDINATION_STATE_CONTRACT.local_authority_protocol.todo_list_result_schema;
export const LOCAL_COORDINATION_PROMOTION_REQUEST_SCHEMA = COORDINATION_STATE_CONTRACT.local_authority_protocol.promotion_request_schema;
export const LOCAL_COORDINATION_PROMOTION_RESULT_SCHEMA = COORDINATION_STATE_CONTRACT.local_authority_protocol.promotion_result_schema;
export const LOCAL_COORDINATION_PROMOTION_RECEIPT_SCHEMA = COORDINATION_STATE_CONTRACT.local_authority_protocol.promotion_receipt_schema;

export const COORDINATION_RUNTIME_SHADOW_COMMIT_REQUEST_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.commit_request_schema;
export const COORDINATION_RUNTIME_SHADOW_COMMIT_RESULT_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.commit_result_schema;
export const COORDINATION_RUNTIME_SHADOW_RECEIPT_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.receipt_schema;
export const COORDINATION_RUNTIME_SHADOW_INSPECT_REQUEST_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.inspect_request_schema;
export const COORDINATION_RUNTIME_SHADOW_INSPECT_RESULT_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.inspect_result_schema;
export const COORDINATION_RUNTIME_SHADOW_BOOTSTRAP_REQUEST_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.bootstrap_request_schema;
export const COORDINATION_RUNTIME_SHADOW_BOOTSTRAP_RESULT_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.bootstrap_result_schema;
export const COORDINATION_RUNTIME_SHADOW_ROLLBACK_REQUEST_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.rollback_request_schema;
export const COORDINATION_RUNTIME_SHADOW_ROLLBACK_RESULT_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.rollback_result_schema;
export const COORDINATION_RUNTIME_SHADOW_QUALIFY_REQUEST_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.qualify_request_schema;
export const COORDINATION_RUNTIME_SHADOW_QUALIFY_RESULT_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.qualify_result_schema;
export const COORDINATION_RUNTIME_SHADOW_TODO_READ_REQUEST_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.todo_read_request_schema;
export const COORDINATION_RUNTIME_SHADOW_TODO_READ_RESULT_SCHEMA = COORDINATION_STATE_CONTRACT.runtime_shadow_protocol.todo_read_result_schema;
