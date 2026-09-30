#!/bin/bash
# Restart the local lab checker (kills by pid file, never by pattern).
cd /home/claude/wenquest/services/labcheck
[ -f /home/claude/local/labcheck.pid ] && kill $(cat /home/claude/local/labcheck.pid) 2>/dev/null && sleep 1
nohup python3 -m uvicorn app:app --host 127.0.0.1 --port 8096 > /home/claude/local/labcheck.log 2>&1 &
echo $! > /home/claude/local/labcheck.pid
