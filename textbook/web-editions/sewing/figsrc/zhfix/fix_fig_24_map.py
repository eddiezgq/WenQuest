"""fig_24_map: data/app cards '（第 19 章）' -> 26, '（第 21 章）' -> 28, '布边追踪（第 23 章）' -> 30.
Lines that start with '（' are rendered with Chrome's line-start bracket trim, so the fit starts at '第'."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_24_map.png', S=1.7)
g.fix((715, 361, 805, 383), '第 19 章）', '第 26 章）', align='c', fitbox=(726, 361, 805, 383), size=30)
g.fix((1195, 361, 1287, 383), '第 21 章）', '第 28 章）', align='c', fitbox=(1208, 361, 1287, 383), size=30)
g.fix((186, 561, 358, 583), '布边追踪（第 23 章', '布边追踪（第 30 章', align='c', fitbox=(186, 561, 345, 583))
g.save()
g.crop((700, 330, 820, 386), SP + 'm1.png', z=3)
g.crop((1180, 330, 1300, 386), SP + 'm2.png', z=3)
g.crop((180, 530, 370, 586), SP + 'm3.png', z=3)
