# Small helpers shared by the en_fig_23_* / en_fig_24_* generators (English figures, Chapters 30-31)
import os, subprocess
H=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.dirname(H)
CSS='''<!doctype html><meta charset="utf-8"><link rel="stylesheet" href="../fig_base.css">
<style>.fig{padding:0;position:relative}.title{position:absolute;left:40px;top:24px;font-size:27px}.sub{position:absolute;left:40px;top:66px;font-size:16.5px}
.ab{position:absolute}.foot{position:absolute;left:40px;font-size:15px}
svg{position:absolute;left:0;top:0;overflow:visible} svg text{font-size:14px;fill:#5a6570;font-family:QFix,"Noto Sans CJK SC",sans-serif}
.card{position:absolute;background:#fff;border:1.5px solid #e2e5e8;border-radius:8px}
</style>'''
def render(name,html):
    p=os.path.join(H,f'en_{name}.en.html'); open(p,'w').write(html)
    subprocess.run(['node','fig.js',f'figsrc/en_{name}.en.html',f'img/en/{name}.png'],cwd=ROOT,check=True)
def page(w,h,title,sub,inner):
    return CSS+f'<div class="fig" style="--w:{w}px;width:{w}px;height:{h}px"><p class="title">{title}</p><p class="sub">{sub}</p>{inner}</div>'
def path(pts):
    return 'M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pts)
def frame(x0,y0,x1,y1,pad=12):
    return f'<rect x="{x0-pad}" y="{y0-pad}" width="{x1-x0+2*pad}" height="{y1-y0+2*pad}" rx="7" fill="#fff" stroke="#e2e5e8" stroke-width="1.5"/>'
