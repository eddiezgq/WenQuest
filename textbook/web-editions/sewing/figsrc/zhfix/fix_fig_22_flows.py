"""fig_22_flows: fully-fashioned knit note '整烫（17、22.4）' -> '整烫（17、29.4）'."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_22_flows.png', S=1.88)
g.fix((1812, 863, 1922, 884), '整烫（17、22.4', '整烫（17、29.4', align='r')
g.save(); g.crop((1640, 860, 1940, 886), SP + 'flows.png', z=3)
