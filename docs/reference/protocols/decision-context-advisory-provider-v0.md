# Decision Context advisory provider v0

`decision_context_advisory_provider_v0` lets an optional LoopX extension
implement the existing Decision Context `ContextProvider` port. It is a
retrieval contract, not a new capability, state authority, or transcript store.

## Ownership

- `decision-context` owns activation, request bounds, evidence rebase, fail-open
  behavior, public projection, and durable-transition policy.
- The extension lifecycle owns install, enable, disable, upgrade, doctor
  readiness, and revision-bound process dispatch.
- A provider owns only a bounded external read and response normalization.
- The Goal/Todo/material/amendment owners remain the only paths for durable
  promotion of a recalled claim.

An implementation declares:

```toml
permissions = ["decision_context.read"]

[runtime]
protocol = "decision_context_advisory_provider_v0"
required_permissions = ["decision_context.read"]

[[implements]]
capability_id = "decision-context"
protocol = "decision_context_advisory_provider_v0"
```

Decision Context may select an exact `config.extension_id`. Without one,
resolution succeeds only when exactly one enabled, doctor-ready extension
implements the protocol. Missing, disabled, stale, ambiguous, failed, and
contract-invalid providers degrade to an unavailable recall receipt; authority
source collection continues.

## Retrieve request

The runtime receives a `decision_context_advisory_retrieve_request_v0` object:

| Field | Contract |
| --- | --- |
| `schema_version` | Exact request schema token. |
| `operation` | Exactly `retrieve`. |
| `namespace` | Bounded caller namespace. |
| `scope_ref` | Provider-neutral scope chosen by the profile. |
| `query` | Bounded private retrieval query. |
| `query_summary` | Public-safe description; the raw query is not projected. |
| `max_results` | Positive integer, capped by Core at 8. |
| `timeout_seconds` | Whole-second execution timeout of at least 1, further capped by the extension binding. Unsupported sub-second values fail open at the capability boundary. |
| `observed_at` | Caller observation time. |

The provider must not interpret a scope as a Goal identity or authority grant.
Host-specific syntax is normalized before the provider boundary. For example,
LoopX parses `codex://threads/<thread-id>` and emits
`host-session:codex:<thread-id>`; the provider never parses the deep link.

## Retrieve response

The runtime returns a `decision_context_advisory_retrieve_response_v0` object:

```json
{
  "schema_version": "decision_context_advisory_retrieve_response_v0",
  "ok": true,
  "status": "completed",
  "reason_code": null,
  "items": [
    {
      "resource_ref": "provider-private-reference",
      "summary": "Public-safe generic summary",
      "content": "transient exact content",
      "score": 0.5
    }
  ]
}
```

Core rejects missing or unknown fields, invalid bounds, a non-numeric score,
items on an unavailable response, and a status/reason mismatch. The process
deadline is the shorter of the profile request and extension lifecycle limits.
`content` and `resource_ref` remain in-process. The public
`context_provider_retrieval_v0` packet keeps the summary and score, hashes the
resource reference, and omits content. Provider errors are reported with
compact reason codes; subprocess output and private paths are not copied into
public state.

The protocol defines no sync or write operation. A provider used through the
`ContextProvider` interface returns `read_only_provider` for `sync`. It grants
no permission, workspace access, claim, lease, lifecycle authority, execution
authority, amendment authority, or write scope.

## Obelisk implementation

The optional `packages/loopx-obelisk` distribution implements this protocol for
historical Codex tasks. It uses Obelisk's public `--version` and read-only
`--query` CLI boundary, filters to the exact normalized Codex session, excludes
`session.is_invoking`, and accepts only visible user or assistant text rows. It
does not import Obelisk code, read its SQLite schema, invoke `--build` or
`--attune`, or control a live Codex task.
