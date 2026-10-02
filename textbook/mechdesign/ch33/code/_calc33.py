"""第 33 章的设计计算书：SH-301 输出轴（B 版）的受力、静强度、疲劳、刚度、临界转速。

工程任务单 TS-33-1 用 ``sheet()`` 导出发给学生的空白计算书（公式和出处已填、结果留空，见 textbook/tools/tasksheet.py）。
数字与 33.4–33.7 节的算例同一套函数（_shaft.py）。台阶处的理论应力集中系数这里用 [SHI] 的首轮估计（大圆角），
学生按 33.5.4 节用有限元或 [PET] 图表换成自己的值；疲劳寿命由数字工厂“仿真与分析”算出后填入。
"""
import math

import mdstd
from calcsheet import CalcSheet

import _shaft as S


def sheet(mat_id="40Cr-QT"):
    mat = mdstd.material(mat_id)
    cs = CalcSheet("SH-301 输出轴（B 版）设计计算书", item="SH-301", rev="B", task="TS-33-1")
    T = cs.given("T", S.T_RATED / 1e3, "N·m", "额定输出转矩（已含工况系数）", src="数字工厂参数配置器 T_RATED")
    cs.given("n", S.N_OUT, "r/min", "输出转速", src="1450 r/min ÷ 10.5")
    cs.given("d₂", S.D_GEAR, "mm", "GR-302 分度圆直径", src="m z = 3 × 70")
    cs.given("α", 20, "°", "压力角", src="GB/T 1356")
    cs.given("a, L", f"{S.Z_GEAR - S.Z_BRG_A:g} / {S.SPAN:g}", "mm", "齿轮到左轴承的距离、跨距", src="B 版结构（33.2 节）")
    cs.given("σb / σs / σ₋₁ / τ₋₁", f"{mat['sigma_b']:g} / {mat['sigma_s']:g} / {mat['sigma_1']:g} / {mat['tau_1']:g}", "MPa",
             f"材料性能（{mat['name']}）", src=mat["src"])
    cs.given("[S]", 1.5, "", "许用安全系数", src="33.5.5 节")
    cs.given("L_req", S.LIFE_H, "h", "要求寿命（频繁起停）", src="客户要求；任务单 TS-33-1")
    cs.find("S_static, S_ca", "四个截面的静强度、疲劳安全系数")
    cs.find("θ_A, θ_B, n_c1, L_h", "轴承处转角、一阶临界转速、疲劳寿命")

    Ft, Fr = S.gear_forces()
    cs.step("F_t", "F_t = 2T/d₂", Ft, "N", "圆周力", src="式 (33.4.1)")
    cs.step("F_r", "F_r = F_t tan α", Fr, "N", "径向力", src="式 (33.4.1)")
    (RAx, RBx), (RAy, RBy) = S.reactions(Ft), S.reactions(Fr)
    cs.step("R_A", "R_B = F a/L，R_A = F − R_B（两平面），R = √(R_H² + R_V²)", math.hypot(RAx, RAy), "N", "左轴承支反力", src="33.4.3 节")
    cs.step("R_B", "同上", math.hypot(RBx, RBy), "N", "右轴承支反力", src="33.4.3 节")

    series, rate, rated = S.torque_series()
    K_peak = float(series.max()) / rated
    cs.step("K_peak", "K = T_max / T（跑合试验台转矩记录）", K_peak, "", "起动冲击倍数", src="33.8.4 节；数字工厂 test-01")

    S_min, sca_min = math.inf, math.inf
    for k, sec in S.SECTIONS.items():
        d = sec["d"]
        M, Tq = S.M_total(sec["z"]), S.torque_at(sec["z"])
        cs.step(f"M_{k}", "M = √(M_H² + M_V²)", M / 1e3, "N·m", f"截面 {k} 合成弯矩（{sec['what'][0]}）", src="式 (33.4.2)")
        sig, tau = M / S.W_solid(d), Tq / S.WT_solid(d)
        s_vm = K_peak * math.sqrt(sig ** 2 + 3 * tau ** 2)
        Ss = cs.step(f"S_static,{k}", "S = σs / (K_peak √(σ² + 3τ²))", mat["sigma_s"] / s_vm, "", f"截面 {k} 静强度安全系数", src="式 (33.4.3)、(33.4.4)")
        S_min = min(S_min, Ss)
        if sec["notch"] == "keyseat":
            a = mdstd.kt_estimate("keyseat_endmill")
            src_a = "[SHI] 应力集中首轮估计（端铣键槽）"
        else:
            a = mdstd.kt_estimate("shoulder_round")
            src_a = "[SHI] 首轮估计（大圆角）；换成有限元（33.5.4 节）或 [PET] 的值"
        f = S.fatigue_factors(sec, mat, "ground", None if sec["notch"] == "keyseat" else (a["Kt"], a["Kts"]))
        cs.table_value(f"α_σ,{k} / α_τ,{k}", f"{f['alpha_s']:.2f} / {f['alpha_t']:.2f}", "", f"截面 {k} 理论应力集中系数", src=src_a)
        cs.step(f"k_σ,{k} / k_τ,{k}", "k = 1 + q(α − 1)，q 按诺伊伯—库恩公式", f"{f['k_s']:.2f} / {f['k_t']:.2f}", "", f"截面 {k} 有效应力集中系数", src="式 (33.5.3)")
        cs.step(f"ε_{k}, β", "ε = 1.24 d^−0.107，β = a σb^b（磨削）", f"{f['eps']:.3f} / {f['beta']:.3f}", "", f"截面 {k} 尺寸、表面系数", src="[SHI] 疲劳一章（马林系数）")
        cs.step(f"K_σ,{k} / K_τ,{k}", "K = k/ε + 1/β − 1", f"{f['K_s']:.2f} / {f['K_t']:.2f}", "", f"截面 {k} 综合影响系数", src="式 (33.5.4)")
        c = S.safety(sec, mat, f, M, Tq)
        sca = cs.step(f"S_ca,{k}", "S_ca = S_σ S_τ / √(S_σ² + S_τ²)", c["S_ca"], "", f"截面 {k} 疲劳安全系数", src="式 (33.5.5)、(33.5.6)")
        sca_min = min(sca_min, sca)

    Ft_, Fr_ = S.gear_forces()
    z, yx, tx = S.deflection(Ft_)
    _, yy, ty = S.deflection(Fr_)
    th = [math.hypot(float(tx[abs(z - zb).argmin()]), float(ty[abs(z - zb).argmin()])) * 1e3 for zb in (S.Z_BRG_A, S.Z_BRG_B)]
    cs.step("θ_A / θ_B", "梁单元法，两平面合成", f"{th[0]:.3f} / {th[1]:.3f}", "mrad", "轴承处转角", src="33.6 节")
    nc1 = float(S.critical_speeds(n_modes=2)[0][0])
    cs.step("n_c1", "梁单元法；邓克利公式核对", nc1, "r/min", "一阶临界转速", src="33.7 节")
    cs.step("L_h", "雨流计数 + 古德曼修正 + 迈因纳累积", "（由“仿真与分析”算出后填入）", "h", "疲劳寿命（外伸段键槽、台阶圆角）", src="33.8 节")

    cs.check("S_static,min", S_min, ">=", 1.5, "静强度", src="33.4.5 节")
    cs.check("S_ca,min", sca_min, ">=", 1.5, "疲劳强度", src="33.5.5 节")
    cs.check("θ_max", max(th), "<=", 1.0, "轴承处转角（mrad）", src="[SHI] 轴一章")
    cs.check("n/n_c1", S.N_OUT / nc1, "<=", 0.7, "临界转速", src="33.7.2 节")
    cs.note("寿命按数字工厂“仿真与分析”的报告填写，并与 33.8 节对照；截面 I、II 还要按过盈配合的系数复核（第 25 章）。")
    return cs


if __name__ == "__main__":
    print(sheet().markdown())
