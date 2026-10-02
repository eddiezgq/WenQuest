o=[]
def box(x0,x1,y,h,t,fill='#fff',st='#c9c9bd',sw=1.6):
    o.append(f'<rect x="{x0}" y="{y}" width="{x1-x0}" height="{h}" rx="9" fill="{fill}" stroke="{st}" stroke-width="{sw}"/>')
    if t: o.append(f'<text x="{(x0+x1)/2}" y="{y+h/2+6}" class="bx" text-anchor="middle">{t}</text>')
def arr(x1,y1,x2,y2): o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2-2 if y1==y2 else x2}" y2="{y2-2 if x1==x2 else y2}" stroke="#b5b5aa" stroke-width="1.6" marker-end="url(#a)"/>')
def out(y,h,t,lines):
    box(1008,1220,y,h,None,'#e6eef9','#2f7bd9',2.6)
    cy=y+h/2-(len(lines))*13+4
    o.append(f'<text x="1114" y="{cy}" class="ob" text-anchor="middle">{t}</text>')
    for i,l in enumerate(lines): o.append(f'<text x="1114" y="{cy+30+i*25}" class="os" text-anchor="middle">{l}</text>')
box(42,212,141,579,None,'#ebebe7','#c9c9bd')
for y,t,c in [(402,'Main shaft','mb'),(438,'(arm shaft)','ms'),(474,'one revolution','ms'),(500,'= one stitch','ms')]:
    o.append(f'<text x="127" y="{y}" class="{c}" text-anchor="middle">{t}</text>')
H=70
rows=[(148,['Needle-bar crank','Needle-bar link']),(272,['Take-up crank pin']),(396,['Timing belt 1:1','Hook shaft','Gears 1:2']),(520,[None,'Feed-lift eccentric','Feed-lift rock shaft']),(644,['Feed eccentric','Stitch-length regulator','Feed rock shaft'])]
X=[(265,477),(513,724),(760,972)]
for y,ts in rows:
    cy=y+H/2
    if ts[0]: arr(212,cy,265,cy)
    prev=None
    for i,t in enumerate(ts):
        if t is None: continue
        box(X[i][0],X[i][1],y,H,t)
        if prev is not None: arr(X[prev][1],cy,X[i][0],cy)
        prev=i
    arr(X[prev][1],cy,1008,cy)
o.append('<text x="866" y="170" class="lab" text-anchor="middle">slider-crank</text>')
o.append('<text x="742" y="294" class="lab" text-anchor="middle">four-bar linkage (the take-up lever is the coupler)</text>')
arr(618,466,618,520)
out(141,85,'Needle bar, needle',['piercing: 1 reciprocation'])
out(264,86,'Take-up lever',['take-up: 1 swing'])
out(388,86,'Rotary hook',['loop catching: 2 turns'])
out(512,208,'Feed bar, feed dog',['feed: horizontal + vertical','combine into one','elliptical path'])
html=('<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">'
'<div class="fig" style="--w:1000px;padding:0"><svg width="1000" height="576" viewBox="0 0 1344 774" xmlns="http://www.w3.org/2000/svg" style="display:block">'
'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 1L10 5L0 9z" fill="#b5b5aa"/></marker></defs>'
'<style>svg text{font-family:QFix,"Noto Sans CJK SC",sans-serif}.t{font-size:23px;font-weight:700;fill:#111}.s{font-size:16.5px;fill:#555}.bx{font-size:18px;fill:#222}'
'.mb{font-size:20px;font-weight:700;fill:#111}.ms{font-size:17px;fill:#555}.ob{font-size:19px;font-weight:700;fill:#111}.os{font-size:16.5px;fill:#555}.lab{font-size:16px;fill:#555}</style>'
'<text x="42" y="52" class="t">One main shaft drives four trains, so the four motions are always in step</text>'
'<text x="42" y="86" class="s">Typical link-type industrial lockstitch machine; the right column shows each output member and how often it acts per revolution</text>'
+''.join(o)+'</svg></div>')
open('figsrc/en_w_423def1c.en.html','w').write(html)
