# Proposal Lane · development core

**An open-source alternative for Better Proposals workflows, in preparation.**

Local Python library only. The browser editor, authenticated sharing service and printable PDF workflow are not implemented yet. This is not a usable product release.

```mermaid
flowchart LR
  A[Proposal line items] --> B[Exact decimal estimate]
  B --> C[Immutable shared snapshot]
  C --> D[Revoke access when needed]
  B --> E[Edit a new revision]
```

Implemented: line items with fractional quantities, explicit currency, fixed discount, tax percentage, exact cents, optimistic revision checks, immutable shared snapshots and revocable hashed share credentials. Run `python3 -m unittest discover -s tests -v` with Python 3.12; no third-party dependencies are needed for this core.

Amounts accept plain decimal strings. Each line is rounded half-up to cents; the fixed discount is subtracted from the rounded subtotal; tax is rounded half-up on the discounted subtotal. Only USD, EUR, GBP, CAD and AUD are supported initially, all at two decimal places. Currency conversion and jurisdiction-specific tax compliance are not provided. Limits: 100 line items, quantity up to 1 million, unit price up to 1 million, subtotal up to 1 billion currency units. Zero-price items are allowed; zero quantity is not.

Owner methods still require an authenticated service boundary. Share keys confer read access; they do not establish identity, consent, signature or payment. Revocation cannot erase copies already downloaded. No external network service is started by this code.

Next: authenticated API, polished editor/client preview, safe print/PDF output, six interface languages, real browser acceptance and persistent deployment recovery.

[Scope and primary references](docs/SCOPE.md) · [MIT license](LICENSE)
