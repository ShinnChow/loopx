import assert from "node:assert/strict";
import test from "node:test";
import { decodeRefreshRetry, refreshRecovery, type RefreshRetryRequest } from "../../loopx/control_plane/quota/refresh_recovery.ts";

const request: RefreshRetryRequest = {
  vision: null, unchanged_reason: null, merge_patch: false,
  workspace_requested: false, mutation: {}, delivery_outcome: "outcome_progress",
  delivery_batch_scale: "implementation", delivery_boundary: null, progress_observation: null,
};
const prior = {
  generated_at: "2026-01-01T00:00:00Z", classification: "validated_change",
  delivery_outcome: "outcome_progress", delivery_batch_scale: "implementation",
  vision_checkpoint: { decision: "missing_required", satisfied: false, delivery_boundary: "semantic_closeout" },
};

test("legacy missing checkpoint can be supplemented but not rewritten", () => {
  const supplement = { ...request, unchanged_reason: "Original evidence still applies." };
  const accepted = refreshRecovery(supplement, prior, true, "unknown", false);
  assert.equal(accepted.decision, "supplement_checkpoint");
  const complete = { ...prior, refresh_recovery: accepted,
    vision_checkpoint: { ...prior.vision_checkpoint, decision: "unchanged_with_reason", satisfied: true } };
  assert.equal(refreshRecovery(supplement, complete, true, "unknown", false).decision, "replay");
  assert.equal(refreshRecovery({ ...supplement, unchanged_reason: "Different decision." }, complete, true, "unknown", false).decision, "reject");
  assert.equal(refreshRecovery(request, complete, true, "unknown", false).decision, "replay");
  assert.equal(refreshRecovery(supplement, prior, true, "unknown", true).reason, "checkpoint_superseded_by_later_vision");
});

test("receipt repair is separate from append and malformed inputs fail closed", () => {
  assert.equal(refreshRecovery(request, null, false, undefined, false).decision, "append");
  assert.equal(refreshRecovery(request, prior, false, undefined, false).decision, "repair_receipt");
  assert.equal(refreshRecovery({ ...request, delivery_outcome: "outcome_gap" }, prior, true, undefined, false).decision, "reject");
  assert.equal(refreshRecovery({ ...request, mutation: { next_action: "Replace plan" } }, prior, true, undefined, false).decision, "reject");
  for (const field of ["workspace_requested", "merge_patch", "vision", "mutation", "delivery_outcome", "progress_observation"]) {
    assert.throws(() => decodeRefreshRetry({ ...request, [field]: 1 }));
  }
});

test("digest uses JSON structure, not property insertion order", () => {
  const first = refreshRecovery({ ...request, vision: { state: "open", vision_patch: { a: 1, b: 2 } } }, null, false, undefined, false);
  const second = refreshRecovery({ ...request, vision: { vision_patch: { b: 2, a: 1 }, state: "open" } }, null, false, undefined, false);
  assert.equal(first.vision_request_digest, second.vision_request_digest);
});

test("workspace supplements preserve the monitor compatibility boundary", () => {
  const monitor = { ...prior, classification: "quota_monitor_poll", delivery_batch_scale: null };
  assert.equal(refreshRecovery({ ...request, workspace_requested: true }, monitor, true, "required", false).decision, "supplement_workspace");
  assert.equal(refreshRecovery({ ...request, workspace_requested: true, unchanged_reason: "Still applicable" }, monitor, true, "required", false).reason, "repair_workspace_before_checkpoint");
  assert.equal(refreshRecovery({ ...request, workspace_requested: true }, prior, true, "not_required", false).decision, "replay");
});
