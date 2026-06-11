# Release notes

This release uses clean public names for the certificate-chain archives and verification commands.

Public commands:

```bash
python scripts/verify_certificate.py --root . --log-level INFO
python scripts/check_repository.py --root . --log-level INFO
python scripts/replay_certificate_chain.py --root . --log-level INFO
```

The four certificate-chain archives are named by their public role: per-record evidence, construction audit, witness construction, and final adjudication.
