#!/bin/bash
export PATH=/home/claude/manim-venv/bin:$PATH
cd /home/claude/physics/anim
for s in RefFrame Derivative Projectile Circular Relative; do
  manim -r 1920,1080 --fps 30 --disable_caching ch1.py $s > log_$s.txt 2>&1 && echo "$s ok" >> done.txt || echo "$s FAIL" >> done.txt
done
echo ALL >> done.txt
