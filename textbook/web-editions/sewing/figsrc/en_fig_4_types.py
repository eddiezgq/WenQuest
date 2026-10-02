from en_relabel import *
N = 'fig_4_types'
im = load(N)
K = (31, 42, 54); G = (93, 107, 122); W = (255, 255, 255)
header(im, 'Four basic forms of take-up mechanism',
       'Schematic; blue: needle thread; purple: take-up lever or take-up part; grey: driving part on the main shaft')
T = dict(size=36, color=K, bold=True, mode='c', ecolor=W)
rep(im, B(112, 165, 300, 196), 'Cam type', at=P(115, 180), **T)
rep(im, B(1090, 165, 1290, 196), 'Link type (four-bar)', at=P(1093, 180), **T)
rep(im, B(112, 789, 300, 820), 'Sliding-lever type', at=P(115, 803), **T)
rep(im, B(1090, 789, 1290, 820), 'Rotary type (take-up disc)', at=P(1093, 803), **T)
L = dict(size=28, color=K, mode='c', ecolor=W)
rep(im, B(118, 223, 185, 248), 'Cam groove', anchor='rm', at=P(185, 235), **L)
rep(im, B(92, 646, 136, 671), 'Roller', anchor='rm', at=P(136, 658), **L)
rep(im, B(1106, 235, 1172, 260), 'Crank pin', anchor='rm', at=P(1172, 247), **L)
rep(im, B(1675, 235, 1860, 260), 'Eye follows the coupler curve', at=P(1678, 247), **L)
rep(im, B(1126, 646, 1172, 671), 'Rocker', anchor='rm', at=P(1172, 658), **L)
rep(im, B(72, 881, 136, 906), 'Crank pin', anchor='rm', at=P(137, 893), **L)
rep(im, B(616, 1176, 890, 1201), 'Swinging slider (the lever slides in it)', at=P(619, 1188), **L)
rep(im, B(1769, 1011, 1856, 1036), 'Fixed guide', at=P(1772, 1023), **L)
rep(im, B(1024, 1165, 1090, 1190), 'Take-up\ndisc', anchor='rm', at=P(1090, 1166), spacing=1.2, **L)
N2 = dict(size=25, color=G, mode='c', ecolor=W, spacing=1.5)
rep(im, B(1138, 877, 1215, 900), 'Uniform rotation', at=P(1142, 888), **N2)
rep(im, B(655, 593, 868, 669), 'Supply curve can be designed\nas required; groove and roller\nsuffer impact and wear; mostly\nfor low-speed domestic machines',
    at=P(659, 598), **N2)
rep(im, B(1690, 535, 1910, 636), 'Most common on industrial\nlockstitch machines: only pin\njoints, smooth, durable and\nfast; pay-out curve limited\nby the linkage geometry',
    at=P(1694, 540), **N2)
rep(im, B(90, 1252, 640, 1277), 'The lever both swings and slides, giving a flatter, longer eye path;\ncompact, also used on high-speed machines', at=P(95, 1255), **N2)
rep(im, B(1055, 1252, 1610, 1303), 'The disc’s lobe pushes the thread out (take-up) as it turns to the thread side\n'
    'and pays out as it turns away; no reciprocating impact (1953 patent);\na later patent uses it to reduce excess pay-out (1996)', at=P(1059, 1252), **N2)
save(im, N)
