from en_relabel import *
N = 'fig_6_timing'
im = load(N)
K = (31, 42, 54); G = (93, 107, 122); PU = (142, 68, 173); R = (192, 57, 43); OR = (224, 102, 47)
DG = (27, 94, 56); GN = (46, 158, 91); BL = (47, 111, 214); AM = (187, 114, 51); AM2 = (183, 121, 31); TAN = (166, 139, 82)
header(im, 'Feed timing: when does the fabric move?',
       'Worked example: fabric 1.5 mm (two plies of cotton), stitch length 3 mm, standard timing; heights of needle point, top of eye and dog surface measured from the throat plate (0)')
M = dict(bold=True, mode='c')
rep(im, B(642, 170, 760, 191), 'Point enters 101.7°', 22, K, anchor='rm', at=P(760, 180), **M)
rep(im, B(465, 198, 590, 219), 'Take-up tightest 55°', 22, PU, anchor='rm', at=P(589, 208), **M)
rep(im, B(819, 198, 1044, 219), 'Eye top at plate, dog drops 114.2°', 22, R, at=P(820, 208), **M)
rep(im, B(1112, 170, 1185, 191), 'Loop catch 206°', 22, OR, anchor='mm', at=P(1148, 180), **M)
rep(im, B(1280, 170, 1398, 191), 'Point leaves 258.3°', 22, K, anchor='mm', at=P(1339, 180), **M)
rep(im, B(1535, 198, 1636, 219), 'Dog emerges 325.8°', 22, DG, anchor='mm', at=P(1585, 208), **M)
rep(im, B(355, 244, 500, 267), 'Dog grips and feeds (green)', 25, GN, bold=True, mode='v', at=P(358, 255))
rep(im, B(984, 246, 1114, 268), 'Needle in fabric (grey)', 25, G, mode='v', anchor='mm', at=P(1048, 257))
erase(im, B(783, 257, 856, 279), 'v')
copy_strip(im, B(809, 257, 815, 279), dy=170)
text(im, P(820, 268), 'Top of eye', 24, BL, bold=True)
rep(im, B(631, 317, 671, 339), 'Needle\npoint', 25, K, bold=True, mode='v', anchor='mm', at=P(651, 318), spacing=1.2)
rep(im, B(1078, 649, 1174, 673), 'Feed-dog tooth tip', 26, AM2, bold=True, mode='h', anchor='mm', at=P(1126, 661))
rep(im, B(104, 474, 165, 496), 'Fabric 1.5', 22, TAN, mode='c', anchor='rm', at=P(163, 485))
rep(im, B(116, 557, 165, 578), 'Plate 0', 22, G, mode='c', anchor='rm', at=P(163, 567))
erase(im, B(820, 756, 1322, 781), 'v')
copy_strip(im, B(1145, 756, 1152, 781), dy=-60)
text(im, P(824, 758), 'Fabric position (solid): moves with the dog only\nwhile the dog is above the plate; 3.00 mm per stitch', 25, AM, bold=True, spacing=1.35)
erase(im, B(980, 953, 1154, 976), 'v')
copy_strip(im, B(1145, 953, 1152, 976), dy=-100)
text(im, P(1060, 964), 'Horizontal dog position X (dashed)', 25, DG, bold=True, anchor='mm')
rep(im, B(815, 1063, 1282, 1087), 'Main-shaft angle (0° = needle bar at top dead centre; the ends show the previous and next stitch)', 25, G,
    mode='c', anchor='mm', at=P(1048, 1075))
erase(im, B(170, 1110, 1220, 1162), 'c')
text(im, P(177, 1117), 'Reading: when the dog emerges at 325.8° the needle has already left the fabric (258.3°), so the fabric moves clear of the needle;\n'
     'when the point enters at 101.7° the dog has completed 99 % of its horizontal stroke and the fabric moves only about 0.04 mm more;\n'
     'at 114.2° the top of the eye reaches the plate surface and the dog drops at the same moment: the standard timing of the instruction manual.',
     24, K, spacing=1.6)
save(im, N)
