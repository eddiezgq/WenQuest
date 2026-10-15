#!/usr/bin/env bash
# Build site/vendor (fonts and libraries, 第 34 轮) and put it on a server, only when its version changed.
# Usage (CI deploy jobs): bash tools/vendor/deploy.sh deploy@<host>
set -euo pipefail
TARGET="$1"
cd "$(dirname "$0")"
npm ci --ignore-scripts --no-audit --no-fund --silent
python3 build.py ../../site/vendor
cd ../..
NEW=$(cat site/vendor/VERSION)
OLD=$(ssh "$TARGET" 'cat /opt/wenquest/site/vendor/VERSION 2>/dev/null || true')
if [ "$NEW" = "$OLD" ]; then
    echo "site/vendor $NEW is already on the server"
    exit 0
fi
# unpack next to the live folder, then swap, so pages never see a half-copied folder
tar czf - -C site vendor | ssh "$TARGET" 'set -e; cd /opt/wenquest/site; rm -rf vendor.new vendor.old; mkdir vendor.new; tar xzf - -C vendor.new --strip-components=1; [ -d vendor ] && mv vendor vendor.old; mv vendor.new vendor; rm -rf vendor.old'
echo "site/vendor ${OLD:-none} -> $NEW copied"
