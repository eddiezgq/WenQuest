#!/usr/bin/env bash
# Textbook animations after a deploy: forget earlier failures (a new animator may render them now), wait until
# the gateway's worker has made every video (at most WAIT seconds), then print what is ready and why the rest failed.
# Usage: deploy/textbook-media.sh [WAIT]      Called by the deploy job; never fails the deploy.
. "$(dirname "$0")/lib.sh"
WAIT="${1:-600}"

status() {
    dc exec -T gateway python - <<'PY'
import json, pathlib
root, media = pathlib.Path("/textbook"), pathlib.Path("/data/textbook-media")
ready = total = 0
for idx in sorted(root.glob("*/web/index.json")):
    book = idx.parent.parent.name
    for name, h in (json.loads(idx.read_text(encoding="utf-8")).get("anims") or {}).items():
        total += 1
        d = media / book
        if (d / f"{name}-{h}.mp4").exists():
            ready += 1
        elif (d / f"{name}-{h}.err").exists():
            err = json.loads((d / f"{name}-{h}.err").read_text(encoding="utf-8")).get("error", "")
            print(f"FAILED {book}/{name}: " + " | ".join(err.splitlines())[:1500])
print(f"READY {ready}/{total}")
PY
}

dc exec -T gateway sh -c 'rm -f /data/textbook-media/*/*.err' 2>/dev/null || true
end=$(( $(date +%s) + WAIT ))
while :; do
    out=$(status 2>&1 || true)
    line=$(printf '%s\n' "$out" | grep '^READY' | tail -n 1)
    r=${line#READY }
    if [ -n "$line" ] && [ "${r%/*}" = "${r#*/}" ]; then break; fi
    if printf '%s\n' "$out" | grep -q '^FAILED' || [ "$(date +%s)" -ge "$end" ]; then break; fi
    sleep 20
done
log "Textbook animations:"
printf '%s\n' "$out"
dc logs --since 30m gateway 2>/dev/null | grep -i 'textbook animation' | tail -n 20 || true
