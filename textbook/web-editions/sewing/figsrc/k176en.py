import subprocess
mot={4:'000001100000',5:'000011110000',6:'000111111000',7:'000011110000',8:'000001100000'}
rib='110011001100'
cs=46;cells=''
for r in range(8,0,-1):
    row=f'<th style="border:none;font-weight:400;color:#5a6570;padding-right:10px">{r}</th>'
    for i in range(12):
        if r<=3: c='#4a8bdb' if rib[i]=='1' else '#deddd5'
        else: c='#f08452' if mot[r][i]=='1' else '#eeeeee'
        row+=f'<td style="width:{cs}px;height:{cs}px;background:{c};border-radius:4px"></td>'
    cells+=f'<tr>{row}</tr>'
cells+='<tr><th></th>'+''.join(f'<td style="text-align:center;color:#5a6570;font-size:13px">{i}</td>' for i in range(1,13))+'</tr>'
leg=lambda c,t:f'<span style="display:inline-flex;align-items:center;gap:8px;margin-right:28px"><i style="width:22px;height:22px;background:{c};border-radius:4px;display:inline-block;border:1px solid #ccc"></i>{t}</span>'
html=f'''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css"><style>.nb th,.nb td{{border:none!important}}</style>
<div class="fig" style="--w:1060px"><p class="title">Each cell of the pattern chart is one needle's action in one row; the compiler splits it into course-by-course selection data</p>
<p class="sub">12 needles × 8 rows example: bottom 3 rows 2×2 rib, top 5 rows two-colour jacquard (diamond); the chart is read from the bottom up, row 1 is knitted first</p>
<div style="margin:0 0 16px 40px">{leg('#4a8bdb','Front bed knits')}{leg('#deddd5','Back bed knits')}{leg('#f08452','Motif (carrier 2)')}{leg('#eeeeee','Ground (carrier 1)')}</div>
<div style="display:flex;gap:30px;align-items:center"><table style="border-collapse:separate;border-spacing:5px" class="nb">{cells}</table>
<div class="box" style="text-align:left;padding:16px 18px;width:330px"><b style="color:#1b2430">Chart row 4 → two courses</b>
<p style="margin:10px 0 2px">Course a (→), carrier 1, front-bed selection:</p><p class="mono" style="margin:0">111110011111</p>
<p style="margin:10px 0 2px">Course b (←), carrier 2, front-bed selection:</p><p class="mono" style="margin:0;color:#c4531d">000001100000</p>
<p style="font-size:12.5px;color:#5a6570;margin-top:12px">1 = knit, 0 = miss; the two courses' selections are complementary. Stitch cam, speed, take-down and back-bed backing are assigned separately.</p></div></div>
<p class="note">One chart row of a two-colour jacquard takes two courses (one per colour); the yarn that does not knit floats on the back or is held by the back-bed backing structure.</p></div>'''
open('k176b.en.html','w').write(html)
subprocess.run(['node','../fig.js','k176b.en.html','../img/en/w_b834f1c3.png'],check=True)
