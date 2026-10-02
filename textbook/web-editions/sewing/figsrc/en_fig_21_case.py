"""English version of fig_21_case (Fig. 28-7): balance improvement of a casual-trousers line.
Before: one operation per group with staffing digitised from the original (26 operators, cycle 0.70);
step 1: lab's dynamic-programming grouping at takt 0.55 (src/zh/labs/line21.html);
step 2: special machines for ops 3 and 17, grouping as in the original figure (26 operators, 91.9%)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

D = load_line(); by0 = D['by0']; by1 = D['by1']
K = {3: 2, 7: 2, 13: 2, 17: 2}
before = [([i], K.get(i, 1)) for i in range(1, 21)] + [([21, 22], 1), ([23], 1)]
step1 = [(g['ops'], g['k']) for g in D['dp055_0']['gs']]
step2 = [([6, 1], 2), ([2, 3], 2), ([9, 10, 7], 4), ([4, 11, 5, 8], 4), ([12, 13, 14], 4), ([15, 16], 2), ([17], 2),
         ([18, 19, 20], 4), ([21, 22, 23], 2)]
fig = panel_fig(1120, 350)
w = 0.27
draw_balance(fig, [0.055, 0.11, w, 0.72], 'Before: by experience, one op per group', before, by0)
draw_balance(fig, [0.385, 0.11, w, 0.72], 'Step 1: regroup (same machines)', step1, by0)
draw_balance(fig, [0.715, 0.11, w, 0.72], 'Step 2: special machines for 2 ops', step2, by1)
p = save_panel(fig, 'case.png')
body = f'''<p class="title">Case: improving the balance of a casual-trousers line (26 operators, target 120 pcs/h)</p>
<p class="sub">Generic case written from first principles, worked-example values; output is the theoretical value from standard minutes</p>
<img class="pimg" src="{p}">
{legend_html([('Special machine', B_RED)])}
<p class="note" style="margin-top:16px">Before improvement the bottlenecks are setting the zip and closing the inseam (0.70 min each, 1 operator each), so the line can make only 85.7 pcs/h; after regrouping, 109.1 pcs/h.<br>
Switching the two most time-consuming operations (back welt pockets, attaching the waistband) to special machines brings 26 operators to 120 pcs/h. Reaching 120 pcs/h with unchanged equipment needs 29 operators.</p>'''
print(page('fig_21_case', body))
