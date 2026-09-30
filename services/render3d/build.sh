#!/bin/sh
# Bundle the WenQuest 3D engine (three.js + GLTFLoader + OrbitControls + wq3d) into one file the gateway inlines
# into 3D animation pages and 3D virtual labs (they may not load anything from the network).
set -e
cd "$(dirname "$0")"
OUT=../gateway/app/production/three
mkdir -p "$OUT"
npx esbuild src/entry.js --bundle --format=iife --global-name=WQ3D --minify --legal-comments=none --outfile="$OUT/wq3d.js"
cp node_modules/three/LICENSE "$OUT/THREE-LICENSE.txt"
ls -la "$OUT"
