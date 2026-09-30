#!/bin/sh
# Download the voice models (GitHub releases of k2-fsa/sherpa-onnx) into $1 (default /models).
set -eu
D=${1:-/models}
B=https://github.com/k2-fsa/sherpa-onnx/releases/download
mkdir -p "$D"
cd "$D"
[ -d kokoro-int8-multi-lang-v1_0 ] || curl -fsSL "$B/tts-models/kokoro-int8-multi-lang-v1_0.tar.bz2" | tar xj
[ -d sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09 ] || {
  curl -fsSL "$B/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09.tar.bz2" | tar xj
  rm -rf sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2025-09-09/test_wavs
}
[ -f silero_vad.onnx ] || curl -fsSLO "$B/asr-models/silero_vad.onnx"
