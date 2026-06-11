# Expected outputs

All public commands write detailed logs under `runs/`. Diagnostic CSV files always contain a header and a summary row, including the no-issue case.

## Main certificate verification

Command:

```bash
python scripts/verify_certificate.py --root . --log-level INFO
```

Primary outputs:

```text
runs/certificate_verification/status/certificate_verification.status.json
runs/certificate_verification/diagnostics/component_checks.csv
runs/certificate_verification/diagnostics/failed_component_checks.csv
runs/certificate_verification/log/certificate_verification.log
runs/certificate_verification/certificate_verification_feedback.zip
```

Expected status fields:

```json
{
  "status": "passed",
  "certificate_verified": true,
  "threshold_proved": true,
  "certified_threshold": "0.83201",
  "failed_component_count": 0
}
```

## Repository check

Command:

```bash
python scripts/check_repository.py --root . --log-level INFO
```

Primary outputs:

```text
runs/repository_check/status/repository_check.status.json
runs/repository_check/diagnostics/failed_checks.csv
runs/repository_check/diagnostics/readme_math.csv
runs/repository_check/diagnostics/narrative_lint.csv
runs/repository_check/diagnostics/claim_boundary.csv
runs/repository_check/diagnostics/artifact_hashes.csv
runs/repository_check/log/repository_check.log
runs/repository_check/repository_check_feedback.zip
```

Expected status fields:

```json
{
  "status": "passed",
  "failed_step_count": 0
}
```

## Full certificate-chain replay

Command:

```bash
python scripts/replay_certificate_chain.py --root . --log-level INFO
```

Primary outputs:

```text
runs/certificate_chain_replay/status/certificate_chain_replay.status.json
runs/certificate_chain_replay/diagnostics/component_checks.csv
runs/certificate_chain_replay/log/certificate_chain_replay.log
runs/certificate_chain_replay/certificate_chain_replay_feedback.zip
```

Expected fields:

```json
{
  "status": "passed",
  "per_record_evidence_passed": true,
  "construction_audit_passed": true,
  "witness_construction_passed": true,
  "final_adjudication_passed": true,
  "failed_component_count": 0
}
```

## Component replay outputs

Each component command writes `status`, `diagnostics`, `log`, and a feedback zip under its own run directory:

```text
runs/per_record_evidence_replay/
runs/construction_audit_replay/
runs/witness_construction_replay/
runs/final_adjudication_replay/
```
