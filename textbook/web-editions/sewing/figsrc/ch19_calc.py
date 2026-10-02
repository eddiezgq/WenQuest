# -*- coding: utf-8 -*-
"""第 19 章 算例与“零件库快速配套器”的共用模型（示意值）。

- LIB：页面内置的小型示意零件库。缝制电控模块（D-…）用的是本书的“建议编号，计划入库”，
  规格后缀和全部参数、单价都是示意值；机械件引用问渠零件库里已有的条目和规格
  （A-PUL-HTD、A-BSC-SFU、A-LGD-RAIL、A-CPL-JAW 的尺寸取自库里的 specs.csv），单价示意。
- REQ：四种机器的需求表初值（虚拟实验 19-1 的默认值）。
- configure()：计算需求 → 按判据从库里挑最便宜的组合 → BOM、I/O、固件配置。
  labs/config.html 逐行移植这个文件；python3 figsrc/ch19_calc.py 打印 19.4 节的全部数字，
  并写出 figsrc/ch19_lib.json（实验页面内嵌的就是这份数据）。
"""
import json, math, itertools, os, copy

PI = math.pi
RPM = 2*PI/60

# ---------------------------------------------------------------- 示意零件库
LIB = {
 # 交流永磁同步伺服电机（带 2500 线增量编码器）
 "D-MOT-PMSM": {"zh": "交流永磁同步伺服电机", "en": "AC PMSM servo motor", "sizes": [
   {"size": "250", "rated_power_W": 250, "rated_speed_rpm": 3000, "max_speed_rpm": 5000, "rated_torque_Nm": 0.80, "peak_torque_Nm": 2.0, "rotor_inertia_kgm2": 0.6e-4, "encoder_ppr": 2500, "kt_NmA": 0.45, "price": 520},
   {"size": "400", "rated_power_W": 400, "rated_speed_rpm": 3000, "max_speed_rpm": 6000, "rated_torque_Nm": 1.27, "peak_torque_Nm": 3.2, "rotor_inertia_kgm2": 1.0e-4, "encoder_ppr": 2500, "kt_NmA": 0.50, "price": 680},
   {"size": "550", "rated_power_W": 550, "rated_speed_rpm": 3500, "max_speed_rpm": 7500, "rated_torque_Nm": 1.50, "peak_torque_Nm": 4.5, "rotor_inertia_kgm2": 1.4e-4, "encoder_ppr": 2500, "kt_NmA": 0.50, "price": 860},
   {"size": "750", "rated_power_W": 750, "rated_speed_rpm": 3000, "max_speed_rpm": 6000, "rated_torque_Nm": 2.39, "peak_torque_Nm": 7.2, "rotor_inertia_kgm2": 2.6e-4, "encoder_ppr": 2500, "kt_NmA": 0.55, "price": 1050}]},
 "D-DRV-SERVO": {"zh": "伺服驱动器", "en": "Servo drive", "sizes": [
   {"size": "1A5", "supply_V": 220, "cont_current_A": 1.5, "peak_current_A": 4.5, "brake_energy_J": 30, "bus": "CAN FD", "modes": "速度/转矩", "price": 380},
   {"size": "3A", "supply_V": 220, "cont_current_A": 3.0, "peak_current_A": 9.0, "brake_energy_J": 70, "bus": "CAN FD", "modes": "速度/转矩", "price": 480},
   {"size": "5A", "supply_V": 220, "cont_current_A": 5.0, "peak_current_A": 15.0, "brake_energy_J": 150, "bus": "CAN FD", "modes": "速度/转矩/位置", "price": 620}]},
 # 混合式步进电机；corner_speed_rpm：48 V 驱动时转矩开始下降的转速（示意矩频模型：拐点以上按 1/n 下降）
 "D-MOT-STEP": {"zh": "混合式步进电机", "en": "Hybrid stepper motor", "sizes": [
   {"size": "17-045", "frame": "NEMA 17", "holding_torque_Nm": 0.45, "rotor_inertia_kgm2": 0.068e-4, "rated_current_A": 1.7, "closed_loop": False, "corner_speed_rpm": 600, "price": 70},
   {"size": "23-12", "frame": "NEMA 23", "holding_torque_Nm": 1.2, "rotor_inertia_kgm2": 0.30e-4, "rated_current_A": 3.0, "closed_loop": False, "corner_speed_rpm": 500, "price": 120},
   {"size": "23-22C", "frame": "NEMA 23", "holding_torque_Nm": 2.2, "rotor_inertia_kgm2": 0.48e-4, "rated_current_A": 4.2, "closed_loop": True, "corner_speed_rpm": 450, "price": 260},
   {"size": "34-45C", "frame": "NEMA 34", "holding_torque_Nm": 4.5, "rotor_inertia_kgm2": 1.4e-4, "rated_current_A": 6.0, "closed_loop": True, "corner_speed_rpm": 350, "price": 420},
   {"size": "34-85C", "frame": "NEMA 34", "holding_torque_Nm": 8.5, "rotor_inertia_kgm2": 2.7e-4, "rated_current_A": 6.0, "closed_loop": True, "corner_speed_rpm": 250, "price": 560}]},
 "D-DRV-STEP": {"zh": "步进驱动器", "en": "Stepper drive", "sizes": [
   {"size": "2A", "supply_V": 48, "current_A": 2.2, "microstep": 16, "interface": "脉冲/方向", "closed_loop": False, "price": 60},
   {"size": "4A", "supply_V": 48, "current_A": 4.2, "microstep": 16, "interface": "脉冲/方向", "closed_loop": False, "price": 95},
   {"size": "C4A", "supply_V": 48, "current_A": 4.5, "microstep": 16, "interface": "脉冲/方向", "closed_loop": True, "price": 180},
   {"size": "C6A", "supply_V": 48, "current_A": 6.0, "microstep": 16, "interface": "脉冲/方向", "closed_loop": True, "price": 240}]},
 # 推拉式电磁铁；t_on/t_off：用 D-DRV-SOL（24 V 强激磁、48 V 稳压管续流）驱动时的吸合/释放时间（第 13 章的方法，示意）
 "D-SOL-PUSH": {"zh": "推拉式电磁铁", "en": "Push-pull solenoid", "sizes": [
   {"size": "SEL", "stroke_mm": 0.3, "force_at_stroke_N": 2.5, "coil_R_ohm": 6, "duty_pct": 50, "hold_A": 0.3, "t_on_ms": 0.6, "t_off_ms": 0.5, "price": 55},
   {"size": "S8", "stroke_mm": 4, "force_at_stroke_N": 8, "coil_R_ohm": 12, "duty_pct": 25, "hold_A": 0.6, "t_on_ms": 5.5, "t_off_ms": 4.0, "price": 45},
   {"size": "M15", "stroke_mm": 6, "force_at_stroke_N": 15, "coil_R_ohm": 8, "duty_pct": 25, "hold_A": 1.0, "t_on_ms": 6.9, "t_off_ms": 5.1, "price": 60},
   {"size": "L30", "stroke_mm": 10, "force_at_stroke_N": 30, "coil_R_ohm": 6, "duty_pct": 25, "hold_A": 1.2, "t_on_ms": 11.0, "t_off_ms": 7.0, "price": 85},
   {"size": "XL60", "stroke_mm": 12, "force_at_stroke_N": 60, "coil_R_ohm": 4, "duty_pct": 15, "hold_A": 1.5, "t_on_ms": 16.0, "t_off_ms": 9.0, "price": 130}]},
 "D-DRV-SOL": {"zh": "电磁铁驱动板", "en": "Solenoid driver board", "sizes": [
   {"size": "4CH", "channels": 4, "boost_V": 24, "hold_A": 2.0, "peak_A": 6.0, "clamp_V": 48, "price": 150},
   {"size": "8CH", "channels": 8, "boost_V": 24, "hold_A": 2.0, "peak_A": 8.0, "clamp_V": 48, "price": 240}]},
 "D-ENC-INC": {"zh": "增量编码器", "en": "Incremental encoder", "sizes": [
   {"size": "500", "ppr": 500, "index": True, "max_rpm": 6000, "output": "差分", "price": 60},
   {"size": "1000", "ppr": 1000, "index": True, "max_rpm": 6000, "output": "差分", "price": 80},
   {"size": "2500", "ppr": 2500, "index": True, "max_rpm": 6000, "output": "差分", "price": 120}]},
 "D-SNS-HALL": {"zh": "霍尔脚踏传感器", "en": "Hall pedal sensor", "sizes": [{"size": "P20", "range_mm": 20, "output_V": "0.5–4.5", "price": 40}]},
 "D-SNS-PE": {"zh": "光电传感器", "en": "Photoelectric sensor", "sizes": [{"size": "R30", "range_mm": 30, "response_ms": 0.5, "price": 35}]},
 "D-SNS-PROX": {"zh": "接近开关", "en": "Proximity switch", "sizes": [{"size": "M8", "range_mm": 2, "type": "电感式 PNP", "price": 25}]},
 "D-CTL-WQSC": {"zh": "WQ-SC 主控板", "en": "WQ-SC controller board", "sizes": [
   {"size": "S", "cpu": "Cortex-M4F 170 MHz", "encoder_inputs": 2, "pwm_ch": 8, "can_fd": 1, "di": 12, "do": 8, "ai": 4, "price": 420},
   {"size": "L", "cpu": "Cortex-M4F 170 MHz + FPGA", "encoder_inputs": 4, "pwm_ch": 16, "can_fd": 2, "di": 24, "do": 16, "ai": 8, "price": 680}]},
 "D-IO-EXP": {"zh": "CAN FD 扩展 I/O 板", "en": "CAN FD I/O expansion board", "sizes": [{"size": "16", "di": 16, "do": 16, "ai": 4, "price": 180}]},
 "D-GW-WQSC": {"zh": "网关模块", "en": "Gateway module", "sizes": [{"size": "E", "net": "以太网 + Wi-Fi", "protocols": "MQTT、HTTP", "price": 150}]},
 "D-PSU-SMPS": {"zh": "开关电源", "en": "Switch-mode power supply", "sizes": [
   {"size": "24V100", "V_out": 24, "P_W": 100, "price": 90},
   {"size": "24V150", "V_out": 24, "P_W": 150, "price": 120},
   {"size": "24V240", "V_out": 24, "P_W": 240, "price": 160},
   {"size": "48V240", "V_out": 48, "P_W": 240, "price": 150},
   {"size": "48V350", "V_out": 48, "P_W": 350, "price": 210},
   {"size": "48V480", "V_out": 48, "P_W": 480, "price": 270}]},
 "D-PNU-CYL": {"zh": "气缸", "en": "Pneumatic cylinder", "sizes": [{"size": "32x25", "bore_mm": 32, "stroke_mm": 25, "price": 65}]},
 "D-PNU-VLV": {"zh": "电磁阀", "en": "Solenoid valve", "sizes": [{"size": "52-24", "ports": "5/2", "V": 24, "price": 55}]},
 "D-HMI-PANEL": {"zh": "触摸屏", "en": "Touch panel", "sizes": [{"size": "7", "size_in": 7, "interface": "RS-485", "price": 260}]},
 # —— 问渠零件库里已有的机械件（尺寸取自库的 specs.csv；单价示意）
 "A-PUL-HTD": {"zh": "同步带轮", "en": "Timing pulley", "lib": True, "sizes": [
   {"size": "GT2-20-9", "PD_mm": 12.732, "b_mm": 9, "J_kgm2": 0.6e-6, "price": 25},
   {"size": "3M-24-15", "PD_mm": 22.918, "b_mm": 15, "J_kgm2": 2.5e-6, "price": 35},
   {"size": "5M-20-25", "PD_mm": 31.831, "b_mm": 25, "J_kgm2": 9.0e-6, "price": 55}]},
 "A-BSC-SFU": {"zh": "滚珠丝杠副", "en": "Ball screw (SFU)", "lib": True, "sizes": [
   {"size": "16x5", "d0_mm": 16, "Ph_mm": 5, "Dw_mm": 3.175, "price": 160},
   {"size": "16x10", "d0_mm": 16, "Ph_mm": 10, "Dw_mm": 3.175, "price": 180},
   {"size": "25x10", "d0_mm": 25, "Ph_mm": 10, "Dw_mm": 4.762, "price": 260}]},
 "A-LGD-RAIL": {"zh": "直线导轨副", "en": "Linear guideway", "lib": True, "sizes": [{"size": "HGH15CA", "rail_W_mm": 15, "C_N": 14700, "price": 140}]},
 "A-CPL-JAW": {"zh": "梅花形弹性联轴器", "en": "Jaw coupling", "lib": True, "sizes": [{"size": "LM1", "d_min_mm": 12, "d_max_mm": 25, "J_kgm2": 2e-4, "price": 35}]},
 # 库里没有的外购件：同步带（按米计）
 "BUY-BELT": {"zh": "同步带（库里没有，外购）", "en": "Timing belt (not in library, bought out)", "sizes": [
   {"size": "GT2-9", "b_mm": 9, "EA_kN": 90, "price_per_m": 20},
   {"size": "3M-15", "b_mm": 15, "EA_kN": 150, "price_per_m": 30},
   {"size": "5M-25", "b_mm": 25, "EA_kN": 250, "price_per_m": 45}]},
}
BELT_FOR = {"GT2-20-9": "GT2-9", "3M-24-15": "3M-15", "5M-20-25": "5M-25"}

# ---------------------------------------------------------------- 判据常数（示意）
K = dict(Tf=0.15,          # 主轴库仑摩擦 N·m（第 13 章）
         Trun=0.35,        # 稳速缝纫时的平均负载转矩 N·m（摩擦 + 缝纫阻力，示意）
         starts_per_min=30, sew_frac=0.5,   # 间歇工况（第 18 章）：每分钟起停 30 次，缝纫占一半时间
         kT_servo=0.8,     # 加速所需转矩 ≤ 0.8 × 峰值转矩
         Jratio_max=10,    # 负载惯量 / 转子惯量 ≤ 10
         regen=0.7,        # 急停时回馈到母线的动能比例（第 13 章）
         kT_open=0.6, kT_closed=0.8,   # 步进：所需转矩 ≤ k × 当时可用转矩
         DN_max=70000,     # 滚珠丝杠 d0·n ≤ 70000（示意）
         fn_min=80,        # 同步带轴的最低固有频率 Hz（第 15 章算例 82 Hz）
         sol_ang_max=20,   # 剪线电磁铁吸合/释放折算转角 ≤ 20°（第 13 章，PLATFORM 6）
         bt_window=211.6-10,  # 倒缝切换窗口（第 14 章）
         eta_belt=0.95, eta_screw=0.9, rho_steel=7850,
         P_logic=8, P_hmi=6, boost_share=0.5, psu_margin=1.2, step_eff=0.6, step_idle=5,
         sel_share=0.8)    # 选针器一次吸合+释放 ≤ 0.8 × 一针时间

# ---------------------------------------------------------------- 四种机器的需求表初值
REQ = {
 "LS": dict(name="平缝机 WQ-SC/LS", n_max=5000, t_acc=0.15, J_load=5.0e-4, n_trim=300, n_bt=1800, hmi=False,
            actions=[  # (id, 名称, 行程 mm, 力 N, 何时动作)
              ("trim", "剪线", 3, 12, "trim"), ("wipe", "拨线", 4, 5, "stop"),
              ("bt", "倒缝", 8, 25, "bt"), ("pfl", "抬压脚", 10, 50, "stop")],
            di=["急停", "机头翻起安全开关", "手动回针按钮", "断线检测"], ai=["脚踏", "电控箱温度"],
            sensors=[("D-SNS-HALL", "P20", 1, "脚踏"), ("D-SNS-PE", "R30", 1, "断线检测"), ("D-SNS-PROX", "M8", 1, "机头翻起")],
            pneu=[], axes=[], fixed_steps=[], knit=None),
 "OL": dict(name="包缝机 WQ-SC/OL", n_max=6000, t_acc=0.15, J_load=3.0e-4, n_trim=300, n_bt=1800, hmi=False,
            actions=[("cut", "链线切刀", 3, 12, "stop"), ("pfl", "抬压脚", 10, 50, "stop")],
            di=["急停", "机头翻起安全开关", "前布边光电", "后布边光电"], ai=["脚踏", "电控箱温度"],
            sensors=[("D-SNS-HALL", "P20", 1, "脚踏"), ("D-SNS-PE", "R30", 2, "前、后布边"), ("D-SNS-PROX", "M8", 1, "机头翻起")],
            pneu=[("D-PNU-VLV", "52-24", 1, "吸线头气阀")], axes=[], fixed_steps=[], knit=None),
 "PS": dict(name="电子花样机 WQ-SC/PS", n_max=2800, t_acc=0.15, J_load=5.0e-4, n_trim=300, n_bt=1800, hmi=True,
            actions=[("trim", "剪线", 3, 12, "trim"), ("wipe", "拨线", 4, 5, "stop"), ("trel", "松线", 3, 6, "stop")],
            di=["急停", "安全光幕", "X 原点", "Y 原点", "X 正限位", "X 负限位", "Y 正限位", "Y 负限位",
                "左压框到位", "右压框到位", "气压开关", "断线检测"], ai=["电控箱温度"],
            di_pedal=["压框脚踏", "启动脚踏"],
            sensors=[("D-SNS-PROX", "M8", 6, "X/Y 原点与限位"), ("D-SNS-PE", "R30", 1, "断线检测")],
            pneu=[("D-PNU-CYL", "32x25", 2, "左、右压框气缸"), ("D-PNU-VLV", "52-24", 2, "左、右压框电磁阀")],
            axes=[dict(id="X", name="X 轴", travel=300, m=2.0, F=10.0),
                  dict(id="Y", name="Y 轴", travel=200, m=5.0, F=15.0)],
            v=0.5, a=25.0, fixed_steps=[], knit=None),
 "FK": dict(name="缩比横机 WQ-SC/FK", n_max=None, hmi=True,
            actions=[("car1", "纱嘴 1", 4, 5, "stop"), ("car2", "纱嘴 2", 4, 5, "stop")],
            di=["急停", "安全门", "机头原点", "左限位", "右限位", "断纱检测"], ai=["电控箱温度", "纱线张力"],
            sensors=[("D-SNS-PROX", "M8", 3, "机头原点与限位"), ("D-SNS-PE", "R30", 1, "断纱检测")],
            pneu=[],
            axes=[dict(id="C", name="机头", travel=None, m=3.0, F=20.0)],
            v=0.5, a=5.0,
            fixed_steps=[("st1", "度目（左）", 0.15, 300), ("st2", "度目（右）", 0.15, 300), ("td", "牵拉", 0.6, 60)],
            knit=dict(needles=60, E=5, selectors=2, cam_mm=120)),
}

# ---------------------------------------------------------------- 工具
def item(cat, size):
    return next(s for s in LIB[cat]["sizes"] if s["size"] == size)

def step_torque(m, n):
    """示意矩频：拐点以下为保持转矩，以上按 n_c/n 下降"""
    return m["holding_torque_Nm"]*min(1.0, m["corner_speed_rpm"]/max(n, 1e-9))

def crit(group, text, val, lim, ok, unit=""):
    return dict(group=group, text=text, val=val, lim=lim, ok=bool(ok), unit=unit)

# ---------------------------------------------------------------- 主轴
def spindle_need(r, mot):
    w = r["n_max"]*RPM
    J = r["J_load"]+mot["rotor_inertia_kgm2"]
    alpha = w/r["t_acc"]
    T_acc = J*alpha+K["Tf"]
    f_acc = K["starts_per_min"]*2*r["t_acc"]/60          # 加速 + 减速所占时间比例
    f_run = K["sew_frac"]-f_acc
    T_rms = math.sqrt(f_acc*T_acc**2+f_run*K["Trun"]**2)
    E = 0.5*J*w**2
    return dict(w=w, J=J, alpha=alpha, T_acc=T_acc, T_rms=T_rms, f_acc=f_acc, E=E, E_regen=K["regen"]*E,
                ratio=r["J_load"]/mot["rotor_inertia_kgm2"])

def spindle_check(r, mot, drv):
    s = spindle_need(r, mot); C = []
    C.append(crit("主轴", "最高转速 ≤ 电机最高转速", r["n_max"], mot["max_speed_rpm"], r["n_max"] <= mot["max_speed_rpm"], "r/min"))
    C.append(crit("主轴", "加速所需转矩 ≤ 0.8 × 峰值转矩", s["T_acc"], K["kT_servo"]*mot["peak_torque_Nm"], s["T_acc"] <= K["kT_servo"]*mot["peak_torque_Nm"], "N·m"))
    C.append(crit("主轴", "间歇工况等效转矩 ≤ 额定转矩", s["T_rms"], mot["rated_torque_Nm"], s["T_rms"] <= mot["rated_torque_Nm"], "N·m"))
    C.append(crit("主轴", "负载惯量 / 转子惯量 ≤ 10", s["ratio"], K["Jratio_max"], s["ratio"] <= K["Jratio_max"]))
    Ic, Ip = s["T_rms"]/mot["kt_NmA"], s["T_acc"]/mot["kt_NmA"]
    C.append(crit("伺服驱动", "连续电流 ≤ 驱动器额定", Ic, drv["cont_current_A"], Ic <= drv["cont_current_A"], "A"))
    C.append(crit("伺服驱动", "加速电流 ≤ 驱动器峰值", Ip, drv["peak_current_A"], Ip <= drv["peak_current_A"], "A"))
    C.append(crit("伺服驱动", "急停回馈能量 ≤ 驱动器可吸收", s["E_regen"], drv["brake_energy_J"], s["E_regen"] <= drv["brake_energy_J"], "J"))
    s.update(Ic=Ic, Ip=Ip)
    return s, C

# ---------------------------------------------------------------- 电磁铁
def sol_angles(r, act, sol):
    kind = act[4]
    n = r["n_trim"] if kind == "trim" else r["n_bt"] if kind == "bt" else 0
    return n, 6*n*sol["t_on_ms"]/1000, 6*n*sol["t_off_ms"]/1000

def sol_check(r, act, sol):
    aid, nm, stroke, force, kind = act; C = []
    C.append(crit("电磁铁", f"{nm}：行程 ≥ {stroke} mm", sol["stroke_mm"], stroke, sol["stroke_mm"] >= stroke, "mm"))
    C.append(crit("电磁铁", f"{nm}：行程末端力 ≥ {force} N", sol["force_at_stroke_N"], force, sol["force_at_stroke_N"] >= force, "N"))
    n, a_on, a_off = sol_angles(r, act, sol)
    if kind == "trim":
        C.append(crit("电磁铁", f"{nm}：{n} r/min 下吸合/释放折算转角 ≤ 20°", max(a_on, a_off), K["sol_ang_max"], max(a_on, a_off) <= K["sol_ang_max"], "°"))
    if kind == "bt":
        C.append(crit("电磁铁", f"{nm}：{n} r/min 下切换转角 ≤ 空闲角 201.6°", max(a_on, a_off), K["bt_window"], max(a_on, a_off) <= K["bt_window"], "°"))
    return C

# ---------------------------------------------------------------- 直线轴（X–Y、横机机头）
def axis_travel(r, ax):
    if ax["travel"] is not None:
        return ax["travel"]
    k = r["knit"]; p = 25.4/k["E"]
    return k["needles"]*p+2*(k["cam_mm"]+r["v"]**2/(2*r["a"])*1000)

def axis_eval(r, ax, trans, mot, drv):
    """trans: ('belt', pulley size) 或 ('screw', screw size)"""
    v, a, m, F = r["v"], r["a"], ax["m"], ax["F"]
    L = axis_travel(r, ax)
    C = []; d = dict(L=L)
    Jm = mot["rotor_inertia_kgm2"]
    if trans[0] == "belt":
        pu = item("A-PUL-HTD", trans[1]); rr = pu["PD_mm"]/2000
        n = (v/rr)/RPM; alpha = a/rr
        Jx = 2*pu["J_kgm2"]
        T = (m*a+F)*rr/K["eta_belt"]+(Jm+Jx)*alpha
        belt = item("BUY-BELT", BELT_FOR[trans[1]])
        Lb = (L+150)/1000                       # 带的工作长度：行程 + 两端 75 mm
        kk = belt["EA_kN"]*1e3*(2/(Lb/2))       # 滑座在中间时最软：k = EA(1/L1 + 1/L2)
        fn = math.sqrt(kk/m)/(2*PI)
        d.update(r=rr, n=n, alpha=alpha, T=T, fn=fn, k=kk, Jx=Jx)
        C.append(crit(ax["name"], "同步带轴固有频率 ≥ 80 Hz", fn, K["fn_min"], fn >= K["fn_min"], "Hz"))
    else:
        sc = item("A-BSC-SFU", trans[1]); lead = sc["Ph_mm"]/1000
        n = v/lead*60; alpha = 2*PI*a/lead
        Ls = (L+150)/1000
        dr = (sc["d0_mm"]-sc["Dw_mm"])/1000
        Jsc = PI*K["rho_steel"]*Ls*dr**4/32
        Jc = item("A-CPL-JAW", "LM1")["J_kgm2"]
        Jx = Jsc+Jc
        T = (m*a+F)*lead/(2*PI*K["eta_screw"])+(Jm+Jx)*alpha
        DN = sc["d0_mm"]*n
        d.update(n=n, alpha=alpha, T=T, DN=DN, Jsc=Jsc, Jc=Jc, Jx=Jx)
        C.append(crit(ax["name"], "丝杠 d0·n ≤ 70000", DN, K["DN_max"], DN <= K["DN_max"]))
    kT = K["kT_closed"] if mot["closed_loop"] else K["kT_open"]
    Tav = step_torque(mot, n)
    d.update(Tav=Tav, kT=kT)
    C.append(crit(ax["name"], f"所需转矩 ≤ {kT} × {n:.0f} r/min 时的可用转矩", T, kT*Tav, T <= kT*Tav, "N·m"))
    C.append(crit(ax["name"], "驱动器电流 ≥ 电机额定、闭环电机配闭环驱动", drv["current_A"], mot["rated_current_A"],
                  drv["current_A"] >= mot["rated_current_A"] and (drv["closed_loop"] == mot["closed_loop"]), "A"))
    d["P"] = T*n*RPM/K["step_eff"]+K["step_idle"]
    return d, C

def fixed_step_eval(fs, mot, drv):
    aid, nm, T, n = fs
    kT = K["kT_closed"] if mot["closed_loop"] else K["kT_open"]
    Tav = step_torque(mot, n)
    C = [crit(nm, f"负载 {T} N·m ≤ {kT} × {n} r/min 时的可用转矩", T, kT*Tav, T <= kT*Tav, "N·m"),
         crit(nm, "驱动器电流 ≥ 电机额定、闭环电机配闭环驱动", drv["current_A"], mot["rated_current_A"],
              drv["current_A"] >= mot["rated_current_A"] and drv["closed_loop"] == mot["closed_loop"], "A")]
    return dict(T=T, n=n, P=T*n*RPM/K["step_eff"]+K["step_idle"]), C

def knit_eval(r, sel, enc, carriage_pulley):
    k = r["knit"]; p = 25.4/k["E"]; tn = p/r["v"]
    cyc = sel["t_on_ms"]+sel["t_off_ms"]
    pu = item("A-PUL-HTD", carriage_pulley)
    res = PI*pu["PD_mm"]/(4*enc["ppr"])
    n = r["v"]/(PI*pu["PD_mm"]/1000)*60
    C = [crit("选针", "选针器一次吸合+释放 ≤ 0.8 × 一针时间", cyc, K["sel_share"]*tn, cyc <= K["sel_share"]*tn, "ms"),
         crit("选针", "选针器行程 ≥ 0.3 mm、力 ≥ 2 N", sel["force_at_stroke_N"], 2, sel["stroke_mm"] >= 0.3 and sel["force_at_stroke_N"] >= 2, "N"),
         crit("机头编码器", "每个计数的机头位移 ≤ 0.01 针距", res, 0.01*p, res <= 0.01*p, "mm"),
         crit("机头编码器", "编码器转速 ≤ 允许转速", n, enc["max_rpm"], n <= enc["max_rpm"], "r/min")]
    return dict(p=p, tn=tn, cyc=cyc, res=res), C

# ---------------------------------------------------------------- I/O 与电源
def io_count(r, sol_list, step_list):
    """sol_list: [(名称, 编号)]；step_list: [(名称, 电机 size, 是否闭环)]"""
    enc = (1 if r.get("n_max") else 0)+(1 if r.get("knit") else 0)
    di = list(r["di"])+list(r.get("di_pedal", []))+[f"{nm}驱动报警" for nm, s, cl in step_list if cl]
    do = [f"{nm}电磁铁" for nm, sid in sol_list]+[f"{nm}方向" for nm, s, cl in step_list]+[f"{x[3]}" for x in r["pneu"] if x[0] == "D-PNU-VLV" for _ in range(x[2])]
    pwm = [f"{nm}脉冲" for nm, s, cl in step_list]
    ai = list(r["ai"])
    can = (1 if r.get("n_max") else 0)+1      # 伺服驱动器 + 网关
    return dict(enc=enc, di=di, do=do, pwm=pwm, ai=ai, can=can)

def ctl_check(io, ctl, nexp):
    exp = item("D-IO-EXP", "16")
    C = []
    tot = lambda k: ctl[k]+nexp*exp.get(k, 0)
    for k, nm in (("di", "数字输入 DI"), ("do", "数字输出 DO"), ("ai", "模拟输入 AI")):
        C.append(crit("主控与 I/O", f"{nm}：需要 ≤ 可用", len(io[k]), tot(k), len(io[k]) <= tot(k)))
    C.append(crit("主控与 I/O", "编码器输入：需要 ≤ 可用", io["enc"], ctl["encoder_inputs"], io["enc"] <= ctl["encoder_inputs"]))
    C.append(crit("主控与 I/O", "脉冲（PWM）通道：需要 ≤ 可用", len(io["pwm"]), ctl["pwm_ch"], len(io["pwm"]) <= ctl["pwm_ch"]))
    return C

def psu24_need(r, sols, hmi):
    hold = sum(item("D-SOL-PUSH", s)["hold_A"]**2*item("D-SOL-PUSH", s)["coil_R_ohm"] for s in sols)
    boost = max([24**2/item("D-SOL-PUSH", s)["coil_R_ohm"] for s in sols] or [0])
    P = K["P_logic"]+(K["P_hmi"] if hmi else 0)+hold+K["boost_share"]*boost
    return dict(hold=hold, boost=boost, P=P, need=K["psu_margin"]*P)

# ---------------------------------------------------------------- 自动配套：每类挑最便宜的满足判据的组合
def cheapest(cands, ok, cost):
    best = None
    for c in cands:
        if ok(c) and (best is None or cost(c) < cost(best)):
            best = c
    return best

def configure(key, r=None):
    r = copy.deepcopy(r or REQ[key])
    out = dict(key=key, req=r, bom=[], crits=[])
    def add(cat, size, qty, use, unit_price=None):
        it = item(cat, size)
        up = unit_price if unit_price is not None else it["price"]
        out["bom"].append(dict(id=cat, size=size, qty=qty, use=use, unit=up, sum=round(up*qty, 2)))
    # 主轴
    if r.get("n_max"):
        combos = [(m, d) for m in LIB["D-MOT-PMSM"]["sizes"] for d in LIB["D-DRV-SERVO"]["sizes"]]
        best = cheapest(combos, lambda c: all(x["ok"] for x in spindle_check(r, *c)[1]), lambda c: c[0]["price"]+c[1]["price"])
        m, d = best
        s, C = spindle_check(r, m, d); out["spindle"] = dict(s, mot=m["size"], drv=d["size"]); out["crits"] += C
        add("D-MOT-PMSM", m["size"], 1, "主轴"); add("D-DRV-SERVO", d["size"], 1, "主轴")
        add("A-CPL-JAW", "LM1", 1, "电机—主轴")
    # 电磁铁
    sols = []
    for act in r["actions"]:
        b = cheapest(LIB["D-SOL-PUSH"]["sizes"], lambda s: s["size"] != "SEL" and all(x["ok"] for x in sol_check(r, act, s)), lambda s: s["price"])
        out["crits"] += sol_check(r, act, b); sols.append((act[1], b["size"])); add("D-SOL-PUSH", b["size"], 1, act[1])
    # 横机：选针器、机头编码器
    steps = []
    if r.get("knit"):
        k = r["knit"]
        sel = cheapest(LIB["D-SOL-PUSH"]["sizes"], lambda s: all(x["ok"] for x in knit_eval(r, s, item("D-ENC-INC", "2500"), "3M-24-15")[1][:2]), lambda s: s["price"])
        enc = cheapest(LIB["D-ENC-INC"]["sizes"], lambda e: all(x["ok"] for x in knit_eval(r, sel, e, "3M-24-15")[1][2:]), lambda e: e["price"])
        kd, C = knit_eval(r, sel, enc, "3M-24-15"); out["knit"] = kd; out["crits"] += C
        for i in range(k["selectors"]):
            sols.append((f"选针器 {i+1}", sel["size"]))
        add("D-SOL-PUSH", sel["size"], k["selectors"], "选针器"); add("D-ENC-INC", enc["size"], 1, "机头位置")
    # 电磁铁驱动板
    nch = len(sols); pk = max(24/item("D-SOL-PUSH", s)["coil_R_ohm"] for _, s in sols); hk = max(item("D-SOL-PUSH", s)["hold_A"] for _, s in sols)
    def solok(b, n): return n*b["channels"] >= nch and b["peak_A"] >= pk and b["hold_A"] >= hk
    bestb = cheapest([(b, n) for b in LIB["D-DRV-SOL"]["sizes"] for n in (1, 2, 3)], lambda c: solok(*c), lambda c: c[0]["price"]*c[1])
    add("D-DRV-SOL", bestb[0]["size"], bestb[1], "电磁铁驱动")
    out["crits"].append(crit("电磁铁驱动", "通道数 ≥ 电磁铁数", bestb[1]*bestb[0]["channels"], nch, True))
    out["crits"].append(crit("电磁铁驱动", "峰值电流 ≥ 强激磁电流 24 V / R", bestb[0]["peak_A"], pk, bestb[0]["peak_A"] >= pk, "A"))
    # 直线轴
    out["axes"] = []
    trans = [("belt", s["size"]) for s in LIB["A-PUL-HTD"]["sizes"]]+[("screw", s["size"]) for s in LIB["A-BSC-SFU"]["sizes"]]
    for ax in r["axes"]:
        tlist = trans if ax["id"] != "C" else [("belt", s["size"]) for s in LIB["A-PUL-HTD"]["sizes"]]
        best = None
        for t in tlist:
            for m in LIB["D-MOT-STEP"]["sizes"]:
                for dv in LIB["D-DRV-STEP"]["sizes"]:
                    d, C = axis_eval(r, ax, t, m, dv)
                    if not all(x["ok"] for x in C):
                        continue
                    cost = m["price"]+dv["price"]+trans_cost(t, d["L"])
                    if best is None or cost < best[0]:
                        best = (cost, t, m, dv, d, C)
        cost, t, m, dv, d, C = best
        out["axes"].append(dict(id=ax["id"], name=ax["name"], trans=t, mot=m["size"], drv=dv["size"], d=d))
        out["crits"] += C
        add("D-MOT-STEP", m["size"], 1, ax["name"]); add("D-DRV-STEP", dv["size"], 1, ax["name"])
        for line in trans_lines(t, d["L"], ax["name"]):
            out["bom"].append(line)
        steps.append((ax["name"], m["size"], m["closed_loop"]))
    for fs in r["fixed_steps"]:
        best = None
        for m in LIB["D-MOT-STEP"]["sizes"]:
            for dv in LIB["D-DRV-STEP"]["sizes"]:
                d, C = fixed_step_eval(fs, m, dv)
                if all(x["ok"] for x in C) and (best is None or m["price"]+dv["price"] < best[0]):
                    best = (m["price"]+dv["price"], m, dv, d, C)
        _, m, dv, d, C = best
        out["crits"] += C; add("D-MOT-STEP", m["size"], 1, fs[1]); add("D-DRV-STEP", dv["size"], 1, fs[1])
        steps.append((fs[1], m["size"], m["closed_loop"])); out.setdefault("fixed", []).append(dict(fs=fs, d=d, mot=m["size"]))
    # 传感器、气动
    for cat, size, q, use in r["sensors"]+r["pneu"]:
        add(cat, size, q, use)
    # I/O 与主控
    io = io_count(r, sols, steps); out["io"] = io
    ctls = [(c, n) for c in LIB["D-CTL-WQSC"]["sizes"] for n in (0, 1, 2)]
    bc = cheapest(ctls, lambda c: all(x["ok"] for x in ctl_check(io, *c)), lambda c: c[0]["price"]+c[1]*item("D-IO-EXP", "16")["price"])
    out["crits"] += ctl_check(io, *bc)
    add("D-CTL-WQSC", bc[0]["size"], 1, "主控");
    if bc[1]:
        add("D-IO-EXP", "16", bc[1], "扩展 I/O")
    add("D-GW-WQSC", "E", 1, "联网")
    if r.get("hmi"):
        add("D-HMI-PANEL", "7", 1, "人机界面")
    # 电源
    p24 = psu24_need(r, [s for _, s in sols], r.get("hmi"))
    ps = cheapest([s for s in LIB["D-PSU-SMPS"]["sizes"] if s["V_out"] == 24], lambda s: s["P_W"] >= p24["need"], lambda s: s["price"])
    out["psu24"] = dict(p24, size=ps["size"]); add("D-PSU-SMPS", ps["size"], 1, "24 V：逻辑与电磁铁")
    out["crits"].append(crit("电源", "24 V 电源功率 ≥ 1.2 × 预算", ps["P_W"], p24["need"], True, "W"))
    if steps:
        P48 = sum(a["d"]["P"] for a in out["axes"])+sum(f["d"]["P"] for f in out.get("fixed", []))
        need = K["psu_margin"]*P48
        ps48 = cheapest([s for s in LIB["D-PSU-SMPS"]["sizes"] if s["V_out"] == 48], lambda s: s["P_W"] >= need, lambda s: s["price"])
        out["psu48"] = dict(P=P48, need=need, size=ps48["size"]); add("D-PSU-SMPS", ps48["size"], 1, "48 V：步进驱动")
        out["crits"].append(crit("电源", "48 V 电源功率 ≥ 1.2 × 预算", ps48["P_W"], need, True, "W"))
    out["total"] = round(sum(b["sum"] for b in out["bom"]), 2)
    return out

def trans_cost(t, L):
    if t[0] == "belt":
        pu = item("A-PUL-HTD", t[1]); b = item("BUY-BELT", BELT_FOR[t[1]])
        return 2*pu["price"]+b["price_per_m"]*belt_len(L)+2*item("A-LGD-RAIL", "HGH15CA")["price"]
    return item("A-BSC-SFU", t[1])["price"]+item("A-CPL-JAW", "LM1")["price"]+2*item("A-LGD-RAIL", "HGH15CA")["price"]

def belt_len(L):
    return round(2*(L+150)/1000+0.1, 1)       # 开口回绕：两倍工作长度 + 0.1 m

def trans_lines(t, L, use):
    rail = dict(id="A-LGD-RAIL", size="HGH15CA", qty=2, use=use, unit=140, sum=280)
    if t[0] == "belt":
        pu = item("A-PUL-HTD", t[1]); b = item("BUY-BELT", BELT_FOR[t[1]]); bl = belt_len(L)
        return [dict(id="A-PUL-HTD", size=t[1], qty=2, use=use, unit=pu["price"], sum=2*pu["price"]),
                dict(id="BUY-BELT", size=b["size"], qty=bl, use=use+"（m）", unit=b["price_per_m"], sum=round(b["price_per_m"]*bl, 2)), rail]
    sc = item("A-BSC-SFU", t[1])
    return [dict(id="A-BSC-SFU", size=t[1], qty=1, use=use, unit=sc["price"], sum=sc["price"]),
            dict(id="A-CPL-JAW", size="LM1", qty=1, use=use, unit=35, sum=35), rail]

# ---------------------------------------------------------------- 打印 19.4 节的数字
def main():
    np_ = lambda x, k=2: f"{x:.{k}f}"
    print("=== 19.4 平缝机原型 LS 算例 ===")
    r = REQ["LS"]
    for ms in ("250", "400", "550"):
        m = item("D-MOT-PMSM", ms); s = spindle_need(r, m)
        print(ms, "J_tot", s["J"], "alpha", np_(s["alpha"], 0), "T_acc", np_(s["T_acc"], 3), "0.8Tpk", 0.8*m["peak_torque_Nm"],
              "ratio", np_(s["ratio"], 1), "T_rms", np_(s["T_rms"], 3), "f_acc", s["f_acc"], "E", np_(s["E"], 1), "E_regen", np_(s["E_regen"], 1))
    cfg = configure("LS")
    sp = cfg["spindle"]
    print("chosen", sp["mot"], sp["drv"], "Ic", np_(sp["Ic"]), "Ip", np_(sp["Ip"]))
    print("min accel time with 2.5 N·m limit:", np_(6e-4*5000*RPM/(2.5-0.15), 3), " with 0.8*3.2:", np_(6e-4*5000*RPM/(0.8*3.2-0.15), 3))
    w = 5000*RPM
    print("omega", np_(w, 1), "trim speed deg/ms", 6*300/1000)
    for act in r["actions"]:
        for s in ("S8", "M15", "L30", "XL60"):
            sol = item("D-SOL-PUSH", s); n, a1, a2 = sol_angles(r, act, sol)
            print(" ", act[1], s, n, np_(a1, 1), np_(a2, 1), all(x["ok"] for x in sol_check(r, act, sol)))
    print("trim max speed for M15 (20 deg):", np_(20/(6*0.0069), 0))
    print("psu24", {k: np_(v, 1) if isinstance(v, float) else v for k, v in cfg["psu24"].items()})
    print("io", {k: (len(v) if isinstance(v, list) else v) for k, v in cfg["io"].items()}, cfg["io"])
    for b in cfg["bom"]:
        print("  BOM", b)
    print("total", cfg["total"])
    for c in cfg["crits"]:
        print("  ", "✓" if c["ok"] else "✗", c["group"], c["text"], np_(c["val"], 3) if isinstance(c["val"], float) else c["val"], np_(c["lim"], 3) if isinstance(c["lim"], float) else c["lim"])
    print("enc counts/rev 10000, res deg", 360/10000, "count rate at 5000", 5000/60*10000, "A freq", 5000/60*2500)
    print("HIL: deg per 50us at 5000", 5000/60*360*50e-6, "counts per 50us", 5000/60*10000*50e-6)
    print("at 300 r/min, 0.1deg in us", 0.1/(300*6)*1e6, " at 5000:", 0.1/(5000*6)*1e6)
    for key in ("OL", "PS", "FK"):
        c = configure(key)
        print(f"\n=== {key} === total", c["total"])
        if "spindle" in c:
            print(" spindle", c["spindle"]["mot"], c["spindle"]["drv"], np_(c["spindle"]["T_acc"], 3), np_(c["spindle"]["E_regen"], 1))
        for a in c.get("axes", []):
            print(" axis", a["id"], a["trans"], a["mot"], a["drv"], {k: (round(v, 4) if isinstance(v, float) else v) for k, v in a["d"].items()})
        if "knit" in c:
            print(" knit", c["knit"])
        print(" io", {k: (len(v) if isinstance(v, list) else v) for k, v in c["io"].items()})
        print(" psu", c["psu24"]["size"], round(c["psu24"]["need"], 1), c.get("psu48"))
        for b in c["bom"]:
            print("   ", b["id"], b["size"], b["qty"], b["use"], b["sum"])
        bad = [x for x in c["crits"] if not x["ok"]]
        print(" bad", bad)
    # 包缝机提速到 7000
    r7 = copy.deepcopy(REQ["OL"]); r7["n_max"] = 7000
    c7 = configure("OL", r7); print("\nOL7000", c7["spindle"]["mot"], c7["spindle"]["drv"], c7["total"], np_(c7["spindle"]["T_acc"], 3), np_(c7["spindle"]["E_regen"], 1))
    m400 = item("D-MOT-PMSM", "400"); s, C = spindle_check(r7, m400, item("D-DRV-SERVO", "3A"))
    print(" with 400/3A:", [(x["text"], round(x["val"], 2), x["ok"]) for x in C])
    s, C = spindle_check(r7, item("D-MOT-PMSM", "550"), item("D-DRV-SERVO", "3A"))
    print(" with 550/3A:", [(x["text"], round(x["val"], 2), x["ok"]) for x in C])
    # 花样机丝杠方案
    rp = REQ["PS"]
    for ax in rp["axes"]:
        for t in (("screw", "16x10"), ("screw", "16x5"), ("belt", "3M-24-15"), ("belt", "GT2-20-9")):
            for ms in ("23-22C", "34-45C", "34-85C"):
                d, C = axis_eval(rp, ax, t, item("D-MOT-STEP", ms), item("D-DRV-STEP", "C6A"))
                print(" PS", ax["id"], t, ms, "n", round(d["n"]), "T", round(d["T"], 3), "kTav", round(d["kT"]*d["Tav"], 3),
                      "DN", round(d.get("DN", 0)), "fn", round(d.get("fn", 0), 1), "Jx", d["Jx"], all(x["ok"] for x in C))
    # 丝杠：如果联轴器惯量只有 2e-5（库里没有这样的规格）
    LIB["A-CPL-JAW"]["sizes"][0]["J_kgm2"] = 2e-5
    for a_ in (25, 10, 5):
        rr = copy.deepcopy(rp); rr["a"] = a_
        for vv in (0.5, 0.2):
            rr["v"] = vv
            ok = []
            for ax in rr["axes"]:
                d, C = axis_eval(rr, ax, ("screw", "16x10"), item("D-MOT-STEP", "34-45C"), item("D-DRV-STEP", "C6A"))
                ok.append((ax["id"], round(d["T"], 3), round(d["kT"]*d["Tav"], 3), all(x["ok"] for x in C)))
            print(" small-coupling screw a", a_, "v", vv, ok)
    LIB["A-CPL-JAW"]["sizes"][0]["J_kgm2"] = 2e-4
    # 选针器
    rf = copy.deepcopy(REQ["FK"])
    for E in (5, 7):
        for v in (0.3, 0.5, 0.8):
            rf["knit"]["E"] = E; rf["v"] = v
            p = 25.4/E; tn = p/v*1e3
            print(" FK E", E, "v", v, "p", round(p, 2), "tn", round(tn/1e3, 2), "0.8tn", round(0.8*tn, 2), "S8 ok", 9.5 <= 0.8*tn/1e3, "M15 ok", 12 <= 0.8*tn/1e3)
    json.dump(dict(LIB=LIB, K=K, REQ=REQ, BELT_FOR=BELT_FOR), open(os.path.join(os.path.dirname(__file__), "ch19_lib.json"), "w"), ensure_ascii=False, indent=0)

if __name__ == "__main__":
    main()
