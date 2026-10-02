from en_svgkit import *
x0,x1,y0,y1=119,819,150,560
X=lambda n:x0+(x1-x0)*(n-1)/19; Y=lambda v:y1-(y1-y0)*v
s=frame(x0,y0,x1,y1,10)
for n in [1,5,10,15,20]: s+=f'<line x1="{X(n)}" y1="{y0}" x2="{X(n)}" y2="{y1}" stroke="#dde1e5"/><text x="{X(n)}" y="{y1+30}" text-anchor="middle">{n}</text>'
for v in range(0,101,20): s+=f'<line x1="{x0}" y1="{Y(v/100)}" x2="{x1}" y2="{Y(v/100)}" stroke="#dde1e5"/><text x="{x0-10}" y="{Y(v/100)+5}" text-anchor="end">{v}%</text>'
s+=f'<line x1="{x0}" y1="{Y(.9)}" x2="{x1}" y2="{Y(.9)}" stroke="#1b2430" stroke-width="1.3" stroke-dasharray="6 4"/><text x="{X(18.4)}" y="{Y(.9)+20}" style="fill:#1b2430;font-weight:700;font-size:13px">90%</text>'
for p,c in [(0.9,'#c8352b'),(0.95,'#b8761a'),(0.97,'#e0662f'),(0.99,'#2a6fdb'),(0.999,'#2e9e5b')]:
    s+=f'<path d="{path([(X(n),Y(p**n)) for n in range(1,21)])}" fill="none" stroke="{c}" stroke-width="2.6"/><text x="{x1+10}" y="{Y(p**20)+5}" style="fill:{c};font-weight:700;font-size:14px">p = {p}</text>'
s+=f'<circle cx="{X(10)}" cy="{Y(.97**10)}" r="8" fill="#e0662f"/><text x="{X(10.4)}" y="{Y(.97**10)-20}" style="fill:#e0662f;font-weight:700;font-size:14.5px">97%, 10 steps: 74%</text>'
s+=f'<text x="{(x0+x1)/2}" y="{y1+56}" text-anchor="middle" style="font-size:15px">Number of action steps n</text><text transform="translate({x0-62},{(y0+y1)/2}) rotate(-90)" text-anchor="middle" style="font-size:15px">Unattended completion rate</text>'
# right
def interv(p,n=10,ts=8,tf=30):
    f=n*(1-p)/p; cyc=n*ts/p+f*tf; return 3600/cyc*f
a0,a1=995,1600; Yr=lambda v:y1-(y1-y0)*v/25
s+=frame(a0,y0,a1,y1,10)
for v in range(0,26,5): s+=f'<line x1="{a0}" y1="{Yr(v)}" x2="{a1}" y2="{Yr(v)}" stroke="#dde1e5"/><text x="{a0-14}" y="{Yr(v)+5}" text-anchor="end">{v}</text>'
ps=[0.95,0.97,0.98,0.99,0.995,0.999];w=(a1-a0)/6
for i,p in enumerate(ps):
    v=interv(p);cx=a0+w*(i+.5)
    s+=f'<rect x="{cx-30}" y="{Yr(v)}" width="60" height="{Yr(0)-Yr(v)}" fill="#6495e0"/><text x="{cx}" y="{Yr(v)-8}" text-anchor="middle" style="fill:#1b2430;font-weight:700;font-size:13.5px">{v:.1f}</text><text x="{cx}" y="{y1+30}" text-anchor="middle">{p}</text>'
s+=f'<text x="{(a0+a1)/2}" y="{y1+56}" text-anchor="middle" style="font-size:15px">Single-step success rate</text><text transform="translate({a0-52},{(y0+y1)/2}) rotate(-90)" text-anchor="middle" style="font-size:15px">Human interventions per hour</text>'
inner=f'<svg width="1700" height="700">{s}</svg><p class="foot" style="top:650px">The reported success rate for separating fabric pieces is 97%; for a 10-step flow to finish unattended 90% of the time, every step must reach about 99%.</p>'
render('fig_23_chain',page(1700,700,'Each action done well does not mean the whole flow runs through',
 'Left: unattended completion rate of the whole flow = single-step success rate to the power n; right: human interventions per hour with 10 steps, 8 s per step and 30 s per human fix',inner))
