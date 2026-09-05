"""Generated from coordination_state_contract_v0.json; do not edit."""

from __future__ import annotations

from types import MappingProxyType
from typing import Any, Final

def _freeze(value: Any) -> Any:
    if isinstance(value, dict):
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    return value

COORDINATION_STATE_CONTRACT: Final = _freeze({'schema_version': 'loopx_coordination_state_contract_v0',
 'todo_read_record': {'schema_version': 'loopx_todo_canonical_read_record_v0',
                      'item_schema_version': 'todo_item_v0',
                      'fields': ['index',
                                 'done',
                                 'text',
                                 'schema_version',
                                 'todo_id',
                                 'role',
                                 'status',
                                 'priority',
                                 'title',
                                 'archive_state',
                                 'source_section',
                                 'task_class',
                                 'action_kind',
                                 'task_domain',
                                 'capability_binding_ref',
                                 'task_repository',
                                 'continuation_policy',
                                 'removed_continuation_policy',
                                 'required_write_scopes',
                                 'required_capabilities',
                                 'target_capabilities',
                                 'explore_result_node_refs',
                                 'decision_scope',
                                 'required_decision_scopes',
                                 'decision_outcome',
                                 'decision_scope_outcomes',
                                 'claimed_by',
                                 'created_by',
                                 'last_actor_agent_id',
                                 'bound_agent',
                                 'goal_bound',
                                 'blocks_agent',
                                 'excluded_agents',
                                 'global_gate',
                                 'unblocks_todo_id',
                                 'resume_when',
                                 'resume_monitor_generation',
                                 'resume_condition',
                                 'resume_ready',
                                 'no_followup',
                                 'successor_todo_ids',
                                 'completion_continuation',
                                 'completion_recovery',
                                 'replan_obligation_id',
                                 'target_key',
                                 'cadence',
                                 'next_due_at',
                                 'expires_at',
                                 'watch_only',
                                 'last_checked_at',
                                 'result_hash',
                                 'consecutive_no_change',
                                 'material_change',
                                 'material_change_generation',
                                 'max_no_change_before_replan',
                                 'monitor_effect_id',
                                 'note',
                                 'evidence',
                                 'reason',
                                 'completed_at',
                                 'completion_turn_key',
                                 'updated_at',
                                 'superseded_by',
                                 'completion_validation_required',
                                 'handoff_note'],
                      'required_fields': ['schema_version',
                                          'todo_id',
                                          'role',
                                          'status',
                                          'done',
                                          'text',
                                          'archive_state',
                                          'source_section']},
 'todo_domain_record': {'schema_version': 'loopx_todo_domain_read_record_v0',
                        'item_schema_version': 'todo_domain_record_v0',
                        'fields_from': 'todo_read_record',
                        'exclude_fields_from': 'todo_projection_metadata',
                        'required_fields': ['schema_version',
                                            'todo_id',
                                            'role',
                                            'status',
                                            'done',
                                            'text',
                                            'archive_state']},
 'todo_projection_metadata': {'fields': ['source_section', 'index'],
                              'required_fields': ['source_section']},
 'local_authority_protocol': {'mutation_request_schema': 'loopx_local_coordination_mutation_request_v0',
                              'mutation_result_schema': 'loopx_local_coordination_mutation_result_v0',
                              'todo_read_request_schema': 'loopx_local_coordination_todo_read_request_v0',
                              'todo_read_result_schema': 'loopx_local_coordination_todo_read_result_v0',
                              'todo_list_request_schema': 'loopx_local_coordination_todo_list_request_v0',
                              'todo_list_result_schema': 'loopx_local_coordination_todo_list_result_v0',
                              'promotion_request_schema': 'loopx_local_coordination_promotion_request_v0',
                              'promotion_result_schema': 'loopx_local_coordination_promotion_result_v0',
                              'promotion_receipt_schema': 'loopx_local_coordination_promotion_receipt_v0'},
 'runtime_shadow_protocol': {'commit_request_schema': 'loopx_coordination_runtime_shadow_commit_v0',
                             'commit_result_schema': 'loopx_coordination_runtime_shadow_result_v0',
                             'receipt_schema': 'loopx_coordination_runtime_shadow_receipt_v0',
                             'inspect_request_schema': 'loopx_coordination_runtime_shadow_inspect_v0',
                             'inspect_result_schema': 'loopx_coordination_runtime_shadow_inspection_v0',
                             'bootstrap_request_schema': 'loopx_coordination_runtime_shadow_bootstrap_v0',
                             'bootstrap_result_schema': 'loopx_coordination_runtime_shadow_bootstrap_result_v0',
                             'rollback_request_schema': 'loopx_coordination_runtime_shadow_rollback_v0',
                             'rollback_result_schema': 'loopx_coordination_runtime_shadow_rollback_result_v0',
                             'qualify_request_schema': 'loopx_coordination_runtime_shadow_qualify_v0',
                             'qualify_result_schema': 'loopx_coordination_runtime_shadow_qualification_v0',
                             'todo_read_request_schema': 'loopx_coordination_runtime_shadow_todo_read_v0',
                             'todo_read_result_schema': 'loopx_coordination_runtime_shadow_todo_read_result_v0'},
 'local_authority_shadow_protocol': {'binding_schema': 'loopx_coordination_runtime_shadow_binding_v0',
                                     'config_schema': 'loopx_local_authority_shadow_config_v0',
                                     'request_schema': 'loopx_local_authority_shadow_request_v0',
                                     'projection_schema': 'loopx_local_authority_shadow_projection_v0',
                                     'evidence_schema': 'loopx_local_authority_shadow_evidence_v0',
                                     'observation_receipt_schema': 'loopx_local_authority_shadow_observation_receipt_v0',
                                     'outbox_entry_schema': 'loopx_local_authority_shadow_outbox_entry_v0',
                                     'outbox_commit_schema': 'loopx_local_authority_shadow_outbox_commit_v0',
                                     'drain_cursor_schema': 'loopx_local_authority_shadow_drain_cursor_v0',
                                     'transaction_projection_schema': 'loopx_coordination_runtime_shadow_projection_v0',
                                     'commit_entry_request_schema': 'loopx_coordination_runtime_shadow_commit_entry_request_v0',
                                     'commit_entry_result_schema': 'loopx_coordination_runtime_shadow_commit_entry_result_v0',
                                     'read_request_schema': 'loopx_coordination_runtime_shadow_outbox_read_v0',
                                     'read_result_schema': 'loopx_coordination_runtime_shadow_outbox_read_result_v0',
                                     'event_schema': 'loopx_coordination_runtime_shadow_outbox_event_v0',
                                     'transaction_receipt_schema': 'loopx_coordination_runtime_shadow_outbox_receipt_v0',
                                     'transaction_evidence_schema': 'loopx_local_authority_shadow_evidence_v1'},
 'compatibility': {'unknown_field_policy': 'reject',
                   'field_removal_policy': 'maintainer_approval_required',
                   'markdown_role': 'human_workbench_and_compatibility_projection'}})
LOCAL_COORDINATION_MUTATION_REQUEST_SCHEMA: Final[str] = 'loopx_local_coordination_mutation_request_v0'
LOCAL_COORDINATION_MUTATION_RESULT_SCHEMA: Final[str] = 'loopx_local_coordination_mutation_result_v0'
LOCAL_COORDINATION_TODO_READ_REQUEST_SCHEMA: Final[str] = 'loopx_local_coordination_todo_read_request_v0'
LOCAL_COORDINATION_TODO_READ_RESULT_SCHEMA: Final[str] = 'loopx_local_coordination_todo_read_result_v0'
LOCAL_COORDINATION_TODO_LIST_REQUEST_SCHEMA: Final[str] = 'loopx_local_coordination_todo_list_request_v0'
LOCAL_COORDINATION_TODO_LIST_RESULT_SCHEMA: Final[str] = 'loopx_local_coordination_todo_list_result_v0'
LOCAL_COORDINATION_PROMOTION_REQUEST_SCHEMA: Final[str] = 'loopx_local_coordination_promotion_request_v0'
LOCAL_COORDINATION_PROMOTION_RESULT_SCHEMA: Final[str] = 'loopx_local_coordination_promotion_result_v0'
LOCAL_COORDINATION_PROMOTION_RECEIPT_SCHEMA: Final[str] = 'loopx_local_coordination_promotion_receipt_v0'

COORDINATION_RUNTIME_SHADOW_COMMIT_REQUEST_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_commit_v0'
COORDINATION_RUNTIME_SHADOW_COMMIT_RESULT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_result_v0'
COORDINATION_RUNTIME_SHADOW_RECEIPT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_receipt_v0'
COORDINATION_RUNTIME_SHADOW_INSPECT_REQUEST_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_inspect_v0'
COORDINATION_RUNTIME_SHADOW_INSPECT_RESULT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_inspection_v0'
COORDINATION_RUNTIME_SHADOW_BOOTSTRAP_REQUEST_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_bootstrap_v0'
COORDINATION_RUNTIME_SHADOW_BOOTSTRAP_RESULT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_bootstrap_result_v0'
COORDINATION_RUNTIME_SHADOW_ROLLBACK_REQUEST_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_rollback_v0'
COORDINATION_RUNTIME_SHADOW_ROLLBACK_RESULT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_rollback_result_v0'
COORDINATION_RUNTIME_SHADOW_QUALIFY_REQUEST_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_qualify_v0'
COORDINATION_RUNTIME_SHADOW_QUALIFY_RESULT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_qualification_v0'
COORDINATION_RUNTIME_SHADOW_TODO_READ_REQUEST_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_todo_read_v0'
COORDINATION_RUNTIME_SHADOW_TODO_READ_RESULT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_todo_read_result_v0'

LOCAL_AUTHORITY_SHADOW_BINDING_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_binding_v0'
LOCAL_AUTHORITY_SHADOW_CONFIG_SCHEMA: Final[str] = 'loopx_local_authority_shadow_config_v0'
LOCAL_AUTHORITY_SHADOW_REQUEST_SCHEMA: Final[str] = 'loopx_local_authority_shadow_request_v0'
LOCAL_AUTHORITY_SHADOW_PROJECTION_SCHEMA: Final[str] = 'loopx_local_authority_shadow_projection_v0'
LOCAL_AUTHORITY_SHADOW_EVIDENCE_SCHEMA: Final[str] = 'loopx_local_authority_shadow_evidence_v0'
LOCAL_AUTHORITY_SHADOW_OBSERVATION_RECEIPT_SCHEMA: Final[str] = 'loopx_local_authority_shadow_observation_receipt_v0'
LOCAL_AUTHORITY_SHADOW_OUTBOX_ENTRY_SCHEMA: Final[str] = 'loopx_local_authority_shadow_outbox_entry_v0'
LOCAL_AUTHORITY_SHADOW_OUTBOX_COMMIT_SCHEMA: Final[str] = 'loopx_local_authority_shadow_outbox_commit_v0'
LOCAL_AUTHORITY_SHADOW_DRAIN_CURSOR_SCHEMA: Final[str] = 'loopx_local_authority_shadow_drain_cursor_v0'
LOCAL_AUTHORITY_SHADOW_TRANSACTION_PROJECTION_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_projection_v0'
LOCAL_AUTHORITY_SHADOW_COMMIT_ENTRY_REQUEST_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_commit_entry_request_v0'
LOCAL_AUTHORITY_SHADOW_COMMIT_ENTRY_RESULT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_commit_entry_result_v0'
LOCAL_AUTHORITY_SHADOW_READ_REQUEST_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_outbox_read_v0'
LOCAL_AUTHORITY_SHADOW_READ_RESULT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_outbox_read_result_v0'
LOCAL_AUTHORITY_SHADOW_EVENT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_outbox_event_v0'
LOCAL_AUTHORITY_SHADOW_TRANSACTION_RECEIPT_SCHEMA: Final[str] = 'loopx_coordination_runtime_shadow_outbox_receipt_v0'
LOCAL_AUTHORITY_SHADOW_TRANSACTION_EVIDENCE_SCHEMA: Final[str] = 'loopx_local_authority_shadow_evidence_v1'
