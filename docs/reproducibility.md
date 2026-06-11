# Reproducibility guide

## Standard run

```bash
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
python scripts/verify_certificate.py --root . --log-level INFO
python scripts/check_repository.py --root . --log-level INFO
```

## Windows PowerShell

```powershell
python -m pip install -r requirements.txt
python -m pip install -e . --no-deps
python scripts\verify_certificate.py --root . --log-level INFO
python scripts\check_repository.py --root . --log-level INFO
```

## Explicit certificate archives

```bash
python scripts/verify_certificate.py \
  --root . \
  --per-record-evidence-zip certificate/final_chain/per_record_evidence_feedback.zip \
  --construction-audit-zip certificate/final_chain/construction_audit_feedback.zip \
  --witness-construction-zip certificate/final_chain/witness_construction_feedback.zip \
  --final-adjudication-zip certificate/final_chain/final_adjudication_feedback.zip \
  --log-level INFO
```

## Useful options

- `--root`: repository root.
- `--run-id`: output directory name under `runs/`.
- `--log-level`: one of `DEBUG`, `INFO`, `WARNING`, or `ERROR`.
- `--artifact-root`: directory containing the four certificate-chain archives.
