"""English version of fig_20_parts (Fig. 23-2): table, HTML."""
from en__lib_ch18_23 import page

rows = [('#c4531d', 'Rotary hook (hook body, bobbin-case holder)',
         'hook point sweeps past the needle at ten-odd m/s;<br>holder slides at high speed in the race', 'alloy steel',
         'carburised and quenched, or through-hardened; race<br>finish-ground, hook point lapped; DLC coating (low oil)'),
        ('#c4531d', 'Needle bar and needle-bar bushing',
         'reciprocates eighty or ninety times a second;<br>inertia forces of several hundred N at bottom dead centre',
         'bearing steel or alloy steel', 'quenched, finish-ground, hard-chrome plated;<br>hollow needle bar to save weight'),
        ('#2a5fb8', 'Main shaft, hook shaft, cranks', 'alternating bending and torsion', 'medium-carbon or alloy steel',
         'quench-and-temper, journals hardened then ground;<br>crank dynamically balanced with its counterweight'),
        ('#1b2430', 'Housing and bed', 'supports and locates all other parts;<br>its stiffness determines the vibration behaviour',
         'grey cast iron (or die-cast aluminium alloy)', 'aged to relieve internal stresses; key bores bored<br>on a machining centre in one setup'),
        ('#1f8a4c', 'Feed dog and throat plate', 'pushes the fabric; in contact with fabric and thread', 'alloy steel',
         'hardened, tooth form finish-machined;<br>needle-hole edge polished'),
        ('#7444b4', 'Timing belt and gears', 'keeps the upper and lower shafts exactly in step', 'rubber timing belt / steel gears',
         'pulley tooth accuracy, belt tension;<br>gears hardened and tooth-ground')]
tr = ''.join(f'<tr><td style="color:{c};font-weight:700;font-size:15.5px">{p}</td><td>{w}</td><td style="padding-top:22px">{m}</td><td>{k}</td></tr>'
             for c, p, w, m, k in rows)
body = f'''<p class="title">Key parts: working conditions determine materials and processes</p>
<p class="sub" style="margin-bottom:16px">Illustrative of common practice; specific material grades, hardnesses and processes follow the manufacturer’s drawings</p>
<style>.pt{{width:100%;font-size:14px;color:#1b2430}}.pt th{{font-size:15px;color:#5a6570;padding:22px 10px 14px;border-bottom:1px solid #d8dde1}}
.pt td{{height:96px;padding:12px 10px;line-height:1.6;border-bottom:1px solid #d8dde1}}.pt td:first-child{{padding-top:22px}}.pt tr:last-child td{{border-bottom:none}}</style>
<div class="card" style="padding:0 10px 18px">
<table class="pt"><colgroup><col style="width:21%"><col style="width:28%"><col style="width:20%"><col style="width:31%"></colgroup>
<tr><th>Part</th><th>Working conditions</th><th>Common materials</th><th>Key processes</th></tr>{tr}</table></div>
<p class="note" style="font-size:13.5px">DLC: diamond-like carbon coating. One manufacturer’s literature claims a surface hardness 86% higher than an ordinary hook and 33% less heat generation, with only very little oil needed.</p>'''
print(page('fig_20_parts', body))
