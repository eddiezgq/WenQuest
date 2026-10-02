"""fig_19_mes: digital-twin simulation '模型用第 12、22 章的仿真' -> '模型用第 12、29 章的仿真'."""
import sys; sys.path.insert(0, '/home/claude/sm/figsrc/zhfix')
from zhlib import Fig
SP = '/tmp/claude-0/-home-claude/977649d0-331f-55bb-b300-57007deb1961/scratchpad/'
g = Fig('fig_19_mes.png', S=1.7)
g.fix((1436, 475, 1764, 495), '模型用第 12、22 章的仿真，参数用实测工时和效率', '模型用第 12、29 章的仿真，参数用实测工时和效率', align='c')
g.save(); g.crop((1380, 450, 1820, 500), SP + 'mes.png', z=2)
