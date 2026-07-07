# Final certificate verification report

## Scope boundary

This report summarizes the final verification gate for the frozen certificate records. It does not assert external independent verification, proof-assistant formalization, or a nonconvex theorem.

## Key status

- target: `0.833`
- event_aware_total: `493`
- event_aware_pass: `493`
- witness_source_total: `117`
- witness_source_pass: `117`
- p1_thin_total: `11`
- p1_thin_pass: `11`
- final_replay_only_rows: `2790`
- proof_grade_blocker_rows: `0`
- final_aggregation_passed: `True`
- claim_boundary_ok: `True`
- theorem_ready_candidate: `True`
- theorem_ready: `True`

## Frozen-record inventory

| component | requirement | route kind | route status | rows |
|---|---|---|---|---:|
| TENSOR | final_replay_only | p0_safe_inherited_support_area_record_freeze_candidate | frozen_inherited_candidate | 1419 |
| TENSOR | final_replay_only | p1_closure_interval_record_freeze_candidate | frozen_closure_candidate | 1272 |
| DIRECTED | directed_event_aware_interval_replay_required | directed_rho_event_aware_record_freeze_candidate | frozen_directed_event_aware_candidate_pending_interval_replay | 264 |
| H004 | common_source_event_aware_interval_replay_required | h004_common_source_event_aware_record_freeze_candidate | frozen_common_source_event_aware_candidate_pending_interval_replay | 205 |
| TENSOR | final_replay_only | p2_closure_interval_record_freeze_candidate | frozen_closure_candidate | 56 |
| DIRECTED | source_reconstruction_or_witness_adjudication_required | directed_source_reconstruction_or_witness_fallback_record_freeze_candidate | frozen_source_reconstruction_candidate_pending_adjudication | 51 |
| H004 | final_replay_only | h004_common_source_safe_inherited_record_freeze_candidate | frozen_common_source_inherited_candidate | 43 |
| H004 | clustered_inner_witness_record_adjudication_required | h004_clustered_inner_witness_record_seed_freeze_candidate | frozen_cluster_witness_seed_candidate_pending_adjudication | 34 |
| TENSOR | event_aware_interval_replay_required | p0_event_aware_support_area_record_freeze_candidate | frozen_event_aware_candidate_pending_interval_replay | 24 |
| DIRECTED | directed_witness_record_adjudication_required | directed_rho_cluster_witness_record_seed_freeze_candidate | frozen_directed_witness_seed_candidate_pending_adjudication | 22 |
| TENSOR | thin_guard_extra_replay_required | p1_extra_split_thin_guard_record_freeze_candidate | frozen_closure_candidate | 11 |
| DIRECTED | source witness replay required | directed_existing_inner_witness_record_freeze_candidate | frozen_existing_witness_candidate | 8 |
| TENSOR | inner_witness_record_adjudication_required | p0_symmetric_inner_witness_record_seed_freeze_candidate | frozen_witness_seed_candidate_pending_adjudication | 2 |

## Final blockers

No final verification blockers were produced.
