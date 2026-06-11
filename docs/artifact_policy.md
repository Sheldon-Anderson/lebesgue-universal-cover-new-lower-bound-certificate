# Artifact and SHA256 policy

This repository separates certificate data from source and documentation files.

## Certificate data

The certificate-chain archives are stored in:

```text
certificate/final_chain/
```

The four archives are:

```text
per_record_evidence_feedback.zip
construction_audit_feedback.zip
witness_construction_feedback.zip
final_adjudication_feedback.zip
```

These archives are the data inputs used by the certificate replay code in `ucbs/certificate/`.

## Hash policy

The SHA256 gate covers the certificate-chain archives. The key manifest is:

```text
certificate/manifest/key_artifacts_sha256.txt
```

If any certificate-chain archive changes, the hash check in `scripts/check_repository.py` fails until the manifest is intentionally regenerated.

Documentation, paper files, and Python source files are checked by repository diagnostics and by release control. They are not part of the certificate-data hash gate.

## Verification code

The code that reads and checks the certificate data lives in:

```text
ucbs/certificate/
```

The public entry point is:

```bash
python scripts/verify_certificate.py --root . --log-level INFO
```
