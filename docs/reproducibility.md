# Reproducibility

Run commands from the repository root. The public verifier uses only the records bundled in `certificate/final_chain/` and `certificate/public/`; it does not rerun the original geometric search.

## Full repository release check

```bash
python scripts/check_repository.py --root . --log-level INFO
```

This command checks Python compilation, package metadata, public script entry points, repository layout, Markdown math fragments, public claim boundaries, certificate artifact hashes, and the main certificate verification.

## Main certificate verification

```bash
python scripts/verify_certificate.py --root . --log-level INFO
```

This command verifies the four theorem-critical certificate components and writes diagnostics under `runs/certificate_verification/`.

## Certificate-chain replay

```bash
python scripts/replay_certificate_chain.py --root . --log-level INFO
```

This command verifies the certificate-chain components without the README, documentation, repository-layout, and release-quality checks.

## Component-level replay commands

```bash
python scripts/replay_per_record_evidence.py --root . --log-level INFO
python scripts/replay_construction_audit.py --root . --log-level INFO
python scripts/replay_witness_construction.py --root . --log-level INFO
python scripts/replay_final_adjudication.py --root . --log-level INFO
```

These commands are useful for locating a failure within one certificate component. A successful run writes a compact JSON summary and a feedback ZIP under `runs/`.
