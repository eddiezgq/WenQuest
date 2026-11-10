# FAQ and troubleshooting

> Check `deploy/status.sh` first, then here.

- **The plant manifest has errors**: fix the sheet, row and column named in the message; check locally first with `python -m factory.plant check plant.yaml`.
- **The left sidebar has no Customers & service, Labs & tasks and similar entries**: enterprise plants show only the general parts; those are teaching content for the gearbox demo plant (see the “Plant manifest” chapter).
- **The AI assistant only answers by rules**: no key configured, or the configured provider failed; China deployments use only DeepSeek. See “Plant Insight Hub · AI run log”.
- **The shop board shows no machine status**: check on the “Unified data bus” page that it is connected and that machine IDs match the plant manifest.
- **A proposal stays “Executing”**: check the bridge log (on the server `docker compose -p wq-factory logs --tail 100 bridge`).

```ask
q: The workbench will not open but ERPNext does. What do I check first?
```
