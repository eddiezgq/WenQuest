# -*- coding: utf-8 -*-
"""仿真车间：离散事件仿真。

- 设备按工厂数据的工作中心建模；热处理炉可同时装 20 件，其余设备一次一件。
- 工单按工艺路线逐工序流转，零件逐件传递：上一道做完一件，AGV 就把它送到下一道。
- 每道工序要先“派工”（dispatch），再由操作工在车间终端点“开工”（start）才会加工；
  自动模式（auto_start）下派工即开工，用于生产模式演示和自动测试。
- 刀具（砂轮）随加工磨损，寿命低于 8% 自动换刀；磨床砂轮越磨损，轴承位直径越偏大，
  这就是控制图上“测量值上移、趋近上限”的来源。
- 故障注入（inject_fault）只在教学模式下接受，供教师制造“磨床停机”一类情景。

时间：仿真时钟 = 真实时间 × 倍速。信封 ts 用真实时间（消息何时发出），
cycle_time_s、duration_s 等业务时长用仿真秒（零件实际要加工多久）。
"""
import datetime as dt
import heapq
import itertools
import random
import time
from collections import deque

from wqbus import UNITS, layout
from wqbus.topics import unit_topic

# 工序 → 可用设备（第一个是默认设备）
OP_UNITS = {
    "下料 Sawing": ["saw-01"],
    "粗车 Rough turning": ["cnc-l01-a", "cnc-l01-b"],
    "精车 Finish turning": ["cnc-l01-b", "cnc-l01-a"],
    "调质 Quench & temper": ["ht-01"],
    "渗碳淬火 Carburizing": ["ht-01"],
    "铣键槽 Keyway milling": ["key-01"],
    "滚齿 Gear hobbing": ["hob-01"],
    "磨外圆 Cylindrical grinding": ["grd-01"],
    "铣结合面 Face milling": ["vmc-01"],
    "钻攻螺纹孔 Drilling & tapping": ["vmc-01"],
    "合箱钻铰销孔 Pin-hole reaming": ["hmc-01"],
    "镗轴承孔 Bearing-bore boring": ["hmc-01"],
    "零件检验 Part inspection": ["qc-01"],
    "部件装配 Sub-assembly": ["asm-01"],
    "总装 Final assembly": ["asm-01"],
    "跑合试验 Run-in test": ["test-01"],
    "出厂检验 Final inspection": ["qc-01"],
    "清洗包装 Cleaning & packing": ["asm-01"],
}
CAPACITY = {"ht-01": 20}
SETUP_MIN = {"cnc-l01-a": 10, "cnc-l01-b": 10, "grd-01": 8, "key-01": 6, "saw-01": 3, "ht-01": 5, "qc-01": 2}
WEAR_PER_PART = {"saw-01": 1 / 200, "cnc-l01-a": 1 / 60, "cnc-l01-b": 1 / 60, "key-01": 1 / 40,
                 "grd-01": 1 / 30, "hob-01": 1 / 40, "vmc-01": 1 / 80, "hmc-01": 1 / 80}
SPINDLE = {"saw-01": (60, 40), "cnc-l01-a": (900, 180), "cnc-l01-b": (1400, 90), "key-01": (1200, 80),
           "grd-01": (1800, 400), "hob-01": (300, 60), "vmc-01": (2500, 600), "hmc-01": (2000, 400)}
TOOL_CHANGE_MIN = {"grd-01": 8}
RATED_TORQUE_NM = {"WQR-105": 350.0}   # 额定输出转矩（与参数配置器一致）   # 磨床“换刀”即修整或更换砂轮
AGV_SPEED = 1.0                   # m/s（仿真）
LOAD_UNLOAD_S = 30

# 输出轴检验特性：(特性代号, 中文, 名义, 下限, 上限) —— 与工厂数据“零件检验-输出轴”一致
SH301_CHARS = [
    ("bearing_seat_d35", "轴承位直径 Ø35 k6", 35.010, 35.002, 35.018),
    ("gear_seat_d40", "齿轮位直径 Ø40 k6", 40.010, 40.002, 40.018),
    ("keyway_width_12", "键槽宽 12 N9", 11.9785, 11.957, 12.000),
]


class Clock:
    """仿真时钟：sim = t0_sim + (wall - t0_wall) × speed。"""

    def __init__(self, speed=20.0, wall=time.time):
        self.speed, self.wall = float(speed), wall
        self.t0_wall = wall()
        self.t0_sim = 0.0

    def now(self):
        return self.t0_sim + (self.wall() - self.t0_wall) * self.speed

    def set_speed(self, speed):
        self.t0_sim, self.t0_wall, self.speed = self.now(), self.wall(), float(speed)


class Part:
    def __init__(self, serial, wo):
        self.serial, self.wo = serial, wo
        self.op_index = 0
        self.grind_wear = 0.0     # 磨削时砂轮已磨损的比例 0–1
        self.result = None


class Job:
    """一台设备上的一道工序（某工单的第 k 道）。"""

    def __init__(self, wo, op_index, unit):
        self.wo, self.op_index, self.unit = wo, op_index, unit
        self.op, self.std_min = wo.ops[op_index]
        self.qty = wo.qty
        self.started = False
        self.done = 0
        self.good = 0
        self.time_s = 0.0        # 累计加工时长（仿真秒）
        self.first_start = None

    @property
    def key(self):
        return (self.wo.name, self.op_index)


class WorkOrder:
    def __init__(self, name, item, qty, ops, corr=None):
        self.name, self.item, self.qty = name, item, qty
        self.ops = ops            # [(工序名, 每件分钟)]
        self.corr = corr or name
        tag = name.split("-")[-1]
        self.parts = [Part("{}-{}-{:02d}".format(item.replace("-", ""), tag, i + 1), self) for i in range(qty)]
        self.jobs = {}            # op_index → Job


class Machine:
    def __init__(self, unit):
        self.unit = unit
        self.capacity = CAPACITY.get(unit, 1)
        self.jobs = []            # 已派工的 Job，按派工顺序
        self.inbox = deque()      # 已送到、等待加工的零件
        self.active = {}          # token → (part, job, start, end)
        self.state = "idle"
        self.setup_until = None
        self.setup_job = None     # 最近一次调整针对的工序，同工序连续加工不再调整
        self.down_until = None
        self.down_reason = ""
        self.down_kind = "down"
        self.tool_life = 1.0
        self.last_status = None


class AGV:
    def __init__(self, unit, pos):
        self.unit, self.pos = unit, pos
        self.task = None          # dict(path, start, dist, part, frm, to)
        self.battery = 0.9
        self.heading = 0.0


class Engine:
    def __init__(self, publish, clock=None, mode="teach", auto_start=False, seed=None, status_every_s=2.0):
        """publish(topic, type, source, data, corr) —— 由 main.py 接到总线；测试里接到列表。"""
        self.pub = publish
        self.clock = clock or Clock()
        self.mode = mode
        self.auto_start = auto_start
        self.rng = random.Random(seed)
        self.status_every_s = status_every_s
        self.q = []               # 事件堆：(sim_t, seq, kind, payload)
        self.seq = itertools.count()
        self.machines = {u: Machine(u) for u in UNITS if u in _MACHINE_UNITS}
        self.agvs = {u: AGV(u, layout.AGV_HOME[u]) for u in ("agv-01", "agv-02")}
        self.transfers = deque()  # 等 AGV 的搬运：(part, frm, to)
        self.wos = {}
        self.tokens = itertools.count(1)
        self._last_periodic = -1e9
        # 仿真 0 秒对应的工厂时间：默认为引擎创建时的真实时间；教学情景会改成情景开始的时刻
        self.epoch = dt.datetime.now(dt.timezone.utc) - dt.timedelta(seconds=self.clock.now())

    # ------------------------------------------------------------ 基础
    def now(self):
        return self.clock.now()

    def factory_ts(self, t=None):
        """工厂时间：仿真时刻换算成日历时间（倍速运行时比真实时间走得快）。ERPNext 的工时按它记。"""
        t = self.now() if t is None else t
        v = self.epoch + dt.timedelta(seconds=t)
        return v.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    def at(self, t, kind, **payload):
        heapq.heappush(self.q, (t, next(self.seq), kind, payload))

    def publish_all_status(self):
        for m in self.machines.values():
            self._status(m, force=True)
        for a in self.agvs.values():
            self._agv_status(a)

    def run_due(self):
        """处理所有到期事件；定期发状态。返回处理的事件数。"""
        n = 0
        while self.q and self.q[0][0] <= self.now():
            t, _, kind, p = heapq.heappop(self.q)
            getattr(self, "_ev_" + kind)(t, **p)
            n += 1
        wall = time.time()
        if wall - self._last_periodic >= self.status_every_s:
            self._last_periodic = wall
            for m in self.machines.values():
                if m.state in ("run", "setup") or m.last_status is None:
                    self._status(m, force=True)
            for a in self.agvs.values():
                if a.task:
                    self._agv_status(a)
        return n

    def next_event_time(self):
        return self.q[0][0] if self.q else None

    # ------------------------------------------------------------ 指令
    def command(self, unit, data, corr=None):
        """处理一条 machine.cmd，返回 (accepted, reason)，并在总线上应答。"""
        ok, reason = self._command(unit, data, corr)
        if unit in self.machines:
            self.pub(unit_topic(unit, "cmd/ack"), "machine.ack", "sim/" + unit,
                     {"accepted": ok, "reason": reason, "command": data.get("command"),
                      "work_order": data.get("work_order"), "operation": data.get("operation")}, corr)
        return ok, reason

    def _command(self, unit, d, corr):
        m = self.machines.get(unit)
        if m is None:
            return False, "没有这台设备：" + unit
        cmd = d["command"]
        if cmd == "dispatch":
            wo = self.wos.get(d.get("work_order"))
            if wo is None:
                if not d.get("routing"):
                    return False, "未知工单，派工时需附工艺路线"
                wo = WorkOrder(d["work_order"], d.get("item", "SH-301"), int(d.get("qty", 1)),
                               [tuple(x) for x in d["routing"]], corr)
                self.wos[wo.name] = wo
            idx = self._op_index(wo, d.get("operation"))
            if idx is None:
                return False, "工单 {} 的工艺路线里没有工序 {}".format(wo.name, d.get("operation"))
            if unit not in OP_UNITS.get(wo.ops[idx][0], []):
                return False, "{} 不能做 {}".format(UNITS[unit][1], wo.ops[idx][0])
            if idx in wo.jobs:
                return False, "该工序已派给 {}".format(wo.jobs[idx].unit)
            job = Job(wo, idx, unit)
            wo.jobs[idx] = job
            m.jobs.append(job)
            # 已经送到别的设备、等这道工序的零件，改送到这台
            for other in self.machines.values():
                if other is not m:
                    for p in [p for p in other.inbox if p.wo is wo and p.op_index == idx]:
                        other.inbox.remove(p)
                        m.inbox.append(p)
            if idx == 0:          # 第一道：原材料在锯床旁，派工即到料
                for p in wo.parts:
                    m.inbox.append(p)
            if self.auto_start:
                job.started = True
            self._try_start(m)
            self._status(m)
            return True, "已派工"
        if cmd == "start":
            job = self._find_job(m, d)
            if job is None:
                return False, "这台设备上没有该工序的派工"
            job.started = True
            self._try_start(m)
            self._status(m)
            if m.state in ("down", "fault"):
                return True, "设备{}中，已登记开工，恢复后自动开始".format("停机" if m.state == "down" else "故障")
            return True, "已开工"
        if cmd == "pause":
            job = self._find_job(m, d)
            if job is None:
                return False, "这台设备上没有该工序的派工"
            job.started = False
            self._status(m)
            return True, "当前件做完后暂停"
        if cmd == "reset":
            if m.state not in ("down", "fault"):
                return True, "设备正常，无需复位"
            self._recover(m, self.now(), manual=True)
            return True, "已复位"
        if cmd == "inject_fault":
            if self.mode != "teach":
                return False, "生产模式不接受故障注入"
            minutes = float(d.get("minutes", 30))
            kind = "fault" if d.get("kind") == "fault" else "down"
            self._go_down(m, self.now(), minutes * 60, d.get("reason", "设备故障"), kind)
            return True, "已注入：{} {} 分钟".format(d.get("reason", "故障"), minutes)
        return False, "不支持的指令 " + cmd

    def _op_index(self, wo, op):
        if op is None:
            return None
        for i, (name, _) in enumerate(wo.ops):
            if name == op or name.split(" ")[0] == op:
                return i
        return None

    def _find_job(self, m, d):
        for j in m.jobs:
            if j.wo.name == d.get("work_order") and (d.get("operation") is None or
                                                    j.op == d["operation"] or j.op.split(" ")[0] == d["operation"]):
                return j
        return None

    # ------------------------------------------------------------ 加工
    def _startable(self, m):
        """inbox 中第一件其工序已开工的零件。"""
        for p in list(m.inbox):
            job = p.wo.jobs.get(p.op_index)
            if job and job.unit == m.unit and job.started:
                return p, job
        return None, None

    def _try_start(self, m):
        t = self.now()
        while len(m.active) < m.capacity:
            if m.state in ("down", "fault") or (m.setup_until and m.setup_until > t):
                return
            p, job = self._startable(m)
            if p is None:
                break
            if m.setup_job != job.key and not m.active:
                # 新工序先调整（装夹、对刀、调程序）
                m.setup_job = job.key
                dur = SETUP_MIN.get(m.unit, 5) * 60
                m.setup_until = t + dur
                m.state = "setup"
                self.at(m.setup_until, "setup_done", unit=m.unit)
                self._status(m)
                return
            m.inbox.remove(p)
            std = job.std_min * 60
            wear = 1 - m.tool_life
            factor = self.rng.uniform(0.96, 1.10) + 0.08 * wear
            dur = std * factor
            tok = next(self.tokens)
            m.active[tok] = (p, job, t, t + dur)
            if job.first_start is None:
                job.first_start = t
            m.state = "run"
            if m.unit == "grd-01":
                p.grind_wear = wear
            self.at(t + dur, "cycle_end", unit=m.unit, token=tok)
            self.pub(unit_topic(m.unit, "event"), "machine.event", "sim/" + m.unit,
                     {"event": "cycle_start", "work_order": job.wo.name, "operation": job.op,
                      "op_index": job.op_index, "n_ops": len(job.wo.ops), "item": job.wo.item,
                      "part_serial": p.serial, "std_time_s": std, "factory_ts": self.factory_ts(t)}, job.wo.corr)
        if not m.active and m.state not in ("down", "fault") and not (m.setup_until and m.setup_until > t):
            m.state = "idle"
        self._status(m)

    def _ev_setup_done(self, t, unit):
        m = self.machines[unit]
        if m.setup_until and m.setup_until <= t + 1e-6:
            m.setup_until = None
            if m.state == "setup":
                m.state = "idle"
            self._try_start(m)

    def _ev_cycle_end(self, t, unit, token):
        m = self.machines[unit]
        if token not in m.active:
            return                          # 停机时被顺延，旧事件作废
        p, job, start, end = m.active.pop(token)
        ct = end - start
        job.done += 1
        job.time_s += ct
        m.tool_life = max(0.0, m.tool_life - WEAR_PER_PART.get(unit, 0))
        corr = job.wo.corr
        if unit == "qc-01" and job.wo.item == "SH-301":
            p.result = self._measure(p, corr)
        if unit == "test-01":
            self._torque_log(p, job, corr)
        good = p.result != "fail" if unit == "qc-01" else True
        if good:
            job.good += 1
        self.pub(unit_topic(unit, "event"), "machine.event", "sim/" + unit,
                 {"event": "cycle_end", "work_order": job.wo.name, "operation": job.op,
                  "op_index": job.op_index, "n_ops": len(job.wo.ops), "item": job.wo.item,
                  "part_serial": p.serial, "cycle_time_s": round(ct, 1),
                  "factory_ts": self.factory_ts(end), "factory_start_ts": self.factory_ts(start),
                  "std_time_s": job.std_min * 60, "good": good, "qty_done": job.done, "qty": job.qty}, corr)
        if job.done == job.qty:
            self.pub(unit_topic(unit, "event"), "machine.event", "sim/" + unit,
                     {"event": "op_complete", "work_order": job.wo.name, "operation": job.op,
                      "op_index": job.op_index, "qty": job.qty, "qty_good": job.good,
                      "time_s": round(job.time_s, 1), "item": job.wo.item, "factory_ts": self.factory_ts(t),
                      "last_op": job.op_index == len(job.wo.ops) - 1}, corr)
            m.jobs.remove(job)
        # 送下一道
        p.op_index += 1
        if p.op_index < len(job.wo.ops):
            nxt = job.wo.jobs.get(p.op_index)
            to = nxt.unit if nxt else OP_UNITS[job.wo.ops[p.op_index][0]][0]
            self.transfers.append((p, unit, to))
            self._dispatch_agvs()
        else:
            self.transfers.append((p, unit, "store-02"))
            self._dispatch_agvs()
        # 换刀
        if unit in WEAR_PER_PART and m.tool_life < 0.08:
            self.pub(unit_topic(unit, "event"), "machine.event", "sim/" + unit,
                     {"event": "tool_change", "message": "砂轮修整" if unit == "grd-01" else "换刀",
                      "tool_life_before": round(m.tool_life, 3)}, corr)
            m.tool_life = 1.0
            dur = TOOL_CHANGE_MIN.get(unit, 5) * 60
            m.setup_until = t + dur
            m.state = "setup"
            self.at(m.setup_until, "setup_done", unit=unit)
        self._try_start(m)

    def _torque_log(self, p, job, corr):
        """跑合试验台的“工况模拟”段：带式输送机 启动—运行—停机 × 3，输出轴转矩 10 Hz（第 11 轮疲劳寿命用）"""
        import math
        tr = RATED_TORQUE_NM.get(job.wo.item, 350.0)
        import zlib
        rng = random.Random(zlib.crc32((p.serial + job.wo.name).encode()))   # 同一件每次一样
        rate, out = 10.0, []
        for _ in range(3):
            peak = tr * rng.uniform(1.5, 1.7)                 # 电机起动转矩冲击
            mean = tr * rng.uniform(0.70, 0.80)               # 带上物料，稳定运行
            for i in range(int(25 * rate)):
                t = i / rate
                if t < 1:
                    v = peak * t
                elif t < 2:
                    v = mean + (peak - mean) * math.exp(-4 * (t - 1))
                elif t < 22:
                    v = mean + 0.08 * tr * math.sin(2 * math.pi * 0.5 * t) + rng.gauss(0, 0.03 * tr)
                elif t < 23:
                    v = mean * (23 - t)
                else:
                    v = rng.gauss(0, 0.005 * tr)
                out.append(round(v, 1))
        self.pub(unit_topic("test-01", "torque"), "test.torque", "sim/test-01",
                 {"item": job.wo.item, "part_serial": p.serial, "work_order": job.wo.name, "rate_hz": rate,
                  "samples_nm": out, "duration_s": len(out) / rate, "rated_nm": tr,
                  "program": "工况模拟：带式输送机 启动—运行—停机 × 3"}, corr)

    def _measure(self, p, corr):
        result = "pass"
        for code, name, nom, lo, hi in SH301_CHARS:
            if code == "bearing_seat_d35":
                mean = 35.0065 + 0.0125 * p.grind_wear
                sd = 0.0012
            else:
                mean, sd = nom, (hi - lo) / 10
            v = round(self.rng.gauss(mean, sd), 4)
            r = "pass" if lo <= v <= hi else "fail"
            if r == "fail":
                result = "fail"
            self.pub(unit_topic("qc-01", "measurement"), "quality.measurement", "sim/qc-01",
                     {"part_serial": p.serial, "item": p.wo.item, "work_order": p.wo.name,
                      "characteristic": code, "name": name, "nominal_mm": nom,
                      "lower_tol_mm": lo, "upper_tol_mm": hi, "value_mm": v, "result": r,
                      "n_chars": len(SH301_CHARS), "factory_ts": self.factory_ts()}, corr)
        return result

    # ------------------------------------------------------------ 停机
    def _go_down(self, m, t, dur_s, reason, kind="down"):
        m.state = kind
        m.down_reason, m.down_kind = reason, kind
        m.down_until = t + dur_s
        m.down_since = t
        self.pub(unit_topic(m.unit, "event"), "machine.event", "sim/" + m.unit,
                 {"event": "fault" if kind == "fault" else "alarm", "code": "E-" + m.unit.upper(),
                  "message": reason, "expected_duration_s": dur_s}, None)
        self.at(m.down_until, "recover", unit=m.unit, until=m.down_until)
        self._status(m, force=True)

    def _ev_recover(self, t, unit, until):
        m = self.machines[unit]
        if m.down_until == until:
            self._recover(m, t)

    def _recover(self, m, t, manual=False):
        lost = t - getattr(m, "down_since", t)
        # 被打断的件顺延停机时长
        for tok, (p, job, s, e) in list(m.active.items()):
            ntok = next(self.tokens)
            del m.active[tok]
            m.active[ntok] = (p, job, s, e + lost)
            self.at(e + lost, "cycle_end", unit=m.unit, token=ntok)
        m.down_until = None
        m.state = "run" if m.active else "idle"
        self.pub(unit_topic(m.unit, "event"), "machine.event", "sim/" + m.unit,
                 {"event": "recover", "message": ("人工复位：" if manual else "") + m.down_reason,
                  "downtime_s": round(lost, 1)}, None)
        self._try_start(m)

    # ------------------------------------------------------------ AGV
    def _dispatch_agvs(self):
        t = self.now()
        for a in self.agvs.values():
            if not self.transfers:
                return
            if a.task:
                continue
            p, frm, to = self.transfers.popleft()
            src, dst = layout.dock(frm), layout.dock(to)
            path = layout.route(a.pos, src)[:-1] + layout.route(src, dst) if a.pos != src else layout.route(src, dst)
            dist = layout.length(path)
            dur = dist / AGV_SPEED + 2 * LOAD_UNLOAD_S
            a.task = {"path": path, "start": t, "end": t + dur, "part": p, "frm": frm, "to": to, "dist": dist}
            a.battery = max(0.2, a.battery - dist / 20000)
            self.at(t + dur, "agv_arrive", unit=a.unit)
            self._agv_status(a)

    def _ev_agv_arrive(self, t, unit):
        a = self.agvs[unit]
        task = a.task
        a.pos = task["path"][-1]
        a.task = None
        self._agv_status(a)
        p, to = task["part"], task["to"]
        if to in self.machines:
            self.machines[to].inbox.append(p)
            self._try_start(self.machines[to])
        self._dispatch_agvs()

    def _agv_status(self, a):
        t = self.now()
        if a.task:
            tk = a.task
            f = (t - tk["start"]) / max(1e-6, tk["end"] - tk["start"])
            travel = max(0.0, min(1.0, (t - tk["start"] - LOAD_UNLOAD_S) / max(1e-6, tk["end"] - tk["start"] - 2 * LOAD_UNLOAD_S)))
            (x, y), a.heading = layout.point_at(tk["path"], travel * tk["dist"])
            data = {"x_m": round(x, 2), "y_m": round(y, 2), "heading_deg": round(a.heading, 1),
                    "load": tk["part"].serial, "task": "{} → {}".format(tk["frm"], tk["to"]),
                    "from": tk["frm"], "to": tk["to"], "progress": round(max(0, min(1, f)), 3),
                    "battery": round(a.battery, 3)}
            corr = tk["part"].wo.corr
        else:
            data = {"x_m": a.pos[0], "y_m": a.pos[1], "heading_deg": round(a.heading, 1), "load": None,
                    "task": None, "battery": round(a.battery, 3)}
            corr = None
        self.pub(unit_topic(a.unit, "status"), "logistics.status", "sim/" + a.unit, data, corr)

    # ------------------------------------------------------------ 状态
    def _status(self, m, force=False):
        t = self.now()
        job, prog, serial = None, 0.0, None
        if m.active:
            vals = list(m.active.values())
            p, job, s, e = vals[0]
            serial = p.serial if len(vals) == 1 else "{} 件在炉".format(len(vals))
            prog = sum(max(0, min(1, (t - s) / max(1e-6, e - s))) for _, _, s, e in vals) / len(vals)
        elif m.jobs:
            job = next((j for j in m.jobs if j.started), m.jobs[0])
        rpm, feed = SPINDLE.get(m.unit, (0, 0))
        running = m.state == "run"
        waiting = sum(1 for p in m.inbox)
        data = {
            "state": m.state,
            "work_order": job.wo.name if job else None,
            "operation": job.op if job else None,
            "item": job.wo.item if job else None,
            "part_serial": serial,
            "progress": round(prog, 3),
            "qty_done": job.done if job else 0,
            "qty": job.qty if job else 0,
            "job_started": bool(job and job.started),
            "queue": waiting,
            "spindle_rpm": rpm if running else 0,
            "feed_mm_min": feed if running else 0,
            "tool_life_left": round(m.tool_life, 3),
            "reason": m.down_reason if m.state in ("down", "fault") else None,
            "down_until_s": round(m.down_until - t) if m.down_until else None,
            "down_for_s": round(t - m.down_since) if m.state in ("down", "fault") else None,
            "dispatched": [{"work_order": j.wo.name, "operation": j.op, "started": j.started,
                            "done": j.done, "qty": j.qty} for j in m.jobs],
        }
        key = (data["state"], data["work_order"], data["operation"], data["qty_done"], data["queue"],
               data["job_started"], len(data["dispatched"]))
        if not force and key == m.last_status:
            return
        m.last_status = key
        self.pub(unit_topic(m.unit, "status"), "machine.status", "sim/" + m.unit, data,
                 job.wo.corr if job else None)


_MACHINE_UNITS = {"saw-01", "cnc-l01-a", "cnc-l01-b", "vmc-01", "hmc-01", "key-01", "hob-01",
                  "ht-01", "grd-01", "qc-01", "asm-01", "test-01"}


def routing_for(item):
    """从工厂数据取某物料的工艺路线 [(工序, 分钟)]。"""
    from factory import data
    rt = data.BOMS[item][0]
    return [list(x) for x in data.ROUTINGS[rt]]


def expected_minutes(item, qty):
    """整批按单件流动的理论完工时间（分钟），供测试和 AI 估算用：瓶颈工序 × 件数 + 其余工序各一件。"""
    ops = routing_for(item)
    t = [m for _, m in ops]
    bottleneck = max(m for op, m in ops if op != "调质 Quench & temper")
    return sum(t) + bottleneck * (qty - 1)

