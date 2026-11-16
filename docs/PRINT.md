# Browser print acceptance

Use Print / Save PDF from a saved proposal or client snapshot. Turn off browser-added headers and footers. Output uses A4 pages with 18 mm margins. This is browser printing, not a server-generated PDF download. Unsaved edits must be saved before printing from the editor.

Chromium acceptance covers a one-page proposal and a 28-page stress fixture with 80 scope paragraphs, 100 long line items and a long unbroken client name. The stress test initially exposed horizontal overflow; the paper now wraps unbroken text. Totals stay together and table headers repeat. Automated PDF text/bounds verification confirms every marker occurs once, the expected total appears, no editor controls leak into output, no blank pages appear, and all text fits within page margins. The first rendered page was visually inspected. This is not proof of every possible layout or of other browsers' print engines.

To reproduce, run the local service on port 8096 with a disposable database and `PROPOSAL_OWNER_KEY=proposal-browser-key-000000000000000`. Install Playwright in your test environment and make it available to Node, with Chromium at `/usr/bin/chromium` (override `CHROMIUM_PATH` if needed). Install Poppler for `pdftotext`.

```sh
node scripts/print_acceptance.cjs
python3 scripts/verify_print.py
```

`PROPOSAL_URL`, `PROPOSAL_TEST_KEY` and `PRINT_ARTIFACTS` override the fixture server, key and output directory. Pass the artifact directory to `verify_print.py` when overriding it. The test creates a proposal/share in that disposable database; it does not publish anything. Default artifacts go to `/tmp/proposal-print-pass`.

Remaining: other browser print engines, native-language typography review, public HTTPS and production recovery. Revoking a share prevents future access but cannot erase PDFs a recipient already saved.
