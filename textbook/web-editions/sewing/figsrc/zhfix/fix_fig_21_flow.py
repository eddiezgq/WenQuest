"""fig_21_flow: cutting box '自动裁床（21.2）' -> '自动裁床（28.2）'."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_21_flow.png', S=1.7)
g.fix((188, 454, 300, 474), '自动裁床（21.2）', '自动裁床（28.2）', align='c')
g.save(); g.crop((170, 430, 320, 480), SP + 'flow.png', z=4)
