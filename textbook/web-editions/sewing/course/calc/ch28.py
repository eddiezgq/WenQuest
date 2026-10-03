"""第 28 讲（服装生产工艺与缝制车间）数值题答案。工序数据与虚拟实验 28-1 相同。运行：python3 course/calc/ch28.py"""
import math
OPS = [(1,'后片锁边','OL',0.45,[]),(2,'收后省','SN',0.40,[1]),(3,'开后袋','SN',1.20,[2]),(4,'后袋袋布缉合','SN',0.60,[3]),(5,'后袋口套结','BT',0.25,[4]),
(6,'前片锁边','OL',0.45,[]),(7,'做斜插袋','SN',0.90,[6]),(8,'袋口压明线','SN',0.50,[7]),(9,'门襟里襟锁边','OL',0.35,[]),(10,'绱拉链','SN',0.70,[6,9]),(11,'门襟压明线','SN',0.55,[10]),
(12,'合前后裆','OL',0.50,[5,11]),(13,'合侧缝','OL',0.80,[8,12]),(14,'侧缝压明线','SN',0.60,[13]),(15,'合下裆','OL',0.70,[14]),(16,'做串带','CS',0.25,[]),(17,'绱腰头','SN',1.30,[15,16]),
(18,'做腰头两端','SN',0.60,[17]),(19,'钉串带','BT',0.55,[18]),(20,'卷裤脚','SN',0.55,[15]),(21,'锁眼','BH',0.20,[18]),(22,'钉扣','BS',0.20,[21]),(23,'剪线头检验','HD',0.60,[19,20,22])]
IMP = {3: ('AP', 0.45), 17: ('WB', 0.80)}


def ops(imp=False):
    return {i: dict(m=(IMP[i][0] if imp and i in IMP else m), sam=(IMP[i][1] if imp and i in IMP else s), pre=p) for i, n, m, s, p in OPS}


def order(o):
    succ = {i: set() for i in o}
    for i in o:
        for p in o[i]['pre']:
            succ[p].add(i)
    def all_s(i, seen=None):
        seen = set() if seen is None else seen
        for j in succ[i]:
            if j not in seen:
                seen.add(j); all_s(j, seen)
        return seen
    W = {i: o[i]['sam'] + sum(o[j]['sam'] for j in all_s(i)) for i in o}
    done, seq = set(), []
    while len(seq) < len(o):
        ready = [i for i in o if i not in done and all(p in done for p in o[i]['pre'])]
        i = max(ready, key=lambda k: (W[k], -k)); seq.append(i); done.add(i)
    return seq, W


def group_ok(g, o, takt):
    if len(g) > 4: return None
    ms = {o[i]['m'] for i in g if o[i]['m'] != 'HD'}
    if len(ms) > 2: return None
    t = sum(o[i]['sam'] for i in g); k = math.ceil(t / takt - 1e-9)
    if k > 4: return None
    return k, t / k


def dp(seq, o, takt):
    n = len(seq); best = [None] * (n + 1); best[0] = (0, 0.0, [])
    for j in range(1, n + 1):
        for i in range(max(0, j - 4), j):
            if best[i] is None: continue
            r = group_ok(seq[i:j], o, takt)
            if r is None: continue
            cand = (best[i][0] + r[0], max(best[i][1], r[1]), best[i][2] + [seq[i:j]])
            if best[j] is None or (cand[0], cand[1]) < (best[j][0], best[j][1]): best[j] = cand
    return best[n]


def report(tgt, imp=False):
    o = ops(imp); takt = 60 / tgt; tot = sum(x['sam'] for x in o.values())
    seq, W = order(ops(False))   # 与实验页相同：换专机后仍沿用原设备的位置权重顺序
    N, C, G = dp(seq, o, takt)
    return dict(takt=takt, total=round(tot, 2), N0=math.ceil(tot / takt - 1e-9), N=N, cycle=round(C, 4), out=round(60 / C, 1), bal=round(tot / (N * C) * 100, 1))


print("== 一道工序一组（120 件/时）")
o = ops(); takt = 0.5
ks = {i: math.ceil(o[i]['sam'] / takt - 1e-9) for i in o}
N = sum(ks.values()); C = max(o[i]['sam'] / ks[i] for i in o); tot = sum(x['sam'] for x in o.values())
print("总工时", round(tot, 2), "人数", N, "周期", C, "平衡率 %", round(tot / (N * C) * 100, 1))
for tgt, imp in ((120, False), (150, False), (100, False), (120, True)):
    print("自动分组", tgt, "专机" if imp else "原设备", report(tgt, imp))
print("== 车间问题 / 28.8 案例")
print("原 26 人 周期 0.70：产量", round(60 / 0.7, 1), "平衡率 %", round(13.2 / (26 * 0.7) * 100, 1))
print("重新分组 26 人 周期 0.55：产量", round(60 / 0.55, 1), "平衡率 %", round(13.2 / (26 * 0.55) * 100, 1), "提高 %", round((60 / 0.55) / (60 / 0.7) * 100 - 100, 1))
print("专机后总工时", round(13.2 - 1.2 + 0.45 - 1.3 + 0.8, 2), "26 人 120 件 平衡率 %", round(11.95 / (26 * 0.5) * 100, 1))
sav = 3 * 0.5 * 60 * 8 * 25
print("省 3 人每月 元", sav, "20 万回收月", round(200000 / sav, 1))
print("== 测时与人机")
print("SAM 侧缝压明线", round(0.48 * 1.10 * 1.14, 4))
def mm(n, a=0.3, w=0.05, t=0.9, wage=0.5, rate=0.08):
    C = max(n * (a + w), a + t); return C, (wage + n * rate) * C / n
for t in (0.9, 0.6):
    print("t =", t, "n* =", round((0.3 + t) / 0.35, 2), {n: tuple(round(x, 4) for x in mm(n, t=t)) for n in range(1, 7)})
print("== 测验")
print("q 节拍与 N0：总工时 15.6、目标 100 件/时 → 节拍", 0.6, "N0", math.ceil(15.6 / 0.6))
print("q 平衡率：16.2 分、40 人、周期 0.45 → %", round(16.2 / (40 * 0.45) * 100, 1), "产量", round(60 / 0.45, 1))
print("q SAM 0.50 × 1.05 × 1.12 =", round(0.50 * 1.05 * 1.12, 3))
print("q n*：a=0.2 w=0.05 t=0.8 →", round(1.0 / 0.25, 2), "看 3 台周期", max(3 * 0.25, 1.0), "看 5 台周期", max(5 * 0.25, 1.0))
print("q 每件成本 n=3,a=.2,w=.05,t=.8:", round(mm(3, .2, .05, .8)[1], 4), "n=4:", round(mm(4, .2, .05, .8)[1], 4), "n=5:", round(mm(5, .2, .05, .8)[1], 4))
print("q 分床：S 150 M 300 L 300 XL 150，1:2:2:1 唛架 → 每码层数", 150, "，上限 60 层 → 床数", math.ceil(150 / 60), "（60、60、30）")
print("== 考试")
print("e 18 分、150 件/时：节拍 0.4，N0", math.ceil(18 / 0.4), "；50 人周期 0.38 平衡率", round(18 / (50 * 0.38) * 100, 1), "产量", round(60 / 0.38, 1))
print("e 一人多机 a=0.25 w=0.05 t=1.0: n*", round(1.25 / 0.3, 2), "4 台周期", max(4 * 0.3, 1.25), "5 台", max(5 * 0.3, 1.25))
print("e 观测 0.40 评比 95% 宽放 15%：SAM", round(0.40 * 0.95 * 1.15, 4))
print("e 专机回收：省 2 人、0.5 元/分、25 天×8 h，净投资 15 万 → 月", round(150000 / (2 * 0.5 * 60 * 8 * 25), 1))
print("e 平缝机台数 ⌈1.2/0.5⌉ =", math.ceil(1.2 / 0.5), " 人机比 34/29 =", round(34 / 29, 2))
print("== 作业")
tot = 0.45 + 0.70 + 0.55 + 1.10 + 0.60 + 0.30 + 0.80 + 0.50
print("hw 工序总工时", tot)
# 作业第 1 题：T 恤 8 道工序，目标 150 件/时
TS = {1: dict(m='OL', sam=0.45, pre=[]), 2: dict(m='OL', sam=0.70, pre=[1]), 3: dict(m='CS', sam=0.55, pre=[2]),
      4: dict(m='OL', sam=1.10, pre=[3]), 5: dict(m='OL', sam=0.60, pre=[4]), 6: dict(m='CS', sam=0.30, pre=[5]),
      7: dict(m='CS', sam=0.80, pre=[5]), 8: dict(m='HD', sam=0.50, pre=[6, 7])}
tk = 60 / 150; tot = sum(x['sam'] for x in TS.values())
ks = {i: math.ceil(TS[i]['sam'] / tk - 1e-9) for i in TS}; N1 = sum(ks.values()); C1 = max(TS[i]['sam'] / ks[i] for i in TS)
print("hw T恤 节拍", tk, "N0", math.ceil(tot / tk - 1e-9), "一道一组", N1, "周期", round(C1, 3), "平衡率 %", round(tot / (N1 * C1) * 100, 1))
seq, _ = order(TS); N2, C2, G2 = dp(seq, TS, tk)
print("hw T恤 分组", N2, round(C2, 4), "平衡率 %", round(tot / (N2 * C2) * 100, 1), G2)
for n in (3, 4, 5):
    C, cost = mm(n, 0.25, 0.05, 1.0, 0.5, 0.10)
    print("hw 一人多机 n=", n, "C", C, "每件成本", round(cost, 4))
print("hw SAM 观测 0.52 评比 90% 宽放 15%", round(0.52 * 0.90 * 1.15, 4))
