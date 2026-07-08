# Expected outputs

A successful certificate verification prints a compact JSON summary similar to:

```json
{
  "status": "passed",
  "certificate_verified": true,
  "threshold_proved": true,
  "certified_threshold": "0.833",
  "artifact_hashes_verified": true,
  "failed_component_count": 0
}
```

A successful repository check prints:

```json
{
  "status": "passed",
  "failed_step_count": 0
}
```

The repository check writes detailed CSV diagnostics under `runs/repository_check/diagnostics/`, including rows for release/version consistency, generated build artifacts, final-newline checks, archive/public mirror consistency, paper claim-boundary checks, artifact hashes, and the main certificate verification.
