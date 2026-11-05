"""大学物理 第1章 题库（施工第2步）：10 个知识点 × 2 个模板，每模板生成 6 道同构题，每个知识点 12 道。
答案全部由程序计算；带参考值的模板与第 2 轮细则核对。"""
import math, random, json, zlib
G=9.81
from ch1_items import KPS, t_conveyor, t_odometry, t_basket, t_agv, t_drone

def deg(x): return math.degrees(x)
def rad(x): return math.radians(x)

# ---- 求解函数 ----
def s_walk(p): return {"v_ground": p["vt"]-p["vw"]}                     # 车速-人向后走
def s_rel1d(p): return {"v_B_rel_A": -p["vB"]-p["vA"]}                 # 东为正，B 向西
def s_rain(p): return {"angle_from_vertical_deg": deg(math.atan2(p["vc"],p["vr"]))}
def s_speed_t(p):  # r=(A t, B t^2)
    return {"speed": math.hypot(p["A"], 2*p["B"]*p["t"])}
def s_avgvel(p): return {"v_avg": math.hypot(p["x2"]-p["x1"], p["y2"]-p["y1"])/p["dt"]}
def s_err(p): return {"rel_error_pct": 100*math.sqrt(2)*p["sigma"]/(p["v"]*p["T"])}
def s_hlaunch(p): return {"range": p["v"]*math.sqrt(2*p["h"]/G)}
def s_hmax(p): return {"h_max": (p["v0"]*math.sin(rad(p["theta"])))**2/(2*G)}
def range_h(v0,th,h0):
    vx,vy=v0*math.cos(th),v0*math.sin(th); t=(vy+math.sqrt(vy*vy+2*G*h0))/G; return vx*t
def s_shot(p):
    best=max((range_h(p["v0"],rad(a/10),p["h0"]),a/10) for a in range(300,500))
    return {"best_angle_deg":best[1],"range":best[0]}
def x_at_hoop(v0,th,h0,hoop):
    vx,vy=v0*math.cos(th),v0*math.sin(th); dy=hoop-h0
    disc=vy*vy-2*G*dy
    if disc<0: return None
    t=(vy+math.sqrt(disc))/G; return vx*t
def s_sens(p):
    th=rad(p["theta"]); dy=p["hoop"]-p["h0"]; x=p["x"]
    v0=math.sqrt(G*x*x/(2*math.cos(th)**2*(x*math.tan(th)-dy)))
    d1=x_at_hoop(v0+p["dv"],th,p["h0"],p["hoop"])-x; d2=x-x_at_hoop(v0-p["dv"],th,p["h0"],p["hoop"])
    return {"v0":v0,"miss_m":max(abs(d1),abs(d2))}
def s_dvmax(p):
    lo,hi=1e-4,1.0
    for _ in range(60):
        mid=(lo+hi)/2
        try: ok=s_sens({**p,"dv":mid})["miss_m"]<=p["e"]
        except TypeError: ok=False
        if ok: lo=mid
        else: hi=mid
    return {"dv_max":lo}
def s_bestangle(p):
    res={a:s_sens({**p,"theta":a})["miss_m"] for a in (45,55,65)}
    return {"most_tolerant_angle":min(res,key=res.get)}
def s_an(p): return {"a_n": p["v"]**2/p["R"]}
def s_omega(p): return {"v": p["w"]*p["r"], "a_n": p["w"]**2*p["r"]}
def s_vmax(p): return {"v_max": math.sqrt(p["k"]*G*p["R"]), "v_max_kmh": 3.6*math.sqrt(p["k"]*G*p["R"])}
def s_river(p):
    W,u,w=p["W"],p["u"],p["w"]
    return {"t_straight_heading":W/u,"drift":w*W/u,"t_straight_path":W/math.sqrt(u*u-w*w)}

T=[]  # id, kp, b, stem_zh, stem_en, params, solver, tol, ref, ref_ans
def add(i,kp,b,zh,en,pr,sol,tol=0.01,ref=None,ra=None,valid=None):
    T.append(dict(id=i,kp=kp,b=b,stem_zh=zh,stem_en=en,params=pr,solver=sol,tol=tol,ref=ref,ref_ans=ra,valid=valid))

add("T-1.1-a1","P1-1.1-a",-1.5,"列车以 {vt} m/s 向前行驶，乘客在车厢内以 {vw} m/s 向车尾走。求乘客相对地面的速度（向前为正）。",
    "A train moves forward at {vt} m/s; a passenger walks toward the rear at {vw} m/s. Find the passenger's velocity relative to the ground (forward positive).",
    {"vt":[10,30,2],"vw":[1,3,0.5]},s_walk)
add("T-1.1-a2","P1-1.1-a",-0.5,"取向东为正。A 车向东 {vA} m/s，B 车向西 {vB} m/s。求 B 相对 A 的速度（带正负号）。",
    "East is positive. Car A moves east at {vA} m/s and car B moves west at {vB} m/s. Find B's velocity relative to A (with sign).",
    {"vA":[5,25,5],"vB":[5,25,5]},s_rel1d)
add("T-1.1-b1","P1-1.1-b",-0.5,"传送带以 {u} m/s 向右运动，夹爪相对传送带竖直向下以 {w} m/s 运动。求夹爪对地速度的大小及其与水平方向的夹角。",
    "A conveyor moves right at {u} m/s; the gripper moves straight down relative to the belt at {w} m/s. Find the gripper's ground speed and its angle below the horizontal.",
    {"u":[0.3,0.8,0.05],"w":[0.1,0.4,0.05]},t_conveyor,ref={"u":0.5,"w":0.25},ra={"v_ground":0.56,"angle_below_horizontal_deg":26.6})
add("T-1.1-b2","P1-1.1-b",0.3,"雨滴竖直下落，速度 {vr} m/s；汽车以 {vc} m/s 行驶。车窗上雨痕与竖直方向的夹角是多少？",
    "Rain falls vertically at {vr} m/s; a car drives at {vc} m/s. What angle do the rain streaks on the side window make with the vertical?",
    {"vr":[4,10,1],"vc":[5,30,5]},s_rain,ref={"vr":7,"vc":20},ra={"angle_from_vertical_deg":70.7})
add("T-1.2-a1","P1-1.2-a",-0.8,"质点位矢 r = ({A}t, {B}t²)（m，t 单位 s）。求 t = {t} s 时的速率。",
    "A particle has position r = ({A}t, {B}t²) m. Find its speed at t = {t} s.",
    {"A":[1,4,0.5],"B":[0.5,2,0.5],"t":[1,4,1]},s_speed_t)
add("T-1.2-a2","P1-1.2-a",-1.2,"机器人 {dt} s 内从 ({x1}, {y1}) m 移动到 ({x2}, {y2}) m。求这段时间内平均速度的大小。",
    "A robot moves from ({x1}, {y1}) m to ({x2}, {y2}) m in {dt} s. Find the magnitude of its average velocity.",
    {"x1":[0,2,1],"y1":[0,2,1],"x2":[3,8,1],"y2":[2,6,1],"dt":[2,10,2]},s_avgvel)
add("T-1.2-b1","P1-1.2-b",0.6,"移动机器人里程计位置测量噪声 σ = {sigma} m，速度约 {v} m/s。用相邻两次位置差估算速率。设各次位置测量相互独立、标准差均为 σ，速率误差取两次位置差的标准差除以 T（即 √2σ/T），相对误差 = 速率误差 ÷ 速度。要求相对误差小于 {err_pct}%，采样间隔 T 至少多大？",
    "An odometer has position noise σ = {sigma} m; the robot moves at about {v} m/s. Speed is estimated from two successive positions. Assume independent position readings with standard deviation σ each; the speed error is the standard deviation of the difference divided by T (√2σ/T), and relative error = speed error ÷ speed. What minimum sampling interval T keeps the relative error below {err_pct}%?",
    {"sigma":[0.005,0.02,0.005],"v":[0.3,1.0,0.1],"err":[0.03,0.10,0.01]},t_odometry,0.02,ref={"sigma":0.01,"v":0.5,"err":0.05},ra={"T_min":0.57})
add("T-1.2-b2","P1-1.2-b",0.0,"里程计位置噪声 σ = {sigma} m，机器人速度 {v} m/s，采样间隔 T = {T} s。用相邻两次位置差估算速率。设各次位置测量相互独立、标准差均为 σ，速率误差取两次位置差的标准差除以 T（即 √2σ/T），相对误差 = 速率误差 ÷ 速度。相对误差是多少（%）？",
    "Odometer noise σ = {sigma} m, speed {v} m/s, sampling interval T = {T} s. Speed is estimated from two successive positions. Assume independent position readings with standard deviation σ each; the speed error is the standard deviation of the difference divided by T (√2σ/T), and relative error = speed error ÷ speed. What is the relative error (%)?",
    {"sigma":[0.005,0.02,0.005],"v":[0.3,1.0,0.1],"T":[0.2,1.0,0.1]},s_err,0.02)
add("T-1.3-a1","P1-1.3-a",-0.8,"小球从 {h} m 高处以 {v} m/s 水平抛出，不计空气阻力（g 取 9.81 m/s²）。求水平射程。",
    "A ball is thrown horizontally at {v} m/s from {h} m high. Ignoring drag (take g = 9.81 m/s²), find its horizontal range.",
    {"h":[1,20,1],"v":[2,15,1]},s_hlaunch)
add("T-1.3-a2","P1-1.3-a",-0.3,"以 {v0} m/s、仰角 {theta}° 抛出小球，不计空气阻力（g 取 9.81 m/s²）。求上升的最大高度（相对出手点）。",
    "A ball is launched at {v0} m/s, {theta}° above horizontal. Ignoring drag (take g = 9.81 m/s²), find the maximum height above the launch point.",
    {"v0":[5,25,1],"theta":[20,70,5]},s_hmax)
add("T-1.3-b1","P1-1.3-b",0.8,"投篮机器人在 {h0} m 高处出手，篮筐高 {hoop} m、水平距离 {x} m，出手角 {theta}°。不计空气阻力（g 取 9.81 m/s²），求出手速度。",
    "A shooting robot releases at {h0} m height; the hoop is {hoop} m high and {x} m away; launch angle {theta}°. Ignoring drag (take g = 9.81 m/s²), find the launch speed.",
    {"h0":[0.6,1.2,0.1],"hoop":[2.43,2.43,0],"x":[3.0,5.0,0.5],"theta":[45,65,5]},t_basket,ref={"h0":0.8,"hoop":2.43,"x":4.0,"theta":45},ra={"v0":8.14},
    valid=lambda p:p["x"]*math.tan(rad(p["theta"]))>p["hoop"]-p["h0"]+0.2)
add("T-1.3-b2","P1-1.3-b",1.6,"铅球在 {h0} m 高处以 {v0} m/s 推出，不计空气阻力（g 取 9.81 m/s²）。出手角多大时最远？最远多少米？（角度精确到 0.1°）",
    "A shot is released at {h0} m height with speed {v0} m/s. Ignoring drag (take g = 9.81 m/s²), what launch angle gives the longest throw, and how far is it? (angle to 0.1°)",
    {"h0":[1.6,2.2,0.1],"v0":[10,14,0.5]},s_shot,0.01,ref={"h0":2.0,"v0":13.5},ra={"best_angle_deg":42})
add("T-1.3-c1","P1-1.3-c",1.4,"投篮机器人在 {h0} m 高处出手，篮筐高 {hoop} m、水平距离 {x} m，出手角 {theta}°。名义出手速度取恰好使球穿过篮筐中心的速度；不计空气阻力（g 取 9.81 m/s²）。偏差指球下落经过篮筐高度时的水平位置偏差：分别按 v+Δv、v−Δv 精确计算，取两侧偏差绝对值的较大者。若出手速度误差 Δv = {dv} m/s，偏差是多少米？",
    "Release at {h0} m, hoop {hoop} m high and {x} m away, angle {theta}°. The nominal launch speed is the one that sends the ball through the hoop centre; ignore drag (take g = 9.81 m/s²). The miss is the horizontal offset when the ball descends through hoop height, computed exactly for v+Δv and v−Δv; take the larger absolute value. If the launch-speed error is Δv = {dv} m/s, what is the miss (m)?",
    {"h0":[0.8,0.8,0],"hoop":[2.43,2.43,0],"x":[3.5,5.0,0.5],"theta":[45,65,10],"dv":[0.1,0.2,0.05]},s_sens,0.03,ref={"h0":0.8,"hoop":2.43,"x":4.0,"theta":65,"dv":0.1},ra={"miss_m":0.13},
    valid=lambda p:p["x"]*math.tan(rad(p["theta"]))>p["hoop"]-p["h0"]+0.3)
add("T-1.3-c2","P1-1.3-c",1.3,"投篮机器人在 {h0} m 高处出手，篮筐高 {hoop} m、水平距离 {x} m，出手角 {theta}°。名义出手速度取恰好使球穿过篮筐中心的速度；不计空气阻力（g 取 9.81 m/s²）。偏差指球下落经过篮筐高度时的水平位置偏差：分别按 v+Δv、v−Δv 精确计算，取两侧偏差绝对值的较大者。要求偏差不超过 {e} m，出手速度误差 Δv 最大允许多少（m/s）？",
    "Release at {h0} m, hoop {hoop} m high and {x} m away, angle {theta}°. The nominal launch speed is the one that sends the ball through the hoop centre; ignore drag (take g = 9.81 m/s²). The miss is the horizontal offset when the ball descends through hoop height, computed exactly for v+Δv and v−Δv; take the larger absolute value. To keep the miss within {e} m, what is the largest allowed Δv (m/s)?",
    {"h0":[0.6,1.0,0.2],"hoop":[2.43,2.43,0],"x":[3.5,5.0,0.5],"theta":[45,65,10],"e":[0.05,0.15,0.05]},s_dvmax,0.02,ref={"h0":0.8,"hoop":2.43,"x":4.0,"theta":65,"e":0.13},ra={"dv_max":0.1},
    valid=lambda p:p["x"]*math.tan(rad(p["theta"]))>p["hoop"]-p["h0"]+0.3)
add("T-1.4-a1","P1-1.4-a",-1.0,"机器人以 {v} m/s 沿半径 {R} m 的圆弧行驶。求向心加速度。",
    "A robot drives at {v} m/s around an arc of radius {R} m. Find its centripetal acceleration.",
    {"v":[0.5,3.0,0.5],"R":[0.5,3.0,0.5]},s_an)
add("T-1.4-a2","P1-1.4-a",-0.4,"机械臂末端绕基座转动，角速度 {w} rad/s，到转轴距离 {r} m。求末端线速度和向心加速度。",
    "An arm's end effector rotates about the base at {w} rad/s, {r} m from the axis. Find its linear speed and centripetal acceleration.",
    {"w":[0.5,4,0.5],"r":[0.3,1.2,0.1]},s_omega)
add("T-1.4-b1","P1-1.4-b",1.0,"AGV 以半径 {R} m 转弯，重心高 {h} m，轮距 {b} m，轮地摩擦系数 {mu}。设重心位于左右轮中间，各轮摩擦系数相同，侧翻以内侧车轮刚要离地为临界（g 取 9.81 m/s²）。求开始侧翻和开始侧滑的速度，并判断哪个先发生。",
    "An AGV turns on radius {R} m; centre of mass {h} m high, track width {b} m, friction coefficient {mu}. Assume the centre of mass is midway between the wheels, equal friction at all wheels, and tipping begins when the inner wheels just lift (take g = 9.81 m/s²). Find the speeds at which it starts to tip and to slip, and which comes first.",
    {"R":[1.0,3.0,0.5],"h":[0.3,0.8,0.1],"b":[0.4,0.8,0.1],"mu":[0.4,0.8,0.1]},t_agv,ref={"R":1.5,"h":0.6,"b":0.5,"mu":0.6},ra={"v_tip":2.47,"v_slip":2.97,"first":"tip"})
add("T-1.4-b2","P1-1.4-b",0.2,"为保证舒适，侧向加速度不超过 {k}g（g 取 9.81 m/s²）。转弯半径 {R} m 时最高车速是多少（m/s 和 km/h）？",
    "For comfort, lateral acceleration must stay below {k}g (take g = 9.81 m/s²). On a {R} m radius, what is the maximum speed (m/s and km/h)?",
    {"k":[0.1,0.4,0.05],"R":[1,10,0.5]},s_vmax,ref={"k":0.3,"R":1.5},ra={"v_max":2.10})
add("T-1.5-a1","P1-1.5-a",0.3,"无人机空速 {va} m/s，侧风 {vw} m/s（垂直于航线），要沿直线飞到 {d} m 外的目标。求机头偏转角、地速、飞行时间，以及比无风时多用的时间。",
    "A drone has airspeed {va} m/s with a {vw} m/s crosswind and must fly straight to a target {d} m away. Find the heading correction, ground speed, flight time and the extra time compared with no wind.",
    {"va":[8,15,1],"vw":[2,6,1],"d":[500,2000,250]},t_drone,ref={"va":12,"vw":5,"d":1000},ra={"heading_deg":24.6,"v_ground":10.9,"t":91.7,"t_extra":8.4},
    valid=lambda p:p["vw"]<p["va"])
add("T-1.5-a2","P1-1.5-a",-0.2,"河宽 {W} m，水流速度 {w} m/s，小船相对水速度 {u} m/s。(1) 船头始终垂直河岸，过河用时多少、被冲下多远？(2) 要正对岸到达，过河用时多少？",
    "A river is {W} m wide with current {w} m/s; the boat moves at {u} m/s relative to the water. (1) Heading straight across, how long does it take and how far downstream does it land? (2) To land directly opposite, how long does it take?",
    {"W":[40,200,20],"w":[0.5,2.0,0.5],"u":[2,5,0.5]},s_river,valid=lambda p:p["w"]<p["u"])

# 修正 T-1.4-b2 的 R 范围（教学用 1–3 m 与公路 300–600 m 两档由种子决定）
for t in T:
    if t["id"]=="T-1.4-b2": t["params"]={"k":[0.1,0.4,0.05],"R":[1,600,0]}

def draw(t,rng):
    for _ in range(100):
        p={}
        for k,(lo,hi,st) in t["params"].items():
            if t["id"]=="T-1.4-b2" and k=="R": p[k]=rng.choice([1.0,1.5,2.0,2.5,3.0,300,400,500,600]); continue
            p[k]=lo if st==0 else round(lo+st*rng.randint(0,int(round((hi-lo)/st))),4)
        if t["valid"] is not None and not t["valid"](p): continue
        try: t["solver"](p); return p
        except (TypeError, ValueError, ZeroDivisionError): continue
    raise RuntimeError(t["id"])

def make(t,seed):
    p=draw(t,random.Random(zlib.crc32(f'{t["id"]}#{seed}'.encode()))); q=dict(p)
    if "err" in q: q["err_pct"]=round(q["err"]*100)
    a={k:(round(v,4) if isinstance(v,float) else v) for k,v in t["solver"](p).items()}
    return {"id":f'{t["id"]}#{seed}',"template":t["id"],"kp":t["kp"],"b":t["b"],"params":p,
            "stem_zh":t["stem_zh"].format(**q),"stem_en":t["stem_en"].format(**q),"answer":a,"rel_tol":t["tol"]}

def check_refs():
    rows=[];ok=True
    for t in T:
        if not t["ref"]: continue
        got=t["solver"](t["ref"])
        for k,v in t["ref_ans"].items():
            g=got[k]; good=(g==v) if not isinstance(v,float) and not isinstance(g,float) else abs(g-v)<=0.051*max(1,abs(v)/10) or abs(g-v)/abs(v)<0.01
            rows.append((t["id"],k,v,g if not isinstance(g,float) else round(g,3),good)); ok&=good
    return rows,ok

if __name__=="__main__":
    rows,ok=check_refs()
    for r in rows: print(f"{r[0]:10} {r[1]:26} 参考 {r[2]!s:<6} 程序 {r[3]!s:<8} {'OK' if r[4] else 'MISMATCH'}")
    print("参考核对：","全部一致" if ok else "有不一致")
    items=[]
    for t in T:
        got=[];seen=set();s_=1
        while len(got)<6:
            it=make(t,s_); s_+=1
            key=json.dumps(it["params"],sort_keys=True)
            if key in seen: continue
            seen.add(key); got.append(it)
        items+=got
    from collections import Counter
    c=Counter(i["kp"] for i in items); print("每个知识点题数：",dict(c))
    json.dump({"knowledge_points":[dict(id=a,section=b,name_zh=c_,name_en=d,prerequisites=e) for a,b,c_,d,e in KPS],
               "templates":[{k:v for k,v in t.items() if k not in("solver","valid")} for t in T],"items":items},
              open("ch1_bank.json","w"),ensure_ascii=False,indent=1)
    print("总题数",len(items))
