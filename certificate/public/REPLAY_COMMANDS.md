# Replay commands

From the repository root, run:

```bash
python scripts/verify_certificate.py --root . --log-level INFO
```

A successful run prints a JSON summary containing:

```json
{
  "status": "passed",
  "certificate_verified": true,
  "threshold_proved": true,
  "certified_threshold": "0.833",
  "failed_component_count": 0
}
```

For the certificate-chain component replay, run:

```bash
python scripts/replay_certificate_chain.py --root . --log-level INFO
```

For the repository-level release check, run:

```bash
python scripts/check_repository.py --root . --log-level INFO
```
