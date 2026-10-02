// 实验 34.7 AGV 无线充电（配 34.7 节）。两个相同线圈 L = 24 μH、内阻 0.1 Ω，串联电容补偿（谐振 85 kHz），负载 10 Ω，
// 一次侧电压幅值 10 V（按比例缩小的示例，与算例 34.7.1 相同；实际 AGV 充电为千瓦级）。用相量方程计算（第 36 章）：Z1 I1 − jωM I2 = U1，−jωM I1 + Z2 I2 = 0，M = k L。
const L_347 = 24e-6, R_347 = 0.1, RL_347 = 10, U_347 = 10, F0_347 = 85e3, C_347 = 1 / Math.pow(2 * Math.PI * F0_347, 2) / L_347;
const cplx = { m: (a, b) => [a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0]], d: (a, b) => { const q = b[0] * b[0] + b[1] * b[1]; return [(a[0] * b[0] + a[1] * b[1]) / q, (a[1] * b[0] - a[0] * b[1]) / q]; },
               a: (a, b) => [a[0] + b[0], a[1] + b[1]], s: (a, b) => [a[0] - b[0], a[1] - b[1]], abs: (a) => Math.hypot(a[0], a[1]) };
const link347 = (k, fkHz, comp, L, R0, f0kHz = 85) => {
  const w = 2 * Math.PI * fkHz * 1000, M = k * L, C = 1 / Math.pow(2 * Math.PI * f0kHz * 1000, 2) / L;
  const X = comp ? w * L - 1 / (w * C) : w * L;
  const Z1 = [R0, X], Z2 = [R0 + RL_347, X], jwM = [0, w * M];
  // I1 = U Z2 / (Z1 Z2 + (ωM)²)，I2 = jωM I1 / Z2
  const den = cplx.a(cplx.m(Z1, Z2), [Math.pow(w * M, 2), 0]);
  const I1 = cplx.d(cplx.m([U_347, 0], Z2), den), I2 = cplx.d(cplx.m(jwM, I1), Z2);
  const Pin = 0.5 * U_347 * I1[0], PL = 0.5 * Math.pow(cplx.abs(I2), 2) * RL_347;
  return { eta: PL / Pin, PL, Vout: cplx.abs(I2) * RL_347, I1: cplx.abs(I1), C };
};
// 手机（Qi 一类）：线圈 10 μH、内阻 0.3 Ω，谐振 128 kHz。发射端调节电压，使负载功率不超过 5 W，且一次侧电流幅值不超过 3 A。
const phone347 = (k) => {
  const r = link347(k, 128, true, 10e-6, 0.3, 128);
  const s = Math.min(Math.sqrt(5 / r.PL), 3 / r.I1);
  return { eta: r.eta, PL: r.PL * s * s, Vout: r.Vout * s, I1: r.I1 * s, C: r.C };
};
WQ.lab({
  title: ["实验 34.7 AGV 无线充电", "Lab 34.7 Wireless charging of an AGV"],
  goal: ["改变线圈间距（耦合系数 k）、频率和补偿方式，看传输效率和功率怎样变化，理解为什么无线充电要用谐振。",
         "Change the coil gap (coupling k), the frequency and the compensation, and see how efficiency and power respond — why wireless charging uses resonance."],
  scenes: [
    { id: "agv", robot: true, name: ["AGV 充电桩", "AGV charging pad"],
      problem: { title: ["机器人问题：AGV 停到充电位", "Robot problem: an AGV parks over its charger"],
                 text: ["地面线圈与车底线圈相对，间隙由停车精度决定。间隙大一点、频率偏一点，充电还行吗？", "The floor coil faces the coil under the AGV; the gap depends on parking. Does charging still work with a larger gap or an off-tune frequency?"] } },
    { id: "phone", name: ["手机无线充电", "Phone charging"], hide: ["f", "comp"], params: { k: { value: 0.6 } },
      problem: { title: ["生活中的例子：手机放歪了就充得慢", "Everyday example: a phone placed off-centre charges slowly"],
                 text: ["手机与充电板的线圈对不准时耦合系数变小。", "When the phone's coil is off-centre the coupling falls."] } },
  ],
  params: [
    { id: "k", name: ["耦合系数 k", "Coupling k"], min: 0.02, max: 0.8, step: 0.01, value: 0.3, digits: 2 },
    { id: "f", name: ["频率 f", "Frequency f"], min: 60, max: 110, step: 1, value: 85, unit: "kHz", digits: 0 },
    { id: "comp", name: ["谐振补偿：1 有 / 0 无", "Resonant compensation: 1 on / 0 off"], min: 0, max: 1, step: 1, value: 1, digits: 0 },
  ],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "res", robot: true, text: ["k = 0.30、85 kHz、有补偿：效率超过 90%，读出负载功率。", "k = 0.30, 85 kHz, compensated: efficiency above 90%; read the load power."],
      demo: { scene: "agv", set: { k: 0.3, f: 85, comp: 1 }, press: [], wait: 1 } },
    { id: "nocomp", robot: true, text: ["去掉补偿（k = 0.30、85 kHz）：负载功率降到 1 W 以下。", "Remove the compensation (k = 0.30, 85 kHz): the load power drops below 1 W."],
      demo: { scene: "agv", set: { k: 0.3, f: 85, comp: 0 }, press: [], wait: 1 } },
    { id: "detune", robot: true, text: ["有补偿、k = 0.30，把频率调到 75 kHz 以下：负载功率不到谐振时的一半。", "Compensated, k = 0.30: tune below 75 kHz — the load power falls under half its resonant value."],
      demo: { scene: "agv", set: { k: 0.3, f: 70, comp: 1 }, press: [], wait: 1 } },
    { id: "phone", text: ["手机：把耦合系数调到 0.1 以下，效率降到多少？", "Phone: set k below 0.1. What happens to the efficiency?"],
      demo: { scene: "phone", set: { k: 0.05 }, press: [], wait: 1 } },
  ],
  think: ["k 很小时为什么负载功率反而先增大后减小（图 34.7.1）？效率和功率能不能同时最大？", "Why does the load power first rise and then fall as k grows from small values (Figure 34.7.1)? Can efficiency and power both be at their maximum?"],

  reset(api, s) {},
  readouts(api, s) {
    const f = api.fmt, phone = api.scene === "phone";
    const r = phone ? phone347(api.p.k) : link347(api.p.k, api.p.f, api.p.comp === 1, L_347, R_347);
    const r0 = link347(api.p.k, 85, true, L_347, R_347);
    if (!phone && Math.abs(api.p.k - 0.3) < 0.005) {
      if (api.p.f === 85 && api.p.comp === 1 && r.eta > 0.9) api.done("res");
      if (api.p.f === 85 && api.p.comp === 0 && r.PL < 1) api.done("nocomp");
      if (api.p.f < 75 && api.p.comp === 1 && r.PL < 0.5 * r0.PL) api.done("detune");
    }
    if (phone && api.p.k < 0.1) api.done("phone");
    return [[["效率 η", "Efficiency η"], f(100 * r.eta, 1) + " %"], [["负载功率", "Load power"], f(r.PL, 2) + " W"],
            [["输出电压幅值", "Output voltage (peak)"], f(r.Vout, 2) + " V"], [["一次侧电流幅值", "Primary current (peak)"], f(r.I1, 2) + " A"],
            [["补偿电容", "Compensation C"], f(r.C * 1e9, 1) + " nF"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, phone = api.scene === "phone";
    const gap = 20 + (0.8 - api.p.k) * 120, cx = w * 0.25;
    api.rect(cx - 80, h * 0.65, 160, 14, css("--orange"));
    api.rect(cx - 80, h * 0.65 - gap - 14, 160, 14, css("--orange"));
    if (phone) api.rect(cx - 50 + (0.8 - api.p.k) * 60, h * 0.65 - gap - 60, 100, 46, css("--ink"), null, 8);
    else api.agv(cx, h * 0.65 - gap - 14, 200);
    api.label(api.T("地面线圈", "floor coil"), cx, h * 0.65 + 34, css("--muted"), 12, "center");
    // 右侧：效率随 k 的曲线和当前点
    const pts = [], pts0 = [];
    for (let k = 0.02; k <= 0.8; k += 0.01) {
      pts.push([k, 100 * (phone ? phone347(k) : link347(k, api.p.f, api.p.comp === 1, L_347, R_347)).eta]);
      pts0.push([k, 100 * link347(k, 85, true, L_347, R_347).eta]);
    }
    const P = api.plot(w * 0.52, 20, w * 0.44, h * 0.8, [{ pts: pts0, color: css("--muted") }, { pts, color: css("--blue") }],
                       { xmin: 0, xmax: 0.8, ymin: 0, ymax: 100, xlabel: "k", ylabel: "η / %" });
    const now = phone ? phone347(api.p.k) : link347(api.p.k, api.p.f, api.p.comp === 1, L_347, R_347);
    api.circle(P.X(api.p.k), P.Y(100 * now.eta), 6, css("--red"), css("--ink"));
  },
});
