"""fig_8_oil: side note '（第 20 章）' -> '（第 23 章）' (old ch20 is now ch23)."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_8_oil.png', S=1.7)
# fit up to '章' only: Chrome trims the adjacent '）。' pair
g.fix((1560, 330, 1770, 354), '减少布料沾油（第 20 章', '减少布料沾油（第 23 章', fitbox=(1560, 330, 1735, 354))
g.save(); g.crop((1550, 250, 1830, 360), SP + 'oil.png')
