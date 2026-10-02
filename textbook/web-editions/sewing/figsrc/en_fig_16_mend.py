# Fig. 16-6 (English): thread break on one head — process flow and back-up along the stitch line
import sys; sys.path.insert(0, __file__.rsplit('/', 1)[0])
from en_c1314_lib import *
steps = [('o', '① Detect', 'Needle-thread encoder sees no pulses for several stitches: head k has a broken thread (some stitches already missed)'),
         ('b', '② Whole machine stops', 'Main shaft stops at the set position; indicator lamp of head k lights'),
         ('o', '③ Other heads trim', 'If the back-up is long, the unbroken heads trim first so they do not drag a long thread'),
         ('g', '④ Frame backs up', 'Runs backwards through the stitch data already sewn, past the missed stitches'),
         ('k', '⑤ Rethread', 'Operator rethreads head k (order relative to ④ depends on the model)'),
         ('y', '⑥ Single-head mending', 'Only head k drops its needle; the needle bars of the other heads are jumped and stay still'),
         ('b', '⑦ Whole machine resumes', 'Back at the break point, all heads embroider together')]
cells = []
for i, (c, t, d) in enumerate(steps):
    cells.append(f'<div class="box {c}" style="padding:10px 8px;min-height:116px{";border-color:#6b7682" if c=="k" else ""}"><b style="font-size:14px">{esc(t)}</b><span style="margin-top:6px;line-height:1.45">{esc(d)}</span></div>')
    if i < len(steps) - 1:
        cells.append('<div style="display:flex;align-items:center;justify-content:center"><svg width="18" height="16"><path d="M0 8H10" stroke="#5a6570" stroke-width="2"/><path d="M8 2L17 8L8 14z" fill="#5a6570"/></svg></div>')
flow = '<div style="display:grid;grid-template-columns:' + ' 18px '.join(['1fr'] * 7) + ';gap:2px;align-items:stretch">' + ''.join(cells) + '</div>'

# stitch line
x0, dx, n_done, d = 60, 26.2, 20, 5
stop = x0 + n_done * dx; brk = stop - d * dx
s = ['<svg width="1100" height="380" viewBox="0 0 1100 380" style="display:block">',
     '<defs><marker id="ag" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0L10,5L0,10z" fill="#5a6570"/></marker></defs>',
     f'<text x="{(brk+stop)/2}" y="30" font-size="12.5" font-weight="700" fill="#c8382a" text-anchor="middle">Stitches missed after the break (detection delay d)</text>',
     f'<rect x="{brk}" y="42" width="{stop-brk}" height="56" fill="#c8382a" opacity="0.12" rx="2"/>',
     f'<line x1="{x0}" y1="70" x2="{stop}" y2="70" stroke="#1b2430" stroke-width="1.6"/>',
     f'<line x1="{stop}" y1="70" x2="{x0+40*dx}" y2="70" stroke="#c9ced3" stroke-width="1.4" stroke-dasharray="5 4"/>']
s += [f'<circle cx="{x0+i*dx:.1f}" cy="70" r="4" fill="#1b2430"/>' for i in range(n_done + 1)]
s += [f'<circle cx="{x0+i*dx:.1f}" cy="70" r="4" fill="#d3d8dc"/>' for i in range(n_done + 1, 41)]
s += [f'<line x1="{brk}" y1="112" x2="{brk}" y2="134" stroke="#c8382a" stroke-width="1.6"/>',
      f'<line x1="{stop}" y1="112" x2="{stop}" y2="134" stroke="#2f6fd8" stroke-width="1.6"/>',
      f'<text x="{brk}" y="154" font-size="12.5" font-weight="700" fill="#c8382a" text-anchor="middle">Actual break</text>',
      f'<text x="{stop}" y="154" font-size="12.5" font-weight="700" fill="#2f6fd8" text-anchor="middle">Stop point</text>',
      f'<text x="{(brk+stop)/2 - 20}" y="180" font-size="12.5" font-weight="700" fill="#2e9e5b" text-anchor="middle">Back up b stitches (b larger than d: 2–3 stitches of overlap)</text>',
      f'<line x1="{stop}" y1="198" x2="{brk - 2*dx}" y2="198" stroke="#2e9e5b" stroke-width="2.4"/>',
      f'<path d="M{brk-2*dx-12} 198l14 -8v16z" fill="#5a6570"/>',
      f'<line x1="{brk-2*dx}" y1="228" x2="{stop-2}" y2="228" stroke="#b07a12" stroke-width="2.4"/>',
      f'<path d="M{stop+2} 228l-14 -8v16z" fill="#5a6570"/>',
      f'<text x="{(brk-2*dx+stop)/2}" y="258" font-size="12.5" font-weight="700" fill="#b07a12" text-anchor="middle">Broken head mends on its own up to the stop point</text>',
      '</svg>']
panel = f'''<div style="border:1.2px solid #e3e6e9;border-radius:10px;background:#fff;padding:16px 20px 14px;margin-top:34px">
<p style="font-size:14.5px;font-weight:700;margin:0 0 10px">Along the stitch line: detection delay and back-up count</p>
<div style="margin-top:22px">{''.join(s)}</div>
<p style="font-size:13px;margin:-90px 0 0">If the back-up count is smaller than the detection delay (b less than d), the mending does not join up and a stretch of missed stitches remains; backing up too far wastes time and thickens the overlap. The faster the detection (the smaller d), the less back-up is needed.</p></div>'''
body = f'''<p class="title">A thread break on one head: whole machine stops, frame backs up, broken head mends on its own</p>
<p class="sub">Compiled from patent descriptions of thread-break handling on multi-head embroidery machines (process schematic)</p>
<div style="margin-top:26px">{flow}</div>{panel}'''
render('fig_16_mend', body, width=1200)
