from en_svgkit import *
x0,x1,y0,y1=119,860,150,560
X=lambda t:x0+(x1-x0)*t/20; Y=lambda w:y1-(y1-y0)*w/600
sew=[(3,7),(9,13),(16,19)]
def wave(lo,hi):
    pts=[(0,lo)];
    for a,b in sew: pts+= [(a,lo),(a,hi),(b,hi),(b,lo)]
    pts.append((20,lo)); return path([(X(t),Y(w)) for t,w in pts])
s=frame(x0,y0,x1,y1,7)
for t in range(0,21,5): s+=f'<line x1="{X(t)}" y1="{y0}" x2="{X(t)}" y2="{y1}" stroke="#dde1e5"/><text x="{X(t)}" y="{y1+24}" text-anchor="middle">{t}</text>'
for w in range(0,601,200): s+=f'<line x1="{x0}" y1="{Y(w)}" x2="{x1}" y2="{Y(w)}" stroke="#dde1e5"/><text x="{x0-7}" y="{Y(w)+4}" text-anchor="end">{w}</text>'
for a,b in sew: s+=f'<rect x="{X(a)}" y="{y0+1}" width="{X(b)-X(a)}" height="18" fill="#c9d8f3"/><text x="{(X(a)+X(b))/2}" y="{y0+14}" text-anchor="middle" style="font-size:12.5px;fill:#2a5fb8;font-weight:700">sew</text>'
s+=f'<path d="{wave(380,520)}" fill="none" stroke="#c8352b" stroke-width="2"/><path d="{wave(15,300)}" fill="none" stroke="#2e9e5b" stroke-width="2"/>'
s+=f'<text x="{x1-5}" y="{Y(545)}" text-anchor="end" style="fill:#c8352b;font-weight:700">Clutch motor: always spinning, more while sewing</text>'
s+=f'<text x="{x1-5}" y="{Y(340)}" text-anchor="end" style="fill:#2e9e5b;font-weight:700">Servo: output only when sewing and accelerating</text>'
s+=f'<text x="{(x0+x1)/2}" y="{y1+46}" text-anchor="middle" style="font-size:14.5px">Time (s)</text>'
s+=f'<text transform="translate({x0-50},{(y0+y1)/2}) rotate(-90)" text-anchor="middle" style="font-size:14px">Motor input power (W, illustrative)</text>'
bx=1120;L=360/79.9
s+='<rect x="980" y="150" width="680" height="431" rx="8" fill="#fff" stroke="#e2e5e8" stroke-width="1.5"/>'
for i,(n,v,c,txt) in enumerate([("Clutch motor",79.9,"#d46b5f","799 000 kWh"),("Servo",44.4,"#5fb680","444 000 kWh"),("Saving",35.5,"#6495e0","355 000 kWh")]):
    yy=200+120*i; tc={"#d46b5f":"#c8352b","#5fb680":"#1f8a4c","#6495e0":"#2a5fb8"}[c]
    s+=f'<text x="1000" y="{yy+31}" style="fill:{tc};font-weight:700;font-size:14.5px">{n}</text><rect x="{bx}" y="{yy}" width="{v*L}" height="50" rx="3" fill="{c}"/><text x="{bx+v*L+7}" y="{yy+31}" style="fill:#1b2430;font-weight:700;font-size:14px">{txt}</text>'
s+='<text x="1000" y="370" style="fill:#1f8a4c;font-size:13px">(direct drive)</text>'
s+='<text x="1000" y="556" style="fill:#1b2430;font-size:14px">Saves about 45%, cutting about 202 t CO₂ a year (0.57 kg/kWh, worked example)</text>'
inner=f'<svg width="1700" height="700" style="font-size:14px">{s}</svg><p class="foot" style="top:650px">The left chart is an illustrative curve explaining the principle, not a measurement; how much is saved depends on the share of running time actually spent sewing.</p>'
render('fig_23_power',page(1700,700,'Clutch motor versus servo direct drive: drawing power whenever switched on, or only while sewing',
 'Left: power over one work cycle (illustrative); right: annual electricity use of a 500-machine factory, each machine running 3550 h a year (from the average powers 0.45 / 0.25 kW in a published retrofit case)',inner))
