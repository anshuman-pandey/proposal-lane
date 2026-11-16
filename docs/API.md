# Local API development preview

Install Python 3.12 dependencies and run:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export PROPOSAL_OWNER_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
export PROPOSAL_DATABASE=proposal.sqlite3
python server.py
```

Listens on localhost port 8095. This is a development server, not production hosting; the English browser workspace is available at `/`. Keep the owner key private. All requests use `Authorization: Bearer <key>`, never query-string credentials. No cross-origin access is enabled.

| Route | Access | Behavior |
| --- | --- | --- |
| POST /api/estimate | Owner | Validate and calculate proposal body without saving |
| GET /api/proposals | Owner | List IDs and revisions |
| POST /api/proposals | Owner | Create proposal from body; returns ID and revision |
| GET /api/proposals/{id} | Owner | Read draft body and revision |
| PUT /api/proposals/{id} | Owner | JSON `{revision, body}`; reject stale revisions |
| GET /api/proposals/{id}/shares | Owner | List share IDs, revisions and revocation state; no keys |
| POST /api/proposals/{id}/shares | Owner | JSON `{revision}`; create immutable snapshot; key returned once |
| POST /api/proposals/{id}/shares/{share}/revoke | Owner | Revoke future access |
| GET /api/shared/{share} | Share key | Read that snapshot only |

Proposal input: title, client, scope, currency, items (description, quantity and unit_price), discount and tax_percent. Numeric inputs must be decimal strings. Calculated totals supplied by clients are ignored and recalculated. See README for rounding and supported currencies.

JSON requests are limited to 256 KiB. Invalid/stale input returns 400, denied credentials 401, wrong content type 415, oversized input 413, unavailable storage 503. All responses prohibit caching and framing. Shared snapshots stay unchanged after draft edits; create a new share to send revised terms. Revocation cannot erase prior copies. No signing, acceptance or payment is implemented.

Verified using Flask's HTTP test client. Chromium owner/client workflow and a one-page print PDF pass. Six languages, other browser print engines and production persistence/recovery remain pending.
