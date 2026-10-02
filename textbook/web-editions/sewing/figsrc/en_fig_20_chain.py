"""English version of fig_20_chain (Fig. 23-3): HTML + inline SVG."""
from en__lib_ch18_23 import page
from en__svg import *

s = []
s.append('<rect x="47" y="142" width="893" height="751" rx="14" fill="#fff" stroke="#d8dde1" stroke-width="1.6"/>')
s.append('<rect x="1012" y="142" width="940" height="751" rx="14" fill="#fff" stroke="#d8dde1" stroke-width="1.6"/>')
# left drawing
s.append('<rect x="94" y="188" width="800" height="82" rx="6" fill="#e9ecf0" stroke="#5a6570" stroke-width="1.8"/>')
s.append(text(118, 236, 'Housing (arm)', 16, MUTED, 700))
s.append('<rect x="294" y="262" width="58" height="138" rx="3" fill="#eef0f2" stroke="#9aa4ae" stroke-width="1.4"/>')
s.append('<rect x="308" y="258" width="30" height="377" rx="4" fill="#cdd2d8" stroke="#1b2430" stroke-width="1.8"/>')
s.append(text(376, 318, 'Needle-bar bushing', 15, MUTED))
s.append(text(376, 389, 'Needle bar', 15, MUTED))
s.append('<rect x="300" y="635" width="46" height="47" rx="4" fill="#d5dade" stroke="#1b2430" stroke-width="1.8"/>')
s.append(text(288, 665, 'Needle clamp', 15, MUTED, 400, 'end'))
s.append('<rect x="318" y="682" width="10" height="130" rx="2" fill="#6b7580" stroke="#1b2430" stroke-width="1.2"/>')
s.append(text(300, 801, 'Needle', 15, MUTED, 400, 'end'))
s.append('<rect x="94" y="824" width="800" height="46" rx="6" fill="#e9ecf0" stroke="#5a6570" stroke-width="1.8"/>')
s.append('<rect x="523" y="812" width="59" height="23" rx="4" fill="#e3e7ea" stroke="#5a6570" stroke-width="1.4"/>')
s.append('<circle cx="553" cy="706" r="105" fill="#f3f5f6" stroke="#1b2430" stroke-width="2"/>')
s.append('<circle cx="553" cy="706" r="10" fill="#1b2430"/>')
s.append(text(553, 753, 'Rotary hook', 16, INK, 700, 'middle'))
s.append('<polygon points="332,752 449,726 452,745" fill="#e0662f"/>')
s.append(text(400, 706, 'Hook point', 15, '#c4531d', 700, 'middle'))
s.append(text(118, 856, 'Bed', 16, MUTED, 700))
s.append(text(630, 856, 'Hook-shaft bore', 15, MUTED, 400, 'middle'))
s.append(text(112, 724, 'Clearance 0.04–0.10 mm', 16, '#c4372b', 700))
s.append(arrow(282, 736, 314, 752, '#c4372b', 1.6))
# right table
s.append(text(1036, 183, 'Links of the dimensional chain (tolerances, illustrative)', 19, INK, 700))
GA, GT = '#e3f3e8', '#1f8a4c'; OA, OT = '#fbe5da', '#c4531d'; KA, KT = '#e3e6e9', '#1b2430'
rows = [(GA, GT, 'Needle-bar bushing bore position', '±0.030 mm', 'absorbed by adjustment'),
        (KA, KT, 'Needle bar–bushing play', '±0.008 mm', 'not absorbable'),
        (GA, GT, 'Needle-clamp hole offset', '±0.020 mm', 'absorbed by adjustment'),
        (OA, OT, 'Needle scarf-face dimension', '±0.020 mm', 'absorbed; returns after a needle change'),
        (OA, OT, 'Needle twist as fitted', '±0.015 mm', 'absorbed; returns after a needle change'),
        (GA, GT, 'Hook-shaft bore position', '±0.030 mm', 'absorbed by adjustment'),
        (GA, GT, 'Hook point to mounting datum', '±0.020 mm', 'absorbed by adjustment'),
        (KA, KT, 'Hook-shaft radial play', '±0.010 mm', 'not absorbable')]
for k, (bg, tc, n, tol, st) in enumerate(rows):
    y = 254 + 73 * k
    s.append(f'<rect x="1036" y="{y-18}" width="34" height="36" rx="6" fill="{bg}"/>')
    s.append(text(1053, y + 6, str(k + 1), 16, tc, 700, 'middle'))
    s.append(text(1094, y + 6, n, 17, INK, 700))
    s.append(text(1450, y + 6, tol, 17, INK))
    s.append(text(1590, y + 6, st, 14.5, tc, 700))
s.append(text(1036, 836, 'Worst case: sum of link tolerances = ±0.153 mm; statistical (±3σ): ±0.058 mm', 16, INK, 700))
s.append(text(1036, 863, 'Permitted range only ±0.03 mm (0.04–0.10 mm)', 16, INK, 700))

body = f'''<p class="title">The dimensional chain of the hook-point clearance: eight links joined end to end</p>
<p class="sub">Illustrative (dimensions exaggerated); tolerances are illustrative values; green links can be absorbed by adjustment during assembly, orange links are absorbed by the adjustment but come back when the needle is changed</p>
{svg(40, 135, 1920, 765, ''.join(s))}'''
print(page('fig_20_chain', body))
