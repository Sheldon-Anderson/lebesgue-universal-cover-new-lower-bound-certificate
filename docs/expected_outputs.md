# Expected outputs

A successful certificate verification prints a compact JSON summary similar to:

```json
{
  "status": "passed",
  "certificate_verified": true,
  "threshold_proved": true,
  "certified_threshold": "0.833",
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
