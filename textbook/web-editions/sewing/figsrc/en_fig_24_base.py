# English fig_24_base; same model as lab 31-1: precision vs defect rate at t=1.88 and at the cost-optimal threshold (Cm=20, Cf=0.5)
import math
from en_svgkit import *
Phi=lambda x:0.5*(1+math.erf(x/math.sqrt(2)))
dp=3.53
def insp(p,t,n=1000):
    tpr=1-Phi(t-dp);fpr=1-Phi(t);tp=p*tpr;fp=(1-p)*fpr;fn=p*(1-tpr)
    return tp/(tp+fp), n*(fn*20+fp*0.5)
def best(p):
    bt,bc=0,1e18
    for i in range(-100,601):
        t=i/100;c=insp(p,t)[1]
        if c<bc-1e-12: bc,bt=c,t
    return bt
x0,x1,y0,y1=120,1000,150,560
lx0,lx1=math.log10(0.001),math.log10(0.2)
X=lambda p:x0+(x1-x0)*(math.log10(p)-lx0)/(lx1-lx0); Y=lambda v:y1-(y1-y0)*v
s=frame(x0,y0,x1,y1,10)
for v in range(0,101,20): s+=f'<line x1="{x0}" y1="{Y(v/100)}" x2="{x1}" y2="{Y(v/100)}" stroke="#dde1e5"/><text x="{x0-10}" y="{Y(v/100)+5}" text-anchor="end">{v}%</text>'
for p,l in [(0.001,'0.1%'),(0.003,'0.3%'),(0.01,'1%'),(0.03,'3%'),(0.1,'10%'),(0.2,'20%')]: s+=f'<text x="{X(p)}" y="{y1+30}" text-anchor="middle">{l}</text>'
ps=[10**(lx0+(lx1-lx0)*i/200) for i in range(201)]
s+=f'<path d="{path([(X(p),Y(insp(p,1.88)[0])) for p in ps])}" fill="none" stroke="#2a6fdb" stroke-width="2.6"/>'
s+=f'<path d="{path([(X(p),Y(insp(p,best(p))[0])) for p in ps[::4]])}" fill="none" stroke="#e0662f" stroke-width="2.2" stroke-dasharray="8 5"/>'
for p in [0.01,0.02,0.1]:
    v=insp(p,1.88)[0]; s+=f'<circle cx="{X(p)}" cy="{Y(v)}" r="8" fill="#2a6fdb"/><text x="{X(p)+14}" y="{Y(v)+26}" style="fill:#2a6fdb;font-weight:700;font-size:15px">{p*100:.0f}%: {v*100:.0f}%</text>'
    print(p,v,insp(p,best(p))[0])
s+=f'<line x1="140" y1="174" x2="182" y2="174" stroke="#2a6fdb" stroke-width="2.6"/><text x="192" y="179" style="fill:#2a6fdb;font-weight:700;font-size:13.5px">Fixed threshold 1.88</text>'
s+=f'<line x1="140" y1="200" x2="182" y2="200" stroke="#e0662f" stroke-width="2.2" stroke-dasharray="8 5"/><text x="192" y="205" style="fill:#e0662f;font-weight:700;font-size:13.5px">Lowest-cost threshold at each defect rate</text>'
s+=f'<text x="{(x0+x1)/2}" y="{y1+56}" text-anchor="middle" style="font-size:15px">Defect rate (log scale)</text><text transform="translate({x0-66},{(y0+y1)/2}) rotate(-90)" text-anchor="middle" style="font-size:15px">Precision (share of alarms that are real defects)</text>'
txt=['Why?','At a 2% defect rate, 1000 items contain only 20 defects,','and 19 are caught; 3% of the 980 good items raise an alarm,','that is 29. There are more false alarms than defects.','','So a quality-inspection model cannot be judged','by a figure such as “98% accuracy” alone.','Ask, at your own factory’s defect rate,','what share of the alarms are real,','and what misses and re-checks each cost.']
s+=''.join(f'<text x="1100" y="{200+30*i}" style="fill:#1b2430;font-size:15px">{t}</text>' for i,t in enumerate(txt))
render('fig_24_base',page(1700,660,'Base rate: the rarer the defects, the less an alarm can be trusted',
 'Precision of the same detector (recall 95%, false-alarm rate 3%) at different defect rates; dashed: the lowest-cost threshold at each defect rate (miss 20 yuan, re-check 0.5 yuan, worked example)',f'<svg width="1700" height="660">{s}</svg>'))
