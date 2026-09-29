#!/bin/bash
# Local animation renderer (services/animator) with the Manim venv.
cd /home/claude/wenquest/services/animator
[ -f /home/claude/local/animator.pid ] && kill $(cat /home/claude/local/animator.pid) 2>/dev/null && sleep 1
PATH=/home/claude/manim-venv/bin:$PATH setsid nohup /home/claude/manim-venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8095 > /home/claude/local/animator.log 2>&1 < /dev/null &
echo $! > /home/claude/local/animator.pid
