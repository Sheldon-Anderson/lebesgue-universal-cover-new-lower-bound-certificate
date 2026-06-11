# Certificate final note

This release contains a finite certificate for the threshold $\tau=0.83201$ in the convex Brass-Sharifi three-test-set framework.

The main public command is:

```bash
python scripts/verify_certificate.py --root . --log-level INFO
```

The certificate data are stored in `certificate/final_chain/`, and the replay code is stored in `ucbs/certificate/`.
