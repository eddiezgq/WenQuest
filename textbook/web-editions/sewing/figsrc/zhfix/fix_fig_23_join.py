"""fig_23_join: whole-garment knitting note '（第 17、22 章）' -> '（第 17、29 章）'."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_23_join.png', S=1.7)
g.fix((1615, 593, 1810, 613), '只用于针织（第 17、22 章', '只用于针织（第 17、29 章', align='c')
g.save(); g.crop((1600, 585, 1840, 616), SP + 'j.png', z=3)
