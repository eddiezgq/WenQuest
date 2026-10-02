# English fig_24_qc; equal-variance normal model of Section 31.2 / lab 31-1 (prev 2%, d'=3.53, t=1.88)
import math
from en_svgkit import *
x0,x1,y0,y1=110,1000,150,560; lo,hi,ym=-4,8,0.42
X=lambda v:x0+(x1-x0)*(v-lo)/(hi-lo); Y=lambda v:y1-(y1-y0)*v/ym
pdf=lambda x,m:math.exp(-0.5*(x-m)**2)/math.sqrt(2*math.pi)
xs=[lo+i*0.02 for i in range(601)]
s=frame(x0,y0,x1,y1,10)
for v in range(-4,9,2): s+=f'<line x1="{X(v)}" y1="{y0}" x2="{X(v)}" y2="{y1}" stroke="#dde1e5"/><text x="{X(v)}" y="{y1+30}" text-anchor="middle">{v}</text>'
for k in range(5): v=k/10; s+=f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="#dde1e5"/><text x="{x0-8}" y="{Y(v)+5}" text-anchor="end">{v:.1f}</text>'
P=lambda f:path([(X(x),Y(f(x))) for x in xs])
s+=f'<path d="{P(lambda x:0.98*pdf(x,3.53))}" fill="none" stroke="#e0662f" stroke-width="1.6" stroke-dasharray="6 4"/>'
s+=f'<path d="{P(lambda x:0.98*pdf(x,0))}" fill="none" stroke="#2a6fdb" stroke-width="2.6"/><path d="{P(lambda x:0.02*pdf(x,3.53))}" fill="none" stroke="#e0662f" stroke-width="2.6"/>'
s+=f'<line x1="{X(1.88)}" y1="{y0}" x2="{X(1.88)}" y2="{y1}" stroke="#c8352b" stroke-width="2" stroke-dasharray="7 4"/>'
B='font-weight:700;font-size:14px;'
s+=f'<text x="{X(0)}" y="{y0+12}" text-anchor="middle" style="{B}fill:#2a6fdb">Good items 98%</text>'
s+=f'<text x="{X(1.88)+8}" y="{y0+28}" style="{B}fill:#c8352b">Threshold: alarm to the right</text>'
s+=f'<text x="{X(3.53)+12}" y="{y0+12}" style="{B}fill:#e0662f">Defect distribution shape (dashed, enlarged)</text>'
s+=f'<text x="{X(4.2)}" y="{Y(0.045)}" style="{B}fill:#e0662f">Defective 2% (solid, true proportion)</text>'
s+=f'<text x="{(x0+x1)/2}" y="{y1+56}" text-anchor="middle" style="font-size:15px">Detector’s “looks defective” score</text><text transform="translate({x0-62},{(y0+y1)/2}) rotate(-90)" text-anchor="middle" style="font-size:15px">Probability density</text>'
s+='<rect x="1100" y="150" width="560" height="410" rx="8" fill="#fff" stroke="#e2e5e8" stroke-width="1.5"/><text x="1120" y="188" style="fill:#1b2430;font-weight:700;font-size:17px">Per 1000 items</text>'
s+='<text x="1350" y="230" text-anchor="middle" style="font-weight:700;font-size:14px">Actually defective</text><text x="1530" y="230" text-anchor="middle" style="font-weight:700;font-size:14px">Actually good</text>'
s+='<text x="1130" y="302" style="fill:#1b2430;font-weight:700;font-size:15px">Alarm</text><text x="1130" y="412" style="fill:#1b2430;font-weight:700;font-size:15px">Pass</text>'
for (cx,cy,v,good) in [(1270,251,19,1),(1450,251,29,0),(1270,361,1,0),(1450,361,951,1)]:
    f,c=('#dff0e6','#1f8a4c') if good else ('#f6e0de','#c8352b')
    s+=f'<rect x="{cx}" y="{cy}" width="160" height="90" rx="6" fill="{f}"/><text x="{cx+80}" y="{cy+57}" text-anchor="middle" style="fill:{c};font-weight:700;font-size:30px">{v}</text>'
s+='<text x="1120" y="499" style="fill:#1b2430;font-size:14px">Precision = 19 ÷ (19 + 29) ≈ 39%:</text><text x="1120" y="522" style="fill:#1b2430;font-size:14px">fewer than four in ten of the alarms are real defects</text>'
inner=f'<svg width="1700" height="700">{s}</svg><p class="foot" style="top:652px">Recall and false-alarm rate belong to the detector itself; precision also depends on how many defects there are. Move the threshold right: fewer false alarms, more misses.</p>'
render('fig_24_qc',page(1700,700,'Vision inspection: score distributions, threshold and confusion matrix',
 'Worked example: defect rate 2%, detector separability d′ = 3.53, threshold 1.88 (recall 95%, false-alarm rate 3%)',inner))
