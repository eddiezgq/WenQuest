"""第 30 章 缝制设备发展趋势 —— 课程包数值题计算（模型与虚拟实验 30-1 相同）"""
import math
G = 9.81

def B_fab(W, c):            # FAST：B（μN·m）= 9.8e-6 × 克重 × c³(mm)；返回 N·m
    return 9.8e-6 * W * c**3 * 1e-6
def plate(E, t, rho):       # 薄板：B = E t³/12，w = ρ g t
    return E * t**3 / 12, rho * G * t
def buckle(B, L, b):        # 一端夹住、另一端可侧移的推布失稳力
    return math.pi**2 * B * b / (4 * L * L)

FAB = [("针织汗布",150,14),("衬衫府绸",120,20),("西服毛料",250,25),("牛仔布",400,35)]
for n,W,c in FAB:
    B = B_fab(W,c); w = W/1000*G
    print(n, "B μN·m", round(B*1e6,2), " 立住高度 2c≈", round((7.84*B/w)**(1/3)*100,2), "cm")
for n,(E,t,rho) in {"钢板1mm":(200e9,1e-3,7850),"卡纸0.4mm":(4e9,0.4e-3,750)}.items():
    B,w = plate(E,t,rho); print(n, "B N·m", round(B,4), "c m", round((B/w)**(1/3),3))
Bs = B_fab(120,20); Bst,_ = plate(200e9,1e-3,7850); print("衬衫/钢板", Bs/Bst)

# 推布：衬衫府绸 5 cm × 30 cm
F = buckle(Bs,0.05,0.30); Wt = 120/1000*G*0.05*0.30
print("F_cr mN", F*1e3, " 自重 mN", Wt*1e3, " 比", Wt/F, " c/L 临界", (4/math.pi**2)**(1/3))
# 两端夹住 ×16；习题 2
B2 = B_fab(200,25); print("习题2 B", B2*1e6, "F mN", buckle(B2,0.05,0.20)*1e3, "自重 mN", 0.2*G*0.05*0.2*1e3)
# 考试：牛仔布 5 cm × 20 cm
Bd = B_fab(400,35); print("牛仔 F mN", buckle(Bd,0.05,0.20)*1e3, "自重", 0.4*G*0.05*0.2*1e3)
# 测验：针织汗布 立住高度 & 推 4 cm 长 b=10 cm
Bj = B_fab(150,14); print("汗布 F(L=4cm,b=10cm) mN", buckle(Bj,0.04,0.10)*1e3)

# 节电
def energy(m,hr,pc=0.45,ps=0.25): return m*hr*pc, m*hr*ps
e1,e2 = energy(500,3550); print("500台", e1, e2, e1-e2, "t CO2", (e1-e2)*0.57/1000, "20台节电", 20*3550*0.2)
e1,e2 = energy(300,3000); sv=e1-e2; print("习题1", sv, sv*0.7, "回收月", 300*500/(sv*0.7)*12)
print("每台年节电500kWh所需开机 h", 500/0.2)
e1,e2 = energy(200,4000); sv=e1-e2; print("考试 200台4000h", sv, "CO2 t", sv*0.57/1000, "电费", sv*0.7, "回收月(600元/台)", 200*600/(sv*0.7)*12)

# 流程可靠性与回收期
def workflow(p,n,ts,tf):
    P=p**n; f=n*(1-p)/p; cyc=n*ts/p+f*tf
    return dict(P=P,f=f,cyc=cyc,human=f*tf,perh=3600/cyc,intervh=3600/cyc*f)
def payback(price,p,n=10,ts=8,tf=30,sh=2,wage=0.5):
    r=workflow(p,n,ts,tf); hours=8*sh*300; saved=sh*wage*60*8*300
    hc=r['human']/60*r['perh']*hours*wage; net=saved-hc-0.1*price
    return dict(r, saved=saved, hc=hc, net=net, months=12*price/net if net>0 else math.inf)
for p in (0.97,0.99,0.999):
    r=workflow(p,10,8,30); print(p, "P", round(r['P'],4), "干预/h", round(r['intervh'],2), "件/h", round(r['perh'],2))
print("10步90% 所需 p", 0.9**0.1, " 8步95%", 0.95**(1/8), " 0.98^8", 0.98**8, " 0.95^10", 0.95**10, " 0.99^20", 0.99**20)
for p in (0.97,0.99):
    for sh in (2,3):
        r=payback(250000,p,sh=sh); print("回收", p, sh, round(r['months'],1), "省", r['saved'], "失败人工", round(r['hc']))
r=payback(200000,0.97); print("价格20万 回收", r['months'])
r=payback(250000,0.98,n=8); print("8步 98% P", r['P'], "回收", r['months'], "干预", r['intervh'])

# 报道核对
print("22s 一件/天", 86400/22, "21 线", 21*86400/22, " 125万/年→/天", 1.25e6/365, "21线", 21*1.25e6/365, "80万/8.2万", 8e5/(21*86400/22))
print("T恤加工 CO2 g", 0.105*0.57*1000, " 缝制占比", 0.098/0.105)
