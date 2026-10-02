# English fig_24_t9 (chapter ref 19 -> 26)
import math
from en_svgkit import *
boxes=[(40,"Sense","#2a6fdb","#2a5fb8",["Presser-foot height sensor (thickness)","Main-shaft motor current (penetration","resistance); feed-motor load, camera"]),
(450,"Recognise","#8a5cc7","#7444b4",["Change in ply count, crossing a seam,","fabric type;","rules, look-up tables or learned models"]),
(860,"Adjust","#e0662f","#c4531d",["Stitch length, presser-foot pressure,","needle-thread tension, speed,","feed amount (Ch. 14)"]),
(1270,"Result","#2e9e5b","#1f8a4c",["Even stitch length, no skipped stitches,","no thread breaks, no puckering;","data go back to the bus (Ch. 26)"])]
s='<defs><marker id="m" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto"><path d="M0,0 L10,5 L0,10z" fill="#5a6570"/></marker></defs>'
for x,n,c,tc,ls in boxes:
    s+=f'<rect x="{x}" y="130" width="360" height="140" rx="8" fill="#fff" stroke="{c}" stroke-width="2"/><text x="{x+180}" y="160" text-anchor="middle" style="fill:{tc};font-weight:700;font-size:16px">{n}</text>'
    s+=''.join(f'<text x="{x+180}" y="{186+i*19}" text-anchor="middle" style="fill:#1b2430;font-size:13px">{l}</text>' for i,l in enumerate(ls))
for xa in [406,816,1226]: s+=f'<line x1="{xa}" y1="200" x2="{xa+38}" y2="200" stroke="#5a6570" stroke-width="2.6" marker-end="url(#m)"/>'
s+='<path d="M220,274 L220,329 L1450,329 L1450,274" fill="none" stroke="#5a6570" stroke-width="1.6" stroke-dasharray="7 4"/><text x="820" y="352" text-anchor="middle" style="font-size:13.5px">Closed loop: keep measuring after adjusting</text>'
s+='<rect x="60" y="420" width="980" height="308" rx="8" fill="#fff" stroke="#e2e5e8" stroke-width="1.5"/>'
s+='<line x1="120" y1="659" x2="1000" y2="659" stroke="#1b2430" stroke-width="1.4"/><text x="995" y="651" text-anchor="end" style="font-size:12.5px">Throat plate surface</text>'
def fy(x):
    v=math.sin(math.pi*(x-267)/512); return 659-(70 if v>0 else 27)*v
s+=f'<path d="{path([(x,fy(x)) for x in range(120,995,4)])}" fill="none" stroke="#2e9e5b" stroke-width="2.6"/>'
for x,c,ls in [(267,"#c8352b",["t1: feed dog","emerges, lifting","the material"]),(384,"#c8352b",["t3: set","moment"]),(524,"#5a6570",["t2: feed dog at its highest"])]:
    s+=f'<line x1="{x}" y1="450" x2="{x}" y2="689" stroke="{c}" stroke-width="1.3" stroke-dasharray="5 4"/>'+''.join(f'<text x="{x-6 if x==267 else x+6}" y="{462+i*17}" text-anchor="{"end" if x==267 else "start"}" style="fill:{c};font-weight:700;font-size:12.5px">{l}</text>' for i,l in enumerate(ls))
s+='<text x="120" y="719" style="font-size:13px">Main-shaft angle (illustrative)</text><text x="739" y="709" text-anchor="middle" style="fill:#1f8a4c;font-weight:700;font-size:13px">Feed-dog height</text>'
txt=["A company’s published patent (grant publication No. CN121496668B):","at moments t1 and t3 a thickness-sensing mechanism measures","the material thickness H1 and H3; the controller looks up an","adjusted stitch-length value from them and turns the stitch-length","motor to the corresponding angle, so that the stitch length does not","jump when the material gets thicker or thinner.","","The electronic feed and ply-dependent automatic presser-foot pressure","of Chapter 14 are the basis for this kind of “sense → adjust”."]
s+=''.join(f'<text x="1080" y="{470+24*i}" style="fill:#1b2430;font-size:14px">{t}</text>' for i,t in enumerate(txt))
render('fig_24_t9',page(1700,760,'Case T9: how a lockstitch machine adapts itself to different fabrics',
 'The sense → recognise → adjust loop (illustrative); below, a uniform-stitch-length control method from a published patent',f'<svg width="1700" height="760">{s}</svg>'))
