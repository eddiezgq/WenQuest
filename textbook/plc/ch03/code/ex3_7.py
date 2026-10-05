"""3.7 节：上料输送线的 PLC 选型计算书（I/O 点数与余量、24 V 电源容量、响应时间的粗算）。
I/O 来自第 1、2 章和任务单 TS-2-1：急停、启动、停止、反转点动、热继电器、入口与末端光电、两个接触器的辅助触点；
两个接触器、两盏灯。余量取 20 %～30 %，按常见的一体式 PLC 规格向上取。"""
import math
from bookout import out

DI = ["S1_Start", "S2_Stop", "S0_EStop", "F1_Overload", "B1_Entry", "B2_End", "S3_RevJog", "KM1_Aux", "KM2_Aux"]
DO = ["KM1_Run", "H1_Run", "H2_Fault", "KM2_Rev"]
SPARE = 0.25
di_need, do_need = math.ceil(len(DI) * (1 + SPARE)), math.ceil(len(DO) * (1 + SPARE))
SIZES = [(8, 6), (14, 10), (24, 16)]            # common compact PLC sizes (inputs, outputs)
di_cpu, do_cpu = next((i, o) for i, o in SIZES if i >= di_need and o >= do_need)
# 24 V budget, mA: inputs ~4 mA each, photo sensors ~30 mA each, contactor coils 100 mA (both counted), lamps 25 mA, CPU's own 24 V use (assumed 300 mA)
load = {"inputs": len(DI) * 4, "sensors": 2 * 30, "coils": 2 * 100, "lamps": 2 * 25, "cpu": 300}
total = sum(load.values())
psu = next(a for a in (1.3, 2.5, 5.0, 10.0) if a * 1000 >= total * 1.3)
# response: input filter 3 ms + up to two scans of 10 ms + output transistor 0.5 ms + contactor 20 ms
resp = 3 + 2 * 10 + 0.5 + 20
out(n_di=len(DI), n_do=len(DO), di_need=di_need, do_need=do_need, di_cpu=di_cpu, do_cpu=do_cpu, spare_di=di_cpu - len(DI), spare_do=do_cpu - len(DO),
    total_ma=total, psu=psu, resp=resp)
