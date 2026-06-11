# FAQ

## Does the repository contain all certificate data?

Yes. The required archives are bundled in `certificate/final_chain/`.

## What is the difference between certificate verification and repository check?

`verify_certificate.py` checks the certificate-chain archives. `check_repository.py` checks the public release package and also runs the main certificate verification internally.

## What is full certificate-chain replay?

`replay_certificate_chain.py` replays the four certificate-chain components without README, layout, or release-wording checks.

## What do the component replay commands do?

They isolate one component: per-record evidence, construction audit, witness construction, or final adjudication. They are useful for debugging but do not replace the main certificate verification.

## Why is the witness-domain area bound larger than 0.83201?

That value is local to the witness domains. The global certified threshold is obtained after combining all local records over the finite cover.

## Does this solve the nonconvex problem?

No. The scope is the convex Brass-Sharifi three-test-set certificate setting.

## Is a proof-assistant formalization included?

No. The repository contains a finite certificate and Python replay checks.
