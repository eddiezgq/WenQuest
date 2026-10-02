"""English version of fig_19_mes (Fig. 26-7): data flow between ERP, MES, hanger system, machines and the digital twin."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from en__lib_ch26_28 import *

S = []
S.append(sbox(70, 165, 307, 118, 'k', 'ERP', ['Orders, materials, costs', 'Piece-rate pay']))
S.append(sbox(70, 388, 307, 130, 'b', 'MES', ['Splits work orders into operations', 'Dispatches to lines and workstations', 'Collects production reports']))
S.append(sbox(70, 635, 307, 130, 'g', 'Hanger system / work tickets', ['Carrier IDs, bundle numbers', 'Which operation each piece has reached']))
S.append('<rect x="553" y="165" width="142" height="658" rx="12" fill="#e9f0fc" stroke="#2a6fdb" stroke-width="2"/>')
S.append(stext(624, 494, 'Unified data bus', 20, '#2a5fb8', 700, 'middle', 'transform="rotate(-90 624 494)" dominant-baseline="middle"'))
S.append(sbox(823, 165, 307, 118, 'p', 'Dashboard', ['State and piece count of every machine', 'Stop reasons']))
S.append(sbox(823, 388, 307, 130, 's', 'Historian', ['Archives every message', 'Metrics are computed here']))
S.append(sbox(823, 635, 307, 130, 'o', 'Sewing machines (hundreds)', ['State, counts, events', 'Per-minute summary + immediate state']))
S.append(sbox(1247, 165, 706, 600, 'p', 'Digital twin', [], ts=20, anchor='start', tx=1270, ty=203))
S.append(sbox(1282, 236, 635, 141, 'p', '① Real-time mirror', ['Every sewing machine, workstation and hanger carrier has a virtual counterpart',
                                                           'whose state follows the bus messages (dashboard, 3D shop floor)']))
S.append(sbox(1282, 412, 635, 141, 'p', '② Simulation and prediction', ['Starting from the current state, “fast-forward” a few hours: which operation will',
                                                                     'block, which order will be late; models from the simulations of Chapters 12 and 29,',
                                                                     'with parameters from measured times and efficiencies']))
S.append(sbox(1282, 588, 635, 142, 'p', '③ Try options, then release', ['Add a person, change the dispatching rule, re-sequence operations, compare results',
                                                                     'The chosen option is released to the shop floor through MES']))
for y in (223, 453, 700):
    S.append(sline([(380, y), (551, y)], '#3d4752'))
    S.append(sline([(551, y + 17), (380, y + 17)], '#3d4752'))
S.append(sline([(697, 223), (821, 223)], '#3d4752'))
S.append(sline([(697, 453), (821, 453)], '#3d4752'))
S.append(sline([(821, 700), (697, 700)], '#e0662f', 2.5))
S.append(sline([(1132, 223), (1280, 305)], '#8a5cc7'))
S.append(sline([(1132, 453), (1280, 482)], '#5a6570'))
S.append(sline([(1600, 732), (1600, 847), (35, 847), (35, 453), (68, 453)], '#8a5cc7', 2, True, '7 5'))
S.append(stext(913, 873, 'Adjusted plan goes back to MES (released after human confirmation)', 15, '#7444b4', 700, 'middle'))

print(svg_page('fig_19_mes', 'How orders, operations, machine data and the digital twin are connected',
               'Illustrative; every system talks only to the unified data bus (the WenQuest Digital Factory approach)',
               '\n'.join(S), (25, 155, 1940, 735),
               'A simulated sewing machine and a real one send messages in the same format; only the source field differs. To replace the simulation with real equipment, just connect it to the bus — nothing else has to change.'))
