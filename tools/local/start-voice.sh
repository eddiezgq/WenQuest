#!/bin/bash
# Restart the local voice service (kills by pid file, never by pattern). Models: services/voice/fetch_models.sh.
cd /home/claude/wenquest/services/voice
M=/home/claude/local/voice-models
[ -d $M/kokoro-int8-multi-lang-v1_0 ] || ./fetch_models.sh $M
[ -f /home/claude/local/voice.pid ] && kill $(cat /home/claude/local/voice.pid) 2>/dev/null && sleep 1
VOICE_MODELS=$M setsid nohup python3 -m uvicorn app:app --host 127.0.0.1 --port 8098 > /home/claude/local/voice.log 2>&1 < /dev/null &
echo $! > /home/claude/local/voice.pid
