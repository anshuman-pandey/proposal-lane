# Proposal Lane

### Turn scope into a proposal clients can keep.

Write a proposal, price the work, and share an immutable client snapshot. A focused, self-hosted alternative to Better Proposals for estimates and printable proposals.

[![CI](https://github.com/anshuman-pandey/proposal-lane/actions/workflows/check.yml/badge.svg)](https://github.com/anshuman-pandey/proposal-lane/actions/workflows/check.yml) · [MIT license](LICENSE) · Python + SQLite · Self-hosted

![Proposal Lane: actual application workspace](docs/assets/workspace.png)

**Public source preview.** The local workflow and container recovery have been tested. There is no hosted demo or tagged product release yet; public HTTPS acceptance remains pending.

## How it works

1. Enter the scope and line items, including fractional quantities, a fixed discount and tax.
2. Save the draft and create a private client snapshot. Later draft edits leave shared snapshots unchanged.
3. Use browser Print / Save PDF for a portable copy, or revoke future access to a snapshot.

## Try it locally

Requires Git, Python 3 and Docker with the Compose plugin.

```sh
git clone https://github.com/anshuman-pandey/proposal-lane.git
cd proposal-lane
python3 scripts/setup.py
docker compose up --build -d
```

Open **http://127.0.0.1:8095**. Read the generated private `.env` file locally and use its `PROPOSAL_OWNER_KEY` value to unlock the owner workspace. Setup retains any existing `.env`; do not commit or share this file.

The app binds to localhost and stores data in a persistent Docker volume. Links pointing to localhost work only on your computer. For remote sharing, follow the [HTTPS deployment and backup guide](docs/DEPLOYMENT.md). Avoid `docker compose down -v` unless you intend to delete the stored data.

## Included

- Exact-cent calculations: round each line half-up, subtract the fixed discount, then round tax half-up.
- USD, EUR, GBP, CAD and AUD with two decimal places; no currency conversion.
- Revision checks protect drafts against overwriting a newer edit.

**Interface languages:** English, German, Spanish, Japanese, Simplified Chinese and Traditional Chinese. Native-speaker review is still pending. User-authored content is never translated.

## Know the boundaries

Up to 100 line items; quantities and unit prices are each limited to one million, with a one-billion subtotal limit. Printing uses the browser, not a server-side PDF generator. Chromium print output is tested; other print engines remain unverified. No electronic signatures, payments, identity verification or tax-compliance service. Revoking a link cannot recall a saved PDF.

Private links and reviewer keys grant access to whoever holds them. Keep the owner key separate from participant credentials. This project covers the workflow above, not the full feature set of its commercial reference.

## Development and checks

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

The published baseline passed **21 Python tests**. Recorded browser acceptance covers: proposal editing, exact totals, immutable snapshots, revocation and one-page/28-page chromium pdf output. Container restart and clean-volume backup/restore were also checked. See the [validation record](artifacts/validation.json) for the exact evidence and remaining acceptance gates.

Bug reports should include reproduction steps and browser/runtime versions, with private keys and client data removed. Focused fixes and improvements are welcome through [issues](https://github.com/anshuman-pandey/proposal-lane/issues) and pull requests.

## Documentation

[Deployment & backups](docs/DEPLOYMENT.md) · [Print guide](docs/PRINT.md) · [Api guide](docs/API.md) · [Scope & comparison](docs/SCOPE.md) · [Validation evidence](artifacts/validation.json) · [License](LICENSE)
