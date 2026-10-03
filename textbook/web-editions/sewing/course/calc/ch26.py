"""第 26 讲（设备联网与数字孪生）数值题答案。模型与虚拟实验 26-1（model19）相同。运行：python3 course/calc/ch26.py"""
STD = dict(shift_min=480, break_min=30, sam=0.6, run_frac=0.35, seams=3, mid_stops=1, perf=0.85,
           brk_per_h=1.5, brk_min=1, wait_min=25, fault_min=12, defect=0.03, extra_trim=0.05, spm=3000)


def shift(**q):
    p = {**STD, **q}
    planned = p['shift_min'] - p['break_min']
    nb = p['brk_per_h'] * planned / 60
    oper = planned - p['wait_min'] - p['fault_min'] - nb * p['brk_min']
    pieces = oper * p['perf'] / p['sam']
    A, P, Q = oper / planned, pieces * p['sam'] / oper, 1 - p['defect']
    run = pieces * p['sam'] * p['run_frac']
    trims = pieces * p['seams'] + pieces * p['extra_trim'] + nb
    return dict(p=p, planned=planned, nb=nb, oper=oper, pieces=pieces, A=A, P=P, Q=Q, OEE=A * P * Q, run=run,
                stitches=run * p['spm'], trims=trims, est=trims / p['seams'], segs=pieces * p['seams'] * (1 + p['mid_stops']))


s = shift()
print("== 车间问题（一台平缝机一个班次）")
for k in ('planned', 'nb', 'oper', 'pieces', 'A', 'P', 'Q', 'OEE', 'run', 'stitches', 'trims', 'est'):
    print(k, round(s[k], 4))
print("运行时间比例", round(s['run'] / s['planned'], 4), "剪线计数误差", round(s['est'] / s['pieces'] - 1, 4))
print("损失：速度", round(s['oper'] * (1 - s['P']), 1), "返修", round(s['pieces'] * 0.03 * 0.6, 1))

print("== 五种上报方式（500 台、两班、250 B、300 天）")
SC = 2 * (s['nb'] + 2)
modes = dict(stitch=s['stitches'] + SC, segment=2 * s['segs'] + s['trims'] + SC, piece=s['pieces'] + SC,
             minute=s['planned'] + SC, tenmin=s['planned'] / 10)
for m, per in modes.items():
    rate = per * 500 / (480 * 60); gb = per * 500 * 2 * 300 * 250 / 1e9
    print(m, "每台每班", round(per), "条/s", round(rate, 2), "GB/年", round(gb, 1))

print("== 测验")
print("q 每针上报 2500 针/min、转 100 min、250 B：MB", 2500 * 100 * 250 / 1e6, "；每分钟汇总 450 条：MB", 450 * 250 / 1e6)
A = (450 - 50) / 450; P = 400 * 0.8 / 400; Q = 1 - 12 / 400
print("q OEE（450 计划、停 50、SAM 0.8、400 件、12 返修）", round(A, 4), round(P, 4), round(Q, 4), round(A * P * Q * 100, 2))
tr = 600 * 3 + 600 * 0.05 + 10
print("q 剪线数件（3 段、600 件、断线 10、5% 返工）", tr, round(tr / 3, 1), "误差 %", round((tr / 3 / 600 - 1) * 100, 2))
print("q 800 台每分钟一条 条/s", round(800 / 60, 2), " 年存储 GB（两班 450 min、300 天、250 B）", 800 * 450 * 2 * 300 * 250 / 1e9)
print("== 考试")
A = (450 - 60) / 450; P = 640 * 0.5 / 390; Q = 624 / 640
print("e 教材习题 2 核对", round(A, 4), round(P, 4), Q, round(A * P * Q * 100, 2))
A = (450 - 30 - 18 - 12) / 450; P = 700 * 0.45 / 390; Q = 1 - 21 / 700
print("e OEE（等活 30、故障 18、断线 12、SAM 0.45、700 件、21 返修）", round(A * P * Q * 100, 2), "= 合格品时间/计划", round(679 * 0.45 / 450 * 100, 2))
tr = 500 * 4 + 500 * 0.04 + 12
print("e 4 段：", tr / 4, "误差%", round((tr / 4 / 500 - 1) * 100, 2))
print("e 工票每扎 20 件、漏扫 3%：600 件统计", 600 * 0.97)
print("e 每件汇总 + 状态：1000 台、单班、每台每班", round(s['pieces'] + SC), "条/s", round((s['pieces'] + SC) * 1000 / 28800, 2))
print("== 作业")
st = shift(wait_min=40, fault_min=20, brk_per_h=2.0, perf=0.8, sam=0.75, defect=0.04, seams=4, extra_trim=0.06)
for k in ('nb', 'oper', 'pieces', 'A', 'P', 'Q', 'OEE', 'run', 'trims', 'est'):
    print("hw", k, round(st[k], 4))
print("hw 剪线误差 %", round((st['est'] / st['pieces'] - 1) * 100, 2), "缝纫时间比例", round(st['run'] / st['planned'] * 100, 1))
per_piece = st['pieces'] + 2 * (st['nb'] + 2)
print("hw 每件汇总 每台每班", round(per_piece), "；300 台、2 班 条/s", round(per_piece * 300 / 28800, 2), "GB/年", round(per_piece * 300 * 2 * 300 * 250 / 1e9, 2))
