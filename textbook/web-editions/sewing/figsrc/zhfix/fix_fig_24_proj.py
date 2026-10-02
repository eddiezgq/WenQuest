"""fig_24_proj: '第 21 章 • 实验 21-1、22-1' -> '第 28 章 • 实验 28-1、29-1';
'第 21、22 章 • 实验 22-1' -> '第 28、29 章 • 实验 29-1'. One digit span at a time (equal widths)."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_24_proj.png', S=1.7)
B2 = (518, 315, 706, 335)
for o, n in [('第 21 章 • 实验 21-1、22-1', '第 28 章 • 实验 21-1、22-1'),
             ('第 28 章 • 实验 21-1、22-1', '第 28 章 • 实验 28-1、22-1'),
             ('第 28 章 • 实验 28-1、22-1', '第 28 章 • 实验 28-1、29-1')]:
    g.fix(B2, o, n, align='c')
B4 = (1300, 315, 1476, 335)
for o, n in [('第 21、22 章 • 实验 22-1', '第 28、22 章 • 实验 22-1'),
             ('第 28、22 章 • 实验 22-1', '第 28、29 章 • 实验 22-1'),
             ('第 28、29 章 • 实验 22-1', '第 28、29 章 • 实验 29-1')]:
    g.fix(B4, o, n, align='c')
g.save()
g.crop((510, 310, 715, 340), SP + 'pj2.png', z=3)
g.crop((1295, 310, 1480, 340), SP + 'pj4.png', z=3)
