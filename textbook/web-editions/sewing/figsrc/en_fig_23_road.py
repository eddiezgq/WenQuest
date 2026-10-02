# English version of fig_23_road (chapter refs updated: 12,22->12,29; 19->26; 24->31; 23.6->30.6)
import subprocess, os
H=os.path.dirname(os.path.abspath(__file__))
cols=[("More economical","#2e9e5b","#dcece1",[("Clutch motor → servo → direct drive","Widespread (Ch. 13)",.9),("Low-oil and oil-free lubrication","Widespread (Ch. 5, 8)",.6),("Electronic feed, tension, presser foot","Spreading (Ch. 14)",.3)]),
("Smarter","#2a6fdb","#dfe6f2",[("Single-machine automation: pattern sewers, template machines","Mature (Ch. 11, 15)",.9),("Networking, MES, digital twins","Being adopted (Ch. 26)",.6),("Automatic parameter setting by fabric (AI)","Early stage (Ch. 31)",.3)]),
("Fewer people","#e0662f","#f6e4da",[("Automatic units + hanger systems","Mature (Ch. 12, 29)",.9),("Sewing robots","Demonstration lines, not yet at scale",.6),("Humanoid robots","Single-operation trials (2026)",.3)]),
("No sewing","#8a5cc7","#ebe1ef",[("Whole-garment knitting","Used in sweaters (Ch. 17)",.9),("Ultrasonic welding, heat bonding","Used in sportswear and underwear",.6),("Related: digital printing, green manufacturing","Section 30.6",.3)])]
body=''
for n,c,f,cards in cols:
    body+=f'<div class="col"><div class="hd" style="background:{f};color:{c}">{n}</div>'
    for t,s,p in cards:
        body+=f'<div class="cd" style="border-color:{c}"><b>{t}</b><span>{s}</span><div class="bar"><i style="width:{p*100:.0f}%;background:{c}"></i></div></div>'
    body+='</div>'
html=f'''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">
<style>.fig{{padding:24px 40px 0;height:780px;position:relative}}.title{{font-size:27px}}.sub{{font-size:16.5px;margin-bottom:22px}}
.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:20px}}
.hd{{height:70px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:23px;font-weight:700;margin-bottom:30px}}
.cd{{height:120px;border:2px solid;border-radius:8px;background:#fff;margin-bottom:30px;padding:16px 20px;position:relative}}
.cd b{{display:block;font-size:16.5px;line-height:1.3}}.cd span{{display:block;font-size:15px;color:#5a6570;margin-top:8px}}
.bar{{position:absolute;right:20px;bottom:14px;width:100px;height:9px;border-radius:5px;background:#d8dce0;overflow:hidden}}.bar i{{display:block;height:100%;border-radius:5px}}
.foot{{position:absolute;left:40px;bottom:22px;font-size:15px}}</style>
<div class="fig" style="--w:1700px"><p class="title">Directions of development for sewing equipment: which have matured, and which are still at the threshold</p>
<p class="sub">Illustrative; numbers in parentheses are chapters or sections of this book</p><div class="grid">{body}</div>
<p class="foot">The bar at the bottom right of each card shows maturity (illustrative): in each column, the lower the card, the newer and less mature. The “fewer people” column is held back most by the softness of cloth and by payback on investment.</p></div>'''
open(os.path.join(H,'en_fig_23_road.en.html'),'w').write(html)
subprocess.run(['node','fig.js','figsrc/en_fig_23_road.en.html','img/en/fig_23_road.png'],cwd=os.path.dirname(H),check=True)
