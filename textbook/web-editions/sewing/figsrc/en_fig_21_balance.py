"""English version of fig_21_balance (Fig. 28-5): line-balance charts. Groups computed by the lab's own code
(src/zh/labs/line21.html, see en_c2628/line_model.js)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

D = load_line(); by = D['by0']
g1 = [(g['ops'], g['k']) for g in D['one0']['gs']]
g2 = [(g['ops'], g['k']) for g in D['dp0']['gs']]
fig = panel_fig(1120, 350)
draw_balance(fig, [0.055, 0.11, 0.42, 0.72], 'One operation per group (k = ⌈time ÷ takt⌉)', g1, by)
draw_balance(fig, [0.565, 0.11, 0.42, 0.72], 'Adjacent operations share groups (dynamic programming)', g2, by)
p = save_panel(fig, 'balance.png')
body = f'''<p class="title">Line-balance charts: one operation per group versus shared groups of adjacent operations</p>
<p class="sub">Target 120 pcs/h, takt 0.5 min; bar width proportional to the number of operators, bar height is the load per operator; colours indicate machine type</p>
<img class="pimg" src="{p}">
{legend_html()}
<p class="note" style="margin-top:16px">With one operation per group, even a 0.55 min operation needs 2 operators, who wait half of the time; sharing groups cuts the line from 38 to 29 operators (theoretical minimum 27).</p>'''
print(page('fig_21_balance', body))
