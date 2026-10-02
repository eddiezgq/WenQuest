# English fig_24_map (chapter refs updated: 19->26, 21->28, 23->30)
from en_svgkit import *
cols=[("Perception","#2a6fdb","#2a5fb8","#dfe6f2",["Camera images, sensor signals","Vision inspection, fabric recognition,<br>edge tracking (Ch. 30)","Lighting, style changes, new defects:<br>what it has not seen, it cannot recognise"]),
("Prediction","#2e9e5b","#1f8a4c","#dcece1",["Historical orders, equipment data<br>(Ch. 26)","Demand forecasts, delivery forecasts,<br>early warning of equipment failure","Too little data or changed conditions,<br>and the forecast drifts"]),
("Optimisation and generation","#e0662f","#c4531d","#f6e4da",["Patterns, orders, work content<br>(Ch. 28)","Marker making, scheduling, dispatching;<br>design drawings, pattern-making","Set the wrong objective and the better it<br>solves, the further off it gets; copyright"]),
("Language assistants","#8a5cc7","#7444b4","#ebe1ef",["Documents, manuals,<br>data on the data bus","Q&amp;A, drafting documents,<br>training, briefings","Fluent is not the same as correct:<br>cite sources, preview before confirming"])]
lab=["Data","Use","Where it goes wrong"]
b=''
for n,c,tc,f,items in cols:
    b+=f'<div><div class="hd" style="background:{f};color:{tc}">{n}</div>'+''.join(f'<div class="cd" style="border-color:{c}"><small>{lab[i]}</small><span>{t}</span></div>' for i,t in enumerate(items))+'</div>'
inner=f'''<style>.g{{position:absolute;left:40px;top:120px;width:1620px;display:grid;grid-template-columns:repeat(4,1fr);gap:20px}}
.hd{{height:70px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:23px;font-weight:700;margin-bottom:30px}}
.cd{{height:150px;border:2px solid;border-radius:8px;background:#fff;margin-bottom:20px;position:relative;display:flex;align-items:center;justify-content:center;text-align:center;font-size:15.5px;line-height:1.6;padding-top:12px}}
.cd small{{position:absolute;left:18px;top:14px;font-size:13.5px;font-weight:700;color:#5a6570}}</style>
<div class="g">{b}</div><p class="foot" style="top:712px">Whatever the type, AI has to be judged by shop-floor numbers: how many defects missed, how many false alarms, how many days of warning, how many labour hours saved.</p>'''
render('fig_24_map',page(1700,760,'What AI does in apparel making: four types of application, the data each uses, and where each goes wrong',
 'Illustrative; numbers in parentheses are chapters of this book',inner))
