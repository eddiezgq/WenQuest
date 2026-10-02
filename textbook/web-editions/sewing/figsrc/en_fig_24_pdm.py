# English fig_24_pdm; data from lab 31-1's own fleet()/alarms() model (seed 11, sigma 0.08), run via en_fig_24_pdm_sim.js
import json,subprocess
from en_svgkit import *
D=json.loads(subprocess.run(['node',os.path.join(H,'en_fig_24_pdm_sim.js')],capture_output=True,text=True,check=True).stdout)
m=[q for q in D['machines'] if q['i']==6][0]; sig=m['sig']; t0,fail=m['t0'],m['fail']
x0,x1,y0,y1=110,800,150,589; lo,hi=0.68,2.1
X=lambda d:x0+(x1-x0)*d/180; Y=lambda v:y1-(y1-y0)*(min(hi,max(lo,v))-lo)/(hi-lo)
s=frame(x0,y0,x1,y1,10)
for d in range(0,181,30): s+=f'<line x1="{X(d)}" y1="{y0}" x2="{X(d)}" y2="{y1}" stroke="#dde1e5"/><text x="{X(d)}" y="{y1+30}" text-anchor="middle">{d}</text>'
for k in range(7): v=0.8+0.2*k; s+=f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="#dde1e5"/><text x="{x0-10}" y="{Y(v)+5}" text-anchor="end">{v:.1f}</text>'
s+=f'<path d="{path([(X(d),Y(sig[d])) for d in range(fail)])}" fill="none" stroke="#2a6fdb" stroke-opacity=".4" stroke-width="1"/>'
ma=[(d,sum(sig[d-2:d+1])/3) for d in range(2,fail)]
s+=f'<path d="{path([(X(d),Y(v)) for d,v in ma])}" fill="none" stroke="#2a6fdb" stroke-width="2.6"/>'
s+=f'<line x1="{x0}" y1="{Y(1.12)}" x2="{x1}" y2="{Y(1.12)}" stroke="#c8352b" stroke-width="1.6" stroke-dasharray="7 4"/><text x="{x0+8}" y="{Y(1.12)-8}" style="fill:#c8352b;font-weight:700;font-size:14px">Threshold 1.12</text>'
s+=f'<line x1="{X(t0)}" y1="{y0}" x2="{X(t0)}" y2="{y1}" stroke="#5a6570" stroke-width="1.3" stroke-dasharray="4 3"/><text x="{X(t0)-6}" y="{y0+24}" text-anchor="end" style="font-size:14px">Degradation starts</text>'
s+=f'<line x1="{X(fail)}" y1="{y0}" x2="{X(fail)}" y2="{y1}" stroke="#1b2430" stroke-width="1.6" stroke-dasharray="6 3"/><text x="{X(fail)+6}" y="{y0+24}" style="fill:#1b2430;font-weight:700;font-size:14px">Failure</text>'
al=m['marks'][0]; s+=f'<path d="M{X(al)},{y1-6} l-8,14 l16,0z" fill="#e0662f"/><text x="{X(al)}" y="{y1-16}" text-anchor="middle" style="fill:#e0662f;font-weight:700;font-size:14px">Alarm: {fail-al} days ahead</text>'
s+=f'<text x="{(x0+x1)/2}" y="{y1+56}" text-anchor="middle" style="font-size:15px">Day</text><text transform="translate({x0-62},{(y0+y1)/2}) rotate(-90)" text-anchor="middle" style="font-size:15px">Normalised indicator</text>'
a0,a1,b0,b1=960,1619,150,580
XR=lambda f:a0+(a1-a0)*f; YR=lambda v:b1-(b1-b0)*v/30
s+=frame(a0,b0,a1,b1,10)
for f in [0,0.25,0.5,0.75,1]: s+=f'<line x1="{XR(f)}" y1="{b0}" x2="{XR(f)}" y2="{b1}" stroke="#dde1e5"/><text x="{XR(f)}" y="{b1+30}" text-anchor="middle">{f:g}</text>'
for v in range(0,31,5): s+=f'<line x1="{a0}" y1="{YR(v)}" x2="{a1}" y2="{YR(v)}" stroke="#dde1e5"/><text x="{a0-10}" y="{YR(v)+5}" text-anchor="end">{v}</text>'
for i,(w,c) in enumerate([('1','#c8352b'),('3','#2a6fdb'),('7','#2e9e5b')]):
    pts=[(XR(f),YR(l)) for t,f,l,det in D['curves'][w] if abs(t*100-round(t*100))<1e-6 and f<=1.0 and det>0]
    s+=f'<path d="{path(pts)}" fill="none" stroke="{c}" stroke-width="2.4"/><text x="{a1-12}" y="{b0+30+22*i}" text-anchor="end" style="fill:{c};font-weight:700;font-size:14px">— Window {w} day{"s" if w!="1" else ""}</text>'
s+=f'<text x="{(a0+a1)/2}" y="{b1+56}" text-anchor="middle" style="font-size:15px">False alarms per machine per month</text><text transform="translate({a0-56},{(b0+b1)/2}) rotate(-90)" text-anchor="middle" style="font-size:15px">Average lead time (days)</text>'
s+=f'<text x="{a0}" y="690" style="fill:#1b2430;font-size:14px">At the same number of false alarms, higher is better. A 3-day window gives the longest lead time</text><text x="{a0}" y="712" style="fill:#1b2430;font-size:14px">when false alarms are very few; with too long a window, alarms come late.</text>'
inner=f'<svg width="1700" height="780">{s}</svg><p class="foot" style="top:730px">Lower threshold: earlier alarms, more false alarms. Wider smoothing window: fewer false alarms, later alarms. Predictive maintenance has to pick a point between the two that the workshop can accept.</p>'
render('fig_24_pdm',page(1700,780,'Predictive maintenance: alarm earlier, or with fewer false alarms?',
 'Worked example: 200 machines, 180 days; left: daily signal of one degrading machine and its 3-day moving average; right: average lead time versus false alarms for different thresholds and smoothing windows',inner))
