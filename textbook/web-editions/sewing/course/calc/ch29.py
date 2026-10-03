"""第 29 章 典型服装工厂 —— 课程包数值题计算（数据取自教材 29.1–29.5 节）"""
import math

OPS = [("钉洗水标","SNL",0.23),("前后片配对","MNL",0.207),("合肩缝","4OL",0.38),("领罗纹量裁","MNL",0.287),
       ("领罗纹接头","SNL",0.299),("绱领罗纹","4OL",0.345),("压领绷缝","FL",0.287),("钉主唛","SNL",0.38),
       ("袖口绷缝","FL",0.345),("袖片配对","MNL",0.253),("绱袖","4OL",0.483),("袖窿绷缝","FL",0.345),
       ("合侧缝","4OL",0.655),("袖口封结","SNL",0.425),("下摆绷缝","FL",0.529),("剪线头","MNL",0.391)]
SMV = sum(o[2] for o in OPS)
grp = {m: sum(o[2] for o in OPS if o[1] == m) for m in ("4OL","FL","SNL","MNL")}
print("ΣSMV", round(SMV,3), grp, "包缝+绷缝占比", round((grp['4OL']+grp['FL'])/SMV,3))

def line(rate):
    takt = 60/rate
    theo = SMV/takt
    per_op = [max(1, math.ceil(o[2]/takt - 1e-9)) for o in OPS]
    N1 = sum(per_op); bott1 = max(o[2]/k for o,k in zip(OPS, per_op))
    g = {m: math.ceil(s/takt - 0.05) for m,s in grp.items()}   # 允许约 1% 超节拍（教材：绷缝 5.02 配 5）
    N2 = sum(g.values()); bott2 = max(grp[m]/g[m] for m in g)
    return dict(takt_s=takt*60, theo=theo, N_op=N1, eff_op=SMV/(N1*bott1), grp=g, N_grp=N2, eff_grp=SMV/(N2*bott2))
for r in (200, 250, 180):
    print(r, {k:(round(v,3) if isinstance(v,float) else v) for k,v in line(r).items()})

# 资料原配置 22 人：瓶颈与产能
SRC=[1,1,2,1,1,1,1,2,1,1,2,1,2,2,2,1]
b = max(o[2]/k for o,k in zip(OPS,SRC)); print("22人 瓶颈负荷", b, "产能", 60/b, "平衡率", SMV/(22*b))
SRC2 = SRC.copy(); SRC2[15] += 1
b2 = max(o[2]/k for o,k in zip(OPS,SRC2)); print("23人 产能", 60/b2)

# 利特尔法则
print("西服 1500/30 =", 1500/30, "h; 300/30 =", 300/30)
print("捆扎 600/175*60 =", 600/175*60, "min; 吊挂 55/191*60 =", 55/191*60)
print("任务：在制品600、产量150 →", 600/150, "h")

# 口袋机
hand = 0.542+0.861; mach = 480*60/2400/60
print("口袋手工", hand, "机器分/个", mach, "手工人", 140*hand/60, "机器分钟/时", 140*mach, "可用率70%:", 140*mach/0.7)
# 衬衫部件占比
parts = dict(collar=3.62, cuff=3.85, placket=2.21, front=4.22, back=0.84); asm = 7.58
tot = sum(parts.values())+asm
print("衬衫合计", tot, "小部件三项占比", (3.62+3.85+2.21)/tot, "部件占比", sum(parts.values())/tot)

# 绱袖缩缝
print("缩缝 3/47", 3/47, " 习题 50/47:", (50-47)/47, " 顶部 1.5/12:", 1.5/12, "比", 1+1.5/12)

# 毛衫工时账
ff = 17/8 + 32 + 10 + 8; wg = 30/8 + 0 + 5 + 8
print("成型衣片每件人工", ff, "套口占比", 32/ff, " 全成型", wg)
print("横机台数", 1000*17/60/22, " 套口工", 1000*32/60/8, " 全成型台数", 1000*30/60/22)

# 29.5 换款模型
R0 = 30.1/47.6
def hours(Q,SAM,N,E,C,tau):
    k = N*60/SAM*E; lo,hi = 0.0,1e5
    for _ in range(200):
        m=(lo+hi)/2; Y=k*(m-(1-R0)*tau*(1-math.exp(-m/tau)))
        lo,hi = (m,hi) if Y<Q else (lo,m)
    return C+hi
def labor(Q,SAM,c): return hours(Q,SAM,**c)*c['N']*60/Q
def cross(SAM,L,Ce):
    lo,hi=10,1e6
    for _ in range(200):
        m=(lo+hi)/2
        lo,hi = (m,hi) if labor(m,SAM,L)>labor(m,SAM,Ce) else (lo,m)
    return hi
L=dict(N=30,E=0.70,C=4,tau=12); Cc=dict(N=8,E=0.58,C=0.5,tau=6)
print("r0", R0)
for Q in (150,300,1000):
    print(Q, "长线", labor(Q,12,L), "单元", labor(Q,12,Cc), "交货h", hours(Q,12,**L), hours(Q,12,**Cc), "C=0长线", labor(Q,12,{**L,'C':0}))
print("分界批量", cross(12,L,Cc), " C=1,tau=4:", cross(12,{**L,'C':1,'tau':4},Cc), " 仅C=0:", cross(12,{**L,'C':0},Cc), " 仅tau=1:", cross(12,{**L,'tau':1},Cc))
print("稳态", 12/0.7, 12/0.58)
# 学习曲线：t=3τ 时恢复比例
print("3τ 时 E/E∞ =", 1-(1-R0)*math.exp(-3))
# 考试题：单元每件人工 Q=500
print("Q=500", labor(500,12,L), labor(500,12,Cc))
# 接力区人均
print("60/7", 60/7)
