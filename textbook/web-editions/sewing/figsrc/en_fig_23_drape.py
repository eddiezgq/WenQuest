# English fig_23_drape; shapes from the large-deflection cantilever model of lab 30-1 (soft.html), computed by
# running that lab's own elastica() in node (see scratch drape.js); data embedded below via json file.
import json,sys,os
from en_svgkit import *
D=json.load(open(sys.argv[1] if len(sys.argv)>1 else os.path.join(H,'en_fig_23_drape.json')))
names=["Single jersey (knit)","Shirt poplin","Suit wool","Denim","Card 0.4 mm","Steel 1 mm"]
cols=["#2e9e5b","#2a6fdb","#b8761a","#8a44b4","#5a6570","#1b2430"]
cx,cy,sc=200,160,521/0.1
s='<rect x="90" y="139" width="110" height="43" rx="3" fill="#5a6570"/><text x="145" y="166" text-anchor="middle" style="fill:#fff;font-weight:700;font-size:14px">Clamp</text>'
for i in [5,4,0,1,2,3]:
    d=D[i];p=path([(cx+x*sc,cy-y*sc) for x,y in d['pts']])
    st='stroke-dasharray="9 5" stroke-width="2.4"' if i==4 else 'stroke-width="2.4"'
    s+=f'<path d="{p}" fill="none" stroke="{cols[i]}" {st}/>'
s+='<text x="730" y="152" style="fill:#1b2430;font-weight:700;font-size:13.5px">Steel 1 mm</text><text x="730" y="191" style="fill:#5a6570;font-weight:700;font-size:13.5px">Card 0.4 mm</text>'
def fB(B): return f'{B*1e6:.1f} μN·m' if B<1e-3 else (f'{B:.4f} N·m' if B<1 else f'{B:.1f} N·m')
rows=''.join(f'<tr><td style="color:{cols[i]};font-weight:700;font-size:{15 if i<4 else 16}px">{names[i]}</td><td>{D[i]["c"]:.0f} mm</td><td>{fB(D[i]["B"])}</td><td style="font-weight:700">{D[i]["chord"]:.1f}°</td></tr>' for i in range(6))
inner=f'''<svg width="1700" height="820">{s}</svg>
<div class="card" style="left:940px;top:130px;width:720px;height:420px;padding:14px 20px">
<style>.tb td{{padding:17px 0;border-bottom:none;border-top:1px solid #e2e5e8}}.tb tr:first-child td{{border-top:none}}</style><table class="tb" style="width:100%;font-size:14.5px"><tr style="color:#5a6570;font-weight:700"><td style="padding:14px 0 12px">Material</td><td>Bending length c</td><td>Bending rigidity B</td><td>Chord angle</td></tr>
{rows}</table></div>
<div class="ab" style="left:960px;top:574px;font-size:14.5px;line-height:1.7">B = w c³ (w = weight per unit area). Chord angle: inclination of the line from the clamp to the free end;<br>about 42° at an overhang of L = 2c. Shirt fabric is less than a millionth as stiff as 1 mm steel sheet.</div>
<p class="foot" style="top:770px">Cloth droops after projecting a few centimetres: when a machine picks up a piece of cloth, its shape changes. That is why a sewing machine supports the cloth on the throat plate, holds it with the presser foot and drags it with the feed dog.</p>'''
render('fig_23_drape',page(1700,820,'Why cloth “cannot stand up”: the shape of a 10 cm overhang of various materials under their own weight',
 'Horizontally clamped large-deflection cantilever (elastica under gravity), drawn to equal horizontal and vertical scale; fabric bending lengths are worked-example values',inner))
