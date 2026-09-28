#!/bin/bash
# Restart the local gateway (kills by pid file, never by pattern).
cd /home/claude/wenquest/services/gateway
[ -f /home/claude/local/gateway.pid ] && kill $(cat /home/claude/local/gateway.pid) 2>/dev/null && sleep 1
set -a; . /home/claude/local/gateway.env; set +a
nohup python3 -m uvicorn app.main:create_app --factory --host 0.0.0.0 --port 8090 > /home/claude/local/gateway.log 2>&1 &
echo $! > /home/claude/local/gateway.pid
