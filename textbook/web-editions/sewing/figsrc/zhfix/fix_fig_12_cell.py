"""fig_12_cell: '（第 22 章）' -> '（第 29 章）', '第 22 章的虚拟实验 22-1' -> '第 29 章的虚拟实验 29-1'."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_12_cell.png', S=1.7)
g.fix((1265, 457, 1580, 481), '适合几百件一单的小批量（第 22 章', '适合几百件一单的小批量（第 29 章', fitbox=(1265, 457, 1548, 481))
g.fix((1265, 518, 1615, 542), '第 22 章的虚拟实验 22-1 可以把同一件 T 恤', '第 29 章的虚拟实验 22-1 可以把同一件 T 恤')
g.fix((1265, 518, 1615, 542), '第 29 章的虚拟实验 22-1 可以把同一件 T 恤', '第 29 章的虚拟实验 29-1 可以把同一件 T 恤')
g.save(); g.crop((1260, 450, 1640, 550), SP + 'cell.png', z=2)
