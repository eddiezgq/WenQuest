"""English version of fig_19_mqtt (Fig. 26-3): MQTT publish/subscribe and the topic tree."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

S = []
S.append('<rect x="47" y="142" width="1011" height="751" rx="12" fill="#fff" stroke="#d8dde1" stroke-width="1.5"/>')
S.append('<rect x="1130" y="142" width="823" height="751" rx="12" fill="#fff" stroke="#d8dde1" stroke-width="1.5"/>')
S.append(stext(70, 179, 'a    Publish and subscribe', 19, INK, 700))
S.append(stext(1153, 179, 'b    Unified namespace (topic tree)', 19, INK, 700))
ys = [236, 377, 518, 659]
for i, y in enumerate(ys):
    S.append(sbox(82, y, 236, 93, 'o', f'Sewing machine l03-0{5 + i}', ['publishes status, event, counter'], ts=17, ls=13.5, ty=y + 33))
    S.append(sline([(318, y + 47), (441, 505)], ORANGE, 2, False))
S.append('<path d="M441,505 l-10,-12 l3,12 l-3,12z" fill="#5a6570"/>')
S.append(sbox(447, 423, 235, 165, 'b', 'MQTT broker', ['Forwards by topic', 'Retained messages:', 'only the latest is kept'], ts=19, ls=13.5, fill='#e9f0fc', ty=461))
subs = [('Shop-floor dashboard', 'subscribes wq/shirt/sewing/+/status'), ('Historian', 'subscribes wq/shirt/#'),
        ('MES bridge', 'subscribes …/+/counter'), ('Remote maintenance', 'subscribes …/+/event (faults)')]
for (t, l), y in zip(subs, ys):
    S.append(sbox(764, y, 271, 93, 'p', t, [l], ts=17, ls=13.5, ty=y + 33))
    S.append(sline([(685, 505), (762, y + 47)], PURPLE, 2))
for i, t in enumerate(['QoS 1: at least once; the receiver de-duplicates by the id in the message',
                       'Retained message: a new dashboard gets the current state of every machine as soon as it connects',
                       'Last will: if a device drops off, the broker publishes “offline” for it after the heartbeat times out']):
    S.append(stext(70, 811 + 26 * i, t, 14.5, INK))

tree = [(0, 'wq', '', INK, 700), (1, 'shirt', ' (shirt factory)', INK, 700), (2, 'cutting', ' (cutting room)', MUTED, 600),
        (2, 'sewing', ' (sewing room)', '#2a6fdb', 600), (3, 'l03-07', ' (line 3, workstation 7)', ORANGE, 600),
        (4, 'status', '    retained; run / idle / down / fault / offline', ORANGE, 400),
        (4, 'event', '    start, stop, thread break, alarm, operator change', ORANGE, 400),
        (4, 'counter', '    shift totals every minute: pieces, stitches, trims, run seconds', ORANGE, 400),
        (4, 'cmd', '    parameters, style change (only MES may write)', RED, 400),
        (3, 'l03-08 …', '', MUTED, 600), (3, 'hanger', ' (hanger system)', GREEN, 700),
        (2, 'finishing', ' (finishing)', MUTED, 600), (2, 'office/erp', ' (ERP documents)', MUTED, 600)]
for i, (lv, a, b, c, wgt) in enumerate(tree):
    x = 1177 + 47 * lv; y = 236 + 47 * i
    if lv:
        S.append(f'<path d="M{x - 30},{y - 24} V{y - 6} H{x - 8}" fill="none" stroke="#9aa4ae" stroke-width="1.3"/>')
    S.append(f'<text x="{x}" y="{y}" font-size="17" fill="{c}"><tspan font-weight="{max(wgt, 600) if lv < 4 else 400}">{a}</tspan>'
             f'<tspan font-weight="{wgt if lv < 4 else 400}" font-size="{17 if lv < 4 else 15.5}">{b}</tspan></text>')
S.append(stext(1153, 864, 'Example: wq/shirt/sewing/l03-07/status', 17, '#2a6fdb', 700))

print(svg_page('fig_19_mqtt', 'MQTT: devices publish, applications subscribe; topics named by factory hierarchy',
               'Illustrative; topic format follows the WenQuest Digital Factory unified data bus (wq/factory/area/cell/category)',
               '\n'.join(S), (40, 135, 1920, 765)))
