"""fig_18_struct: comms interface '联网（第 19 章）、' -> '联网（第 26 章）、'."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_18_struct.png', S=1.7)
g.fix((1718, 514, 1828, 535), '联网（第 19 章', '联网（第 26 章', align='c')
g.save(); g.crop((1680, 480, 1880, 560), SP + 'st.png', z=3)
