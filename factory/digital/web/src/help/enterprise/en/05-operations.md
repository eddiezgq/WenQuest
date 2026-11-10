# Operations: status, backup, restore, restart

> The digital factory is installed in `/opt/wenquest/factory` on the server; run all the commands below in this directory.

## Everyday commands

| Command | What it does |
| --- | --- |
| `deploy/status.sh` | State and memory of each container, history database size, response of the workbench and ERPNext URLs |
| `deploy/backup.sh` | Backs up the history database, ERPNext (database plus attachments) and `.env`; runs automatically at 03:30 every day with the learning platform backup |
| `deploy/restore.sh backups/<time>` | Restores the history database and ERPNext from a backup; first backs up the current data again automatically |
| `deploy/update.sh` | No arguments: restart the current version (after changing `.env`, e.g. a new plant manifest or AI key) |

New versions deploy automatically on push (tests → build image → run `deploy/update.sh new-image` on the server); no manual upgrades.

## Watch out for

- `.env` holds all passwords and lives only on the server; keep your own copy;
- Before switching plant manifests, run `python -m factory.plant check manifest.yaml` on your own computer first;
- Restore drill: restore once on another machine with `deploy/restore.sh` to confirm the backups work.

More detail is in “Digital factory go-live and maintenance” under “Documents” on the help home page.

```ask
q: How do I confirm last night's backup succeeded?
```
