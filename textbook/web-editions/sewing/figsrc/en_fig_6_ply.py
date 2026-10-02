from en_relabel import *
N = 'fig_6_ply'
im = load(N)
K = (31, 42, 54); G = (93, 107, 122); R = (192, 57, 43); BL = (47, 111, 214); GN = (46, 158, 91)
header(im, 'Ply shift and presser-foot pressure (illustrative model, two plies of slippery lining)',
       'Vertical axis: excess length of the upper ply after 40 cm of seam; presser-foot pressure as a relative value (1 = standard). Left red zone: slipping; right red zone: pressure marks')
B6 = dict(bold=True, mode='v', anchor='mm')
rep(im, B(322, 170, 366, 194), 'Slipping', 26, R, at=P(344, 182), **B6)
rep(im, B(1038, 170, 1082, 194), 'Pressure marks', 26, R, at=P(1060, 182), **B6)
rep(im, B(614, 380, 674, 404), 'Drop feed', 26, R, at=P(644, 392), **B6)
rep(im, B(1125, 537, 1183, 561), 'Needle feed', 26, BL, at=P(1154, 549), **B6)
rep(im, B(1116, 654, 1192, 678), 'Compound feed', 26, GN, at=P(1154, 666), **B6)
rep(im, B(655, 641, 718, 663), 'Usable region', 26, GN, bold=True, mode='c', ecolor=(230, 243, 235), anchor='mm', at=P(686, 652))
keep_colored(im, B(655, 630, 718, 663), seg_pred((230, 243, 235), [BL]), min_size=30)
rep(im, B(197, 559, 286, 582), 'Allowed 3 mm', 25, K, bold=True, mode='v', at=P(385, 570))
rep(im, B(630, 769, 796, 793), 'Presser-foot pressure (relative value)', 26, G, mode='c', anchor='mm', at=P(713, 781))
erase(im, B(1300, 168, 1990, 618), 'c')
blk = ('Model (illustrative):\n\n'
       'The upper ply is carried by friction between the\n'
       'plies and held back by the foot; the foot friction\n'
       'μ_f · P shears and compresses it slightly under the\n'
       'foot, so it lags by ρ = μ_f · P / K per stitch\n'
       '(K: the fabric’s resistance to deformation).\n\n'
       'Too little pressure: the dog cannot grip (slipping);\n'
       'too much: larger shift and pressure marks.\n\n'
       'Drop feed: even at the lowest non-slip pressure the\n'
       'shift is still 4.8 mm, above the allowance.\n'
       'Needle feed cuts the shift to about 30 %, compound\n'
       'feed to about 10 %, and a usable region appears.\n'
       '(Slip limits drawn for drop and needle feed; with\n'
       'compound feed the foot moves with the fabric and\n'
       'the limit falls to 0.58.)')
text(im, P(1306, 181), blk, 25, K, spacing=1.9)
save(im, N)
