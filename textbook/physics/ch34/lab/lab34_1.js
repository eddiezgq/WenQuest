// 实验 34.1 磁铁与线圈：法拉第电磁感应定律（配 34.1 节）。磁铁近似为磁偶极子（磁矩 m = 0.81 A·m²），沿轴线穿过半径 a 的 N 匝线圈：
// Φ = μ0 m a²/[2(a² + z²)^{3/2}]，ε = −N dΦ/dt。机器人场景：AGV 车轮上的磁钢每转一圈掠过拾音线圈一次（转速传感器）。
const MU0_34 = 1.25663706e-6, M_34 = 0.8125;
const flux34 = (z, a) => MU0_34 * M_34 * a * a / (2 * Math.pow(a * a + z * z, 1.5));
const emf34 = (z, a, v, N) => N * 1.5 * MU0_34 * M_34 * a * a * z * v / Math.pow(a * a + z * z, 2.5);
const SUB_34 = 20;                     // 每帧分 20 步计算，脉冲很窄时也不漏掉峰值（与帧率无关）
WQ.lab({
  title: ["实验 34.1 磁铁与线圈：法拉第电磁感应定律", "Lab 34.1 Magnet and coil: Faraday's law"],
  goal: ["让磁铁以不同速度穿过线圈，看电动势的大小、方向和波形怎样随速度、匝数变化；再用同样的原理测 AGV 车轮的转速。",
         "Pass a magnet through a coil at different speeds and see how the emf's size, sign and shape depend on speed and turns; then use the same idea to measure an AGV wheel's speed."],
  scenes: [
    { id: "coil", name: ["磁铁穿过线圈", "Magnet through a coil"], hide: ["rpm"],
      problem: { title: ["生活中的例子：摇一摇就能发电的手电筒", "Everyday example: a shake-to-charge torch"],
                 text: ["手电筒里一块磁铁在线圈中来回滑动。摇得越快，灯越亮吗？", "A magnet slides back and forth through a coil in the torch. Does shaking faster make it brighter?"] } },
    { id: "wheel", robot: true, name: ["AGV 车轮转速传感器", "AGV wheel-speed sensor"], hide: ["v", "N"],
      problem: { title: ["机器人问题：不用编码器也能测轮速", "Robot problem: wheel speed without an encoder"],
                 text: ["车轮（半径 0.05 m）上嵌一块磁钢，每转一圈从拾音线圈旁掠过一次，线圈输出一个电压脉冲。由脉冲的频率求车速。",
                        "A magnet in the wheel (radius 0.05 m) sweeps past a pickup coil once per turn, giving one voltage pulse. Find the speed from the pulse rate."] } },
  ],
  params: [
    { id: "v", name: ["磁铁速度 v", "Magnet speed v"], min: 0.1, max: 2, step: 0.05, value: 0.5, unit: "m/s", digits: 2 },
    { id: "N", name: ["线圈匝数 N", "Turns N"], min: 50, max: 400, step: 50, value: 200, digits: 0 },
    { id: "rpm", name: ["车轮转速", "Wheel speed"], min: 30, max: 300, step: 1, value: 60, unit: "r/min", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--blue)", name: ["NΦ（按比例画出）", "NΦ (scaled)"] }, { color: "var(--orange)", name: ["电动势 ε", "emf ε"] }],
  tasks: [
    { id: "peak", text: ["N = 200、v = 0.5 m/s：读出电动势的峰值，说出靠近和离开时的正负。", "N = 200, v = 0.5 m/s: read the peak emf and the signs while approaching and leaving."],
      demo: { scene: "coil", set: { v: 0.5, N: 200 }, press: ["start"], wait: 3 } },
    { id: "double", text: ["把速度加倍到 1.0 m/s：峰值电动势也加倍（超过 0.85 V），脉冲变窄。", "Double the speed to 1.0 m/s: the peak doubles (above 0.85 V) and the pulse narrows."],
      demo: { scene: "coil", set: { v: 1.0, N: 200 }, press: ["start"], wait: 3 } },
    { id: "wheel", robot: true, text: ["车轮场景：由脉冲计数和计时求出脉冲频率，把它调到 5 Hz，算出这时 AGV 的车速。", "Wheel: find the pulse rate from the pulse count and the elapsed time, set it to 5 Hz and work out the AGV's speed."],
      demo: { scene: "wheel", set: { rpm: 300 }, press: ["start"], wait: 5 } },
  ],
  think: ["整个穿过过程中，电动势对时间的积分是多少？为什么与速度无关？", "What is the time integral of the emf over the whole pass? Why does it not depend on the speed?"],

  reset(api, s) { s.z = -0.1; s.hist = []; s.peak = 0; s.pulses = 0; s.lastA = 0; s.t0 = null; s.integral = 0; },
  update(dt, api, s) {
    const a = 0.01;
    if (api.scene === "coil") {
      const v = api.p.v, N = api.p.N, h = dt * 0.25 / SUB_34;      // 慢放 4 倍：模拟时间 = 实际时间 × 0.25
      for (let i = 0; i < SUB_34 && s.z <= 0.1; i++) {
        const emf = emf34(s.z, a, v, N);
        s.hist.push([s.z / v * 1000, N * flux34(s.z, a) * 1000, emf]);
        s.peak = Math.max(s.peak, Math.abs(emf)); s.integral += emf * h;
        s.z += v * h;
      }
      if (s.z > 0.1) { api.stop(); fin34_1(api, s); }
    } else {
      // 磁钢在半径 0.05 m 的轮缘上，线圈在轮缘外 5 mm：等效为磁铁以轮缘速度掠过，距离在每圈中周期性变化
      const w = api.p.rpm * 2 * Math.PI / 60, R = 0.05, v = w * R, t1 = api.t * 0.25;
      for (let i = 0; i < SUB_34; i++) {
        const t = t1 - dt * 0.25 * (SUB_34 - 1 - i) / SUB_34, ang = (w * t) % (2 * Math.PI);
        const arc = R * (ang < Math.PI ? ang : ang - 2 * Math.PI);
        const emf = 200 * 1.5 * MU0_34 * M_34 * a * a * arc * v / Math.pow(a * a + arc * arc + 0.005 * 0.005, 2.5) * 0.3;
        if (s.lastA < Math.PI && ang >= Math.PI) s.pulses++;
        s.lastA = ang;
        s.hist.push([t * 1000, 0, emf]);
        s.peak = Math.max(s.peak, Math.abs(emf));
      }
      while (s.hist.length > 8000) s.hist.shift();
      if (t1 > 1.0) { api.stop(); fin34_1(api, s); }
    }
  },
  readouts(api, s) {
    const f = api.fmt;
    if (api.scene === "coil") {
      return [[["峰值电动势", "Peak emf"], f(s.peak, 3) + " V"],
              [["N·Φ 的最大值", "Largest NΦ"], f(api.p.N * flux34(0, 0.01) * 1000, 2) + " mWb"],
              [["∫ε dt（整个过程）", "∫ε dt (whole pass)"], f(s.integral * 1000, 3) + " mWb"]];
    }
    const t = s.hist.length ? s.hist[s.hist.length - 1][0] / 1000 : 0;
    return [[["脉冲计数", "Pulses counted"], String(s.pulses)], [["计时", "Elapsed time"], f(t, 3) + " s"], [["脉冲峰值", "Pulse peak"], f(s.peak, 3) + " V"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css;
    // 纵轴随峰值缩放（峰值在 |z| = a/2 处）；NΦ 按比例画出，最大值占纵轴的 80%
    const a = 0.01, ymax = Math.max(0.5, 1.15 * Math.abs(emf34(a / 2, a, api.p.v, api.p.N)));
    const sc = 0.8 * ymax / (api.p.N * flux34(0, a) * 1000);
    const P = api.plot(w * 0.08, h * 0.45, w * 0.86, h * 0.48, [
      { pts: s.hist.map((q) => [q[0], q[2]]), color: css("--orange") },
      ...(api.scene === "coil" ? [{ pts: s.hist.map((q) => [q[0], q[1] * sc]), color: css("--blue") }] : []),
    ], api.scene === "coil" ? { xmin: -0.1 / api.p.v * 1000, xmax: 0.1 / api.p.v * 1000, ymin: -ymax, ymax, xlabel: "t / ms", ylabel: "ε / V" }
                            : { xmin: 0, xmax: 1000, ymin: -Math.max(0.05, 1.3 * s.peak), ymax: Math.max(0.05, 1.3 * s.peak), xlabel: "t / ms", ylabel: "ε / V" });
    if (api.scene === "coil") {
      const cx = w * 0.5, cy = h * 0.2, k = w * 2.2;
      api.ctx.strokeStyle = css("--orange"); api.ctx.lineWidth = 5;
      api.ctx.beginPath(); api.ctx.ellipse(cx, cy, 10, 44, 0, 0, 2 * Math.PI); api.ctx.stroke();
      const mx = cx + s.z * k;
      api.rect(mx - 30, cy - 10, 30, 20, css("--blue")); api.rect(mx, cy - 10, 30, 20, css("--red"));
      api.label("S", mx - 15, cy + 5, "#fff", 12, "center"); api.label("N", mx + 15, cy + 5, "#fff", 12, "center");
    } else {
      const cx = w * 0.3, cy = h * 0.22, R = h * 0.15, ang = (api.p.rpm * 2 * Math.PI / 60 * api.t * 0.25);
      api.circle(cx, cy, R, css("--panel"), css("--ink"));
      api.circle(cx + R * Math.sin(ang), cy + R * Math.cos(ang), 7, css("--red"), css("--ink"));
      api.rect(cx - 8, cy + R + 6, 16, 18, css("--orange"));
      api.label(api.T("拾音线圈", "pickup coil"), cx + 14, cy + R + 20, css("--muted"), 12);
    }
  },
});

function fin34_1(api, s) {
  if (api.scene === "coil") {
    if (api.p.N === 200 && Math.abs(api.p.v - 0.5) < 1e-6 && s.peak > 0.4) api.done("peak");
    if (api.p.N === 200 && api.p.v >= 0.99 && s.peak > 0.85) api.done("double");
  } else if (Math.abs(api.p.rpm / 60 - 5) < 0.05 && s.pulses >= 3) api.done("wheel");
}
