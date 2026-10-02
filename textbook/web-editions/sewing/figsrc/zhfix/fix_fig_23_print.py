"""fig_23_print: footnote '小单快反（第 22 章）' -> '小单快反（第 29 章）'."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_23_print.png', S=1.7)
g.fix((637, 689, 782, 710), '小单快反（第 22 章', '小单快反（第 29 章')
g.save(); g.crop((600, 685, 920, 712), SP + 'p.png', z=3)
