"""fig_13_sys: comms interface 'RS-485 / CAN（13.8、19 章）' -> '…（13.8、26 章）' (old ch19 is now ch26)."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_13_sys.png', S=1.7)
g.fix((1068, 728, 1280, 750), 'RS-485 / CAN（13.8、19 章）', 'RS-485 / CAN（13.8、26 章）', align='c')
g.save(); g.crop((1020, 670, 1330, 760), SP + 'sys.png', z=2)
