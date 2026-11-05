"""大学物理 第1章 质点运动学：知识点、题目模板、同构题生成与答案计算（样例）。
每个模板：参数范围 + 求解函数（答案由程序计算）+ 容差。"""
import math, random, json
G = 9.81

KPS = [
 ("P1-1.1-a","1.1","参考系与坐标系","Reference frames and coordinates",[]),
 ("P1-1.1-b","1.1","伽利略速度合成","Galilean velocity addition",["P1-1.1-a"]),
 ("P1-1.2-a","1.2","位矢、位移与速度","Position, displacement and velocity",["P1-1.1-a"]),
 ("P1-1.2-b","1.2","数值微分与采样误差","Numerical differentiation and sampling error",["P1-1.2-a"]),
 ("P1-1.3-a","1.3","抛体运动方程","Projectile equations of motion",["P1-1.2-a"]),
 ("P1-1.3-b","1.3","按目标求初速度","Launch speed to hit a target",["P1-1.3-a"]),
 ("P1-1.3-c","1.3","出手误差的灵敏度","Sensitivity to launch error",["P1-1.3-b"]),
 ("P1-1.4-a","1.4","向心加速度","Centripetal acceleration",["P1-1.2-a"]),
 ("P1-1.4-b","1.4","侧翻与侧滑条件","Tip-over and slip conditions",["P1-1.4-a"]),
 ("P1-1.5-a","1.5","相对运动与航向修正","Relative motion and heading correction",["P1-1.1-b"]),
]

def t_conveyor(p):
    u,w=p["u"],p["w"]; v=math.hypot(u,w); ang=math.degrees(math.atan2(w,u))
    return {"v_ground":v,"angle_below_horizontal_deg":ang}
def t_odometry(p):
    s,v,e=p["sigma"],p["v"],p["err"]
    return {"T_min":math.sqrt(2)*s/(v*e)}
def t_basket(p):
    x,dy,th=p["x"],p["hoop"]-p["h0"],math.radians(p["theta"])
    den=2*math.cos(th)**2*(x*math.tan(th)-dy)
    return {"v0":math.sqrt(G*x*x/den)}
def t_agv(p):
    R,h,b,mu=p["R"],p["h"],p["b"],p["mu"]
    vt=math.sqrt(G*R*(b/2)/h); vs=math.sqrt(mu*G*R)
    return {"v_tip":vt,"v_slip":vs,"first":"tip" if vt<vs else "slip"}
def t_drone(p):
    va,vw,d=p["va"],p["vw"],p["d"]
    phi=math.degrees(math.asin(vw/va)); vg=math.sqrt(va*va-vw*vw)
    return {"heading_deg":phi,"v_ground":vg,"t":d/vg,"t_extra":d/vg-d/va}

TEMPLATES = [
 {"id":"T-1.1-01","kp":["P1-1.1-b"],"type":"numeric","difficulty_prior":-0.5,
  "stem_zh":"传送带以 {u} m/s 向右运动，夹爪相对传送带竖直向下以 {w} m/s 运动。求夹爪对地速度的大小及其与水平方向的夹角。",
  "stem_en":"A conveyor moves right at {u} m/s; the gripper moves straight down relative to the belt at {w} m/s. Find the gripper's ground speed and its angle below the horizontal.",
  "params":{"u":[0.3,0.8,0.05],"w":[0.1,0.4,0.05]},"solver":t_conveyor,"tol":0.01,
  "reference":{"u":0.50,"w":0.25},"reference_answer":{"v_ground":0.56,"angle_below_horizontal_deg":26.6}},
 {"id":"T-1.2-01","kp":["P1-1.2-b"],"type":"numeric","difficulty_prior":0.5,
  "stem_zh":"移动机器人里程计位置测量噪声 σ = {sigma} m，速度约 {v} m/s。用相邻两次位置差估算速率，要求误差小于 {err_pct}%，采样间隔 T 至少多大？",
  "stem_en":"An odometer has position noise σ = {sigma} m; the robot moves at about {v} m/s. Estimating speed from two successive positions, what minimum sampling interval T keeps the error below {err_pct}%?",
  "params":{"sigma":[0.005,0.02,0.005],"v":[0.3,1.0,0.1],"err":[0.03,0.10,0.01]},"solver":t_odometry,"tol":0.02,
  "reference":{"sigma":0.01,"v":0.5,"err":0.05},"reference_answer":{"T_min":0.57}},
 {"id":"T-1.3-01","kp":["P1-1.3-a","P1-1.3-b"],"type":"numeric","difficulty_prior":0.8,
  "stem_zh":"投篮机器人在 {h0} m 高处出手，篮筐高 {hoop} m、水平距离 {x} m，出手角 {theta}°。不计空气阻力，求出手速度。",
  "stem_en":"A shooting robot releases at {h0} m height; the hoop is {hoop} m high and {x} m away; launch angle {theta}°. Ignoring drag, find the launch speed.",
  "params":{"h0":[0.6,1.2,0.1],"hoop":[2.43,2.43,0],"x":[3.0,5.0,0.5],"theta":[45,65,5]},"solver":t_basket,"tol":0.01,
  "reference":{"h0":0.8,"hoop":2.43,"x":4.0,"theta":45},"reference_answer":{"v0":8.13}},
 {"id":"T-1.4-01","kp":["P1-1.4-a","P1-1.4-b"],"type":"numeric","difficulty_prior":1.0,
  "stem_zh":"AGV 以半径 {R} m 转弯，重心高 {h} m，轮距 {b} m，轮地摩擦系数 {mu}。求开始侧翻和开始侧滑的速度，并判断哪个先发生。",
  "stem_en":"An AGV turns on radius {R} m; centre of mass {h} m high, track width {b} m, friction coefficient {mu}. Find the speeds at which it starts to tip and to slip, and which comes first.",
  "params":{"R":[1.0,3.0,0.5],"h":[0.3,0.8,0.1],"b":[0.4,0.8,0.1],"mu":[0.4,0.8,0.1]},"solver":t_agv,"tol":0.01,
  "reference":{"R":1.5,"h":0.6,"b":0.5,"mu":0.6},"reference_answer":{"v_tip":2.47,"v_slip":2.97,"first":"tip"}},
 {"id":"T-1.5-01","kp":["P1-1.5-a"],"type":"numeric","difficulty_prior":0.3,
  "stem_zh":"无人机空速 {va} m/s，侧风 {vw} m/s（垂直于航线），要沿直线飞到 {d} m 外的目标。求机头偏转角、地速、飞行时间，以及比无风时多用的时间。",
  "stem_en":"A drone has airspeed {va} m/s with a {vw} m/s crosswind and must fly straight to a target {d} m away. Find the heading correction, ground speed, flight time and the extra time compared with no wind.",
  "params":{"va":[8,15,1],"vw":[2,6,1],"d":[500,2000,250]},"solver":t_drone,"tol":0.01,
  "reference":{"va":12,"vw":5,"d":1000},"reference_answer":{"heading_deg":24.6,"v_ground":10.9,"t":91.7,"t_extra":8.4}},
]

def draw(tpl,rng):
    p={}
    for k,(lo,hi,st) in tpl["params"].items():
        p[k]=lo if st==0 else round(lo+st*rng.randint(0,int(round((hi-lo)/st))),4)
    return p

def instance(tpl,seed):
    rng=random.Random(seed)
    for _ in range(50):
        p=draw(tpl,rng)
        if tpl["id"]=="T-1.3-01" and p["x"]*math.tan(math.radians(p["theta"]))<= p["hoop"]-p["h0"]+0.2: continue
        if tpl["id"]=="T-1.5-01" and p["vw"]>=p["va"]: continue
        break
    q=dict(p); 
    if "err" in q: q["err_pct"]=round(q["err"]*100)
    ans={k:(round(v,4) if isinstance(v,float) else v) for k,v in tpl["solver"](p).items()}
    return {"template":tpl["id"],"seed":seed,"params":p,"stem_zh":tpl["stem_zh"].format(**q),"stem_en":tpl["stem_en"].format(**q),"answer":ans,"rel_tol":tpl["tol"]}

if __name__=="__main__":
    ok=True
    for t in TEMPLATES:
        got=t["solver"](t["reference"])
        for k,v in t["reference_answer"].items():
            g=got[k]
            good=(g==v) if isinstance(v,str) else abs(g-v)<=max(0.05*abs(v)*0.2,0.051)
            print(f'{t["id"]:10} {k:28} 参考 {v:<8} 程序 {g if isinstance(g,str) else round(g,3)}  {"OK" if good else "MISMATCH"}')
            ok&=good
    print("ALL OK" if ok else "CHECK FAILED")
    out={"knowledge_points":[dict(id=a,section=b,name_zh=c,name_en=d,prerequisites=e) for a,b,c,d,e in KPS],
         "item_templates":[{k:v for k,v in t.items() if k!="solver"} for t in TEMPLATES],
         "sample_instances":[instance(t,s) for t in TEMPLATES for s in (101,202,303)]}
    json.dump(out,open("ch1_bank_sample.json","w"),ensure_ascii=False,indent=1)
    for i in out["sample_instances"][:15:3]: print(i["stem_zh"],"→",i["answer"])
