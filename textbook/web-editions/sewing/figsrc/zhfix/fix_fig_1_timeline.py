"""fig_1_timeline: stage chapter refs updated to the renumbered book (ch01 text)."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig


def shift(dy):
    """Erase by copying the same columns from dy rows away (dash period 16 px) so the dashed
    year gridlines that run behind the labels are kept intact."""
    def f(a, x0, y0, x1, y1, bg):
        a[y0:y1, x0:x1] = a[y0 + dy:y1 + dy, x0:x1]
    return f


g = Fig('fig_1_timeline.png', S=1.9)
g.fix((1180, 481, 1400, 503), '旋梭、四动作送布（第 2–7 章）', '旋梭、四动作送布（第 2–8 章）', align='l', erase=shift(96))
g.fix((1130, 667, 1345, 690), '电子针距与张力（第 13–14 章）', '电子针距与张力（第 13–22 章）', align='r', erase=shift(96))
g.fix((1580, 851, 1726, 874), '第 19、23、24 章）', '第 14、26、30、31 章）', align='r', erase=shift(-128), fitbox=(1600, 851, 1726, 874))
g.save()
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g.crop((1170, 455, 1410, 510), SP + 't1.png')
g.crop((1120, 645, 1360, 695), SP + 't3.png')
g.crop((1500, 828, 1740, 880), SP + 't5.png')
