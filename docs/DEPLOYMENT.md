# Persistent local hosting

Use Docker or Python 3.12 with the pinned requirements. This is a self-hosting preview; no hosted service or public HTTPS deployment is configured.

```sh
python3 scripts/setup.py
docker compose up --build -d
```

Setup creates `.env` with a random owner key and mode 0600, refusing to overwrite an existing file. Read it locally to unlock http://127.0.0.1:8095. Do not share or commit the owner key. Compose binds to localhost only. Client links therefore work on that machine; remote collaboration requires a separately configured trusted HTTPS reverse proxy and firewall. Create links using the final HTTPS origin.

The service uses Waitress, UID 10001, a read-only container filesystem, writable named `/data` volume, temporary `/tmp`, dropped capabilities and no-new-privileges. Requests are limited to 256 KiB. Never run `docker compose down -v` unless intentionally deleting all drafts and snapshots.

## Backup

Stop writes before copying the SQLite database out of the container:

```sh
docker compose stop
mkdir -m 700 backup
container=$(docker compose ps -aq proposal-lane)
docker cp "$container:/data/proposal.sqlite3" backup/source.sqlite3
chmod 600 backup/source.sqlite3
python3 scripts/backup.py backup/source.sqlite3 backup/proposal.sqlite3
docker compose start
```

The backup script uses SQLite's backup API, checks integrity, creates mode 0600 and refuses to overwrite a destination. Protect both copies; they contain client scopes, prices and share records. Store the owner key separately. Do not copy a live database file directly.

Restore into a new empty volume with the destination service stopped. Put the backup at `/data/proposal.sqlite3`, set owner UID/GID 10001 and permissions 0600, and give UID 10001 ownership of `/data`. Start with the original owner key. Verify draft revisions, old immutable snapshots and previously revoked links before accepting writes. Never overwrite the sole backup or a running database.

## Reproduce recovery acceptance

```sh
docker build -t proposal-lane-acceptance:local .
python3 scripts/container_acceptance.py
```

The test uses disposable containers/volumes. It verifies exact calculated totals, draft edits versus old snapshots, restart, private backup, clean-volume restore, persistence of revocation, new edits/shares after recovery, and stale-write rejection. Test resources are removed afterward. Optional `pip_ca` build secret supports trusted private CA bundles while retaining TLS verification.

Pending: six-language interface, native-speaker review, other browser print engines and public HTTPS acceptance. Snapshot links are bearer credentials, not identity verification or legal acceptance. Revocation cannot delete previously saved PDFs.
