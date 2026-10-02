"""fig_23_road: chapter refs 12、22 -> 12、29; 19 -> 26; 24 -> 31; 第 23.6 节 -> 第 30.6 节."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_23_road.png', S=1.7)
g.fix((1030, 336, 1180, 358), '成熟（第 12、22 章', '成熟（第 12、29 章')
g.fix((548, 512, 680, 534), '推广中（第 19 章', '推广中（第 26 章')
g.fix((548, 689, 660, 711), '起步（第 24 章', '起步（第 31 章')
g.fix((1512, 689, 1600, 711), '第 23.6 节', '第 30.6 节')
g.save()
g.crop((1030, 330, 1200, 362), SP + 'r1.png', z=3)
g.crop((548, 506, 700, 538), SP + 'r2.png', z=3)
g.crop((548, 684, 690, 716), SP + 'r3.png', z=3)
g.crop((1510, 684, 1610, 716), SP + 'r4.png', z=3)
