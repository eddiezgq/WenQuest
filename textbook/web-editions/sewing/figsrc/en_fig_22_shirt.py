# Generates en_fig_22_shirt.en.html (English version of fig_22_shirt) and renders it
import subprocess, os
H=os.path.dirname(os.path.abspath(__file__))
cards=[("Collar","3.62","10 operations",["Sew collar · trim · turn · press","Attach collar to stand"],["Automatic collar sewing &amp; trimming","Collar press"],2),
("Cuffs","3.85","7 operations",["Binding · hemming · sew cuff","Trim · turn and press"],["Automatic cuff unit","Cuff forming press"],2),
("Plackets","2.21","3 operations",["Attach placket · bartack · pleat"],["Automatic placket unit"],1),
("Fronts","4.22","9 operations",["Front placket · press, attach pocket","Label · pleats"],["Placket machine","Automatic pocket setter"],2),
("Back","0.84","2 operations",["Attach yoke · topstitch"],[],0)]
ys=[130,274,417,560,703]
out=[]
for (n,m,o,ops,au,k),y in zip(cards,ys):
    sq=''.join(f'<i class="{"on" if i<k else ""}"></i>' for i in range(6))
    out.append(f'''<div class="card" style="top:{y}px"><b>{n}</b><div class="mn">{m} min</div><div class="ops">{o}</div>
<div class="lst">{'<br>'.join(ops)}</div><div class="sq">{sq}</div><div class="au">{''.join(f"<div>■ {a}</div>" for a in au)}</div></div>''')
lines=''.join(f'<line x1="1122" y1="{y+64}" x2="1197" y2="480"/>' for y in ys)
dash=''.join(f'<line x1="262" y1="480" x2="296" y2="{y+64}"/>' for y in ys)
asm=["Join shoulders, topstitch","Attach collar","Close collar (insert size label)","Set sleeves, topstitch armhole","Close side and sleeve seams","Attach cuffs, topstitch","Hem bottom"]
post=[("Buttonholes (placket, cuffs)",1),("Buttons",1),("Thread trimming",0),("Pressing",0),("Folding, packing",0),("Inspection",0)]
seg=[("Collar 16%",3.62,"#2a6fdb"),("Cuffs 17%",3.85,"#2a6fdb"),("Plackets 10%",2.21,"#2a6fdb"),("Fronts 19%",4.22,"#7ea6e8"),("",0.84,"#a9c3ef"),("Assembly 34%",7.58,"#1b2430")]
html=f'''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">
<style>
.fig{{padding:0;position:relative;height:1000px}}
.title{{position:absolute;left:40px;top:24px;font-size:27px}}
.sub{{position:absolute;left:40px;top:66px;font-size:16.5px;width:1720px}}
.pan{{position:absolute;top:130px;height:700px;border-radius:8px;background:#f1f2f3;border:1.5px solid #e2e5e8;text-align:center}}
.card{{position:absolute;left:300px;width:820px;height:128px;background:#fff;border:1.5px solid #e2e5e8;border-radius:8px}}
.card b{{position:absolute;left:24px;top:14px;font-size:22px;color:#2a5fb8}}
.card .mn{{position:absolute;left:24px;top:52px;font-size:21px;font-weight:700}}
.card .ops{{position:absolute;left:24px;top:90px;font-size:14.5px;color:#5a6570}}
.card .lst{{position:absolute;left:170px;top:20px;font-size:15px;line-height:1.65;width:300px}}
.card .sq{{position:absolute;left:170px;top:86px;display:flex;gap:8px}}
.card .sq i{{width:36px;height:24px;border-radius:4px;background:#e6e8ea;border:1px solid #c8cdd2}}
.card .sq i.on{{background:#c9a227;border-color:#b08d1e}}
.card .au{{position:absolute;left:480px;top:20px;font-size:15px;line-height:1.75;font-weight:700;color:#8a6a10}}
.asm{{left:1200px;width:300px;background:#eef3fc;border:2.5px solid #2a6fdb}}
.asm h3{{margin:20px 0 4px;font-size:23px;color:#2a5fb8}}.asm p{{margin:0 0 18px;font-weight:700;font-size:16.5px}}
.st{{background:#fff;border:1.5px solid #e2e5e8;border-radius:6px;margin:0 30px;height:56px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15.5px;line-height:1.25;padding:0 6px}}
.dn{{height:24px;position:relative}}.dn:before{{content:"";position:absolute;left:50%;top:3px;height:12px;border-left:1.5px solid #5a6570}}.dn:after{{content:"";position:absolute;left:calc(50% - 5px);top:14px;border-top:8px solid #5a6570;border-left:5px solid transparent;border-right:5px solid transparent}}
.pst{{left:1540px;width:220px}} .pst h3{{margin:20px 0 22px;font-size:21px}}
.pst .st{{margin:0 20px;height:60px}} .pst .st.g{{border:2.5px solid #c9a227}} .pst .dn{{height:36px}}.pst .dn:before{{top:6px;height:20px}}.pst .dn:after{{top:25px}}
.cut h3{{margin:20px 0 14px;font-size:21px}} .cut p{{font-size:15px;color:#5a6570;margin:0 0 18px;line-height:1.55}}
svg{{position:absolute;left:0;top:0}}
.bar{{position:absolute;left:300px;top:880px;width:1198px;height:40px;display:flex;gap:2px}}
.bar div{{color:#fff;font-weight:700;font-size:15.5px;display:flex;align-items:center;justify-content:center;border-radius:2px}}
</style>
<div class="fig" style="--w:1800px">
<p class="title">Shirt floor: five parts lines feed the assembly line</p>
<p class="sub">Numbers in the boxes = standard minutes of that section (min/piece, summed from a public 41-operation breakdown), 22.3 min in total; coloured squares = machine positions that can use automatic units</p>
<svg width="1800" height="1000"><defs><marker id="m" markerWidth="10" markerHeight="10" refX="9" refY="5" orient="auto"><path d="M0,1 L9,5 L0,9z" fill="#5a6570"/></marker></defs>
<g stroke="#5a6570" stroke-width="1.6">{lines}</g><circle cx="1196" cy="480" r="5" fill="#5a6570"/>
<g stroke="#5a6570" stroke-width="1.3" stroke-dasharray="4 4" marker-end="url(#m)">{dash}</g>
<line x1="1502" y1="480" x2="1536" y2="480" stroke="#5a6570" stroke-width="2" marker-end="url(#m)"/></svg>
<div class="pan cut" style="left:40px;width:220px"><h3>Cutting, fusing</h3><p>Spreading, cutting<br>Continuous fusing press<br>(collar, cuffs, plackets<br>fused)</p><p>Panels bundled<br>and sent to<br>each parts line</p></div>
{''.join(out)}
<div class="pan asm"><h3>Assembly line</h3><p>7.58 min · 10 operations</p>{'<div class="dn"></div>'.join(f'<div class="st">{a}</div>' for a in asm)}</div>
<div class="pan pst"><h3>Finishing</h3>{'<div class="dn"></div>'.join(f'<div class="st{" g" if g else ""}">{a}</div>' for a,g in post)}
<div style="font-size:13.5px;color:#8a6a10;margin-top:16px;padding:0 10px">Buttonholing and button sewing often use automatic feeders</div></div>
<div style="position:absolute;left:300px;top:845px;font-size:18px;font-weight:700">Work content: the three small parts — collar, cuffs, plackets — take 43%, all parts 66%, assembly only 34%</div>
<div class="bar">{''.join(f'<div style="flex:{w};background:{c}">{t}</div>' for t,w,c in seg)}</div>
<div style="position:absolute;left:967px;top:928px;width:200px;text-align:center;font-size:14.5px;font-weight:700">Back 4%</div>
</div>'''
open(os.path.join(H,'en_fig_22_shirt.en.html'),'w').write(html)
subprocess.run(['node','fig.js','figsrc/en_fig_22_shirt.en.html','img/en/fig_22_shirt.png'],cwd=os.path.dirname(H),check=True)
