"""fig_24_t9: result card '数据回到总线（第 19 章）' -> '…（第 26 章）' (第 14 章 unchanged)."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_24_t9.png', S=1.7)
g.fix((1618, 243, 1772, 263), '数据回到总线（第 19 章', '数据回到总线（第 26 章', align='c')
g.save()
g.crop((1600, 200, 1800, 266), SP + 't9.png', z=3)
