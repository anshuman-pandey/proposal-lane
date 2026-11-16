# Proposal Lane local preview

Open-source alternative for Better Proposals workflows: proposals, line-item estimates, immutable client snapshots, revocable sharing and browser Print / Save PDF. Independent MIT-licensed source; no public repository, release or hosted demo claimed.

## Run

```sh
python3 scripts/setup.py
docker compose up --build -d
```

Read the private `.env` locally for the owner key. Open http://127.0.0.1:8095, unlock, enter scope and line items, and save. Create a client snapshot and save its private link. Edits to the draft do not change existing snapshots. Print a saved version or client view with browser Print / Save PDF; disable browser headers/footers. Localhost links work only on the same computer; remote use needs authorized HTTPS hosting.

English, German, Spanish, Japanese, Simplified Chinese and Traditional Chinese are included. User-entered names, scope and prices are preserved on language changes. Native-speaker review and other browser print engines remain unverified.

Evidence: 21 Python tests; Chromium original proposal workflow and six-locale preference/storage/draft/content/totals/error/mobile checks. Prior 28-page print fixture preserves all 180 content markers and correct totals inside page margins. Container restart/clean-volume restore preserves drafts, snapshots and revoked access, with new writes after recovery. See docs/PRINT.md and docs/DEPLOYMENT.md for limits and reproduction.

## Owner publication

[Prefilled GitHub form](https://github.com/new?name=proposal-lane&description=Open-source%20alternative%20to%20Better%20Proposals%20for%20proposals%20and%20estimates.%20Line-item%20pricing%2C%20immutable%20client%20snapshots%2C%20revocable%20sharing%20and%20print-to-PDF.%20Self-hosted%2C%20six%20languages%2C%20MIT%20licensed.&visibility=public)

Create an empty repository under anshuman-pandey, then give the product-specific go-ahead to push. Existing contents will be inspected before publishing. Naming remains subject to owner review. Public source publication is separate from a release or verified HTTPS demo. No signatures, payments or full Better Proposals parity are claimed.
