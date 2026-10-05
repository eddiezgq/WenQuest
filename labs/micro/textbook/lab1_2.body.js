// 实验 1.2 电压传输特性与噪声容限（配 1.2 节）。两个场景：传输特性（调尺寸比、移动输入看工作点）、
// 编码器输入（把 ±干扰叠加到 0 和 1 上，看会不会越过 VIL、VIH）。传输特性按式 (1.2.1) 逐点二分求解，
// VIL、VIH 取斜率为 −1 的两点，与书中程序 1.2.1 同一算法；按尺寸比缓存，拖动输入时不重算。
const VDD12 = M1_2.P.VDD, W12 = M1_2.P.Wmin, R12 = M1_2.P.kn / M1_2.P.kp;
const cache12 = {};
function vtc12(ratio) {
  const key = ratio.toFixed(3);
  if (!cache12[key]) {
    const nm = M1_2.noiseMargins(W12, ratio * W12), pts = [];
    for (let i = 0; i <= 180; i++) { const v = i * VDD12 / 180; pts.push([v, M1_2.vout(v, W12, ratio * W12)]); }
    cache12[key] = { nm, pts, vm: M1_2.vm(W12, ratio * W12) };
  }
  return cache12[key];
}
function gain12(vi, ratio) { const d = 0.002; return (M1_2.vout(vi + d, W12, ratio * W12) - M1_2.vout(vi - d, W12, ratio * W12)) / (2 * d); }

WQ.lab({
  title: ["实验 1.2 电压传输特性与噪声容限", "Lab 1.2 Voltage transfer characteristic and noise margins"],
  goal: ["扫描输入看输出，找到开关阈值 VM 和斜率为 −1 的两点；调尺寸比使 VM = VDD/2；用噪声容限判断干扰下会不会误判。",
         "Sweep the input and watch the output; find the switching threshold VM and the two unity-gain points; size the inverter for VM = VDD/2; use the noise margins to judge whether noise causes errors."],
  scenes: [
    { id: "vtc", name: ["传输特性", "Transfer curve"], hide: ["noise"],
      problem: { title: ["输入慢慢升高，输出怎样变", "How the output follows a slowly rising input"],
                 text: ["拖动输入电压，看工作点沿传输特性移动；中间那段几乎竖直，两个管子同时饱和。调 Wp/Wn，看 VM 怎样移动。",
                        "Drag the input and watch the operating point move along the curve; in the nearly vertical middle both transistors are saturated. Change Wp/Wn and watch VM move."] } },
    { id: "enc", robot: true, name: ["编码器信号进入控制芯片", "Encoder signal entering the controller"], hide: ["vi"],
      problem: { title: ["机器人问题：电缆上的干扰", "Robot problem: noise on the cable"],
                 text: ["编码器信号经 2 m 电缆进入芯片，叠加了约 ±0.3 V 的干扰：0 变成 0.3 V，1 变成 1.5 V。反相器还能判断对吗？它最多能承受多大的干扰？",
                        "The encoder signal reaches the chip through 2 m of cable with about ±0.3 V of noise: 0 becomes 0.3 V and 1 becomes 1.5 V. Does the inverter still decide correctly? How much noise can it take?"] } },
  ],
  params: [
    { id: "ratio", name: ["尺寸比 Wp/Wn", "Size ratio Wp/Wn"], min: 0.5, max: 5, step: 0.05, value: 1, unit: "", digits: 2 },
    { id: "vi", name: ["输入电压 Vin", "Input voltage Vin"], min: 0, max: 1.8, step: 0.01, value: 0.4, unit: "V", digits: 2 },
    { id: "noise", name: ["干扰幅度", "Noise amplitude"], min: 0, max: 1, step: 0.05, value: 0.3, unit: "V", digits: 2 },
  ],
  tasks: [
    { id: "vm", text: ["调 Wp/Wn，使开关阈值 VM 与 VDD/2 = 0.9 V 相差不到 0.01 V。这时的尺寸比和 r = k′n/k′p 有什么关系？", "Adjust Wp/Wn so that VM is within 0.01 V of VDD/2 = 0.9 V. How does this ratio relate to r = k′n/k′p?"],
      demo: { scene: "vtc", set: { ratio: 2.45 }, press: [], wait: 1 } },
    { id: "vil", text: ["Wp/Wn = 1 时，把输入移到 VIL（斜率为 −1 的左侧点，误差不超过 0.015 V），读出这时的增益。", "With Wp/Wn = 1, move the input to VIL (the left unity-gain point, within 0.015 V) and read the gain there."],
      demo: { scene: "vtc", set: { ratio: 1, vi: 0.72 }, press: [], wait: 1 } },
    { id: "noise", robot: true, text: ["编码器输入用对称尺寸（Wp/Wn 与 r 相差不到 0.1）：把干扰加大到刚好不超过较小的噪声容限（相差不到 0.05 V）。", "Encoder input with symmetric sizing (Wp/Wn within 0.1 of r): raise the noise until it just stays within the smaller noise margin (within 0.05 V)."],
      demo: { scene: "enc", set: { ratio: 2.45, noise: 0.7 }, press: [], wait: 1 } },
  ],
  think: ["干扰越过了 VIL 并不等于一定出错，但为什么设计时仍以噪声容限为界？如果把两个反相器串起来，第二级看到的干扰会变大还是变小？",
          "Crossing VIL does not always cause an error, so why do designers still treat the noise margin as the limit? With two inverters in series, does the second stage see more or less noise?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["传输特性", "transfer curve"], color: "#1d6fb8" }, { name: ["干扰后的输入范围", "input range with noise"], color: "#e67e22" }],
  reset(api, s) { check12(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, c = vtc12(p.ratio), nm = c.nm;
    const rows = [[["开关阈值 VM", "Switching threshold VM"], f(c.vm, 3) + " V"],
                  [["VIL / VIH", "VIL / VIH"], f(nm.VIL, 3) + " / " + f(nm.VIH, 3) + " V"],
                  [["NML / NMH", "NML / NMH"], f(nm.NML, 3) + " / " + f(nm.NMH, 3) + " V"],
                  [["r = k′n/k′p", "r = k′n/k′p"], f(R12, 2)]];
    if (api.scene === "vtc") {
      rows.push([["输出 Vout", "Output Vout"], f(M1_2.vout(p.vi, W12, p.ratio * W12), 3) + " V"], [["增益 dVout/dVin", "Gain dVout/dVin"], f(gain12(p.vi, p.ratio), 2)]);
    } else {
      const ok = p.noise <= Math.min(nm.NML, nm.NMH) + 1e-9;
      rows.push([["0 → 输入最高", "0 → worst input"], f(p.noise, 2) + " V"], [["1 → 输入最低", "1 → worst input"], f(VDD12 - p.noise, 2) + " V"],
                [["判断", "Verdict"], ok ? api.T("在噪声容限之内", "within the noise margins") : api.T("超出噪声容限，可能误判", "beyond the noise margins: may be misread")]);
    }
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mu = css("--muted");
    const blue = "#1d6fb8", amber = "#e67e22", red = "#c0392b", green = css("--green");
    const c = vtc12(p.ratio), nm = c.nm, side = Math.min(w * 0.62, h * 0.82);
    const px = w * 0.08, py = h * 0.06;
    const ax = api.plot(px, py, side, side, [{ pts: c.pts, color: blue }, { pts: [[0, 0], [VDD12, VDD12]], color: css("--grid") }],
      { xmin: 0, xmax: VDD12, ymin: 0, ymax: VDD12, xlabel: "Vin / V", ylabel: "Vout / V" });
    // VIL, VIH, VM
    [[nm.VIL, "VIL"], [nm.VIH, "VIH"]].forEach(([v, n], i) => {
      api.line(ax.X(v), py, ax.X(v), py + side, mu, 1, [4, 4]); api.label(n, ax.X(v) + (i ? 4 : -4), py + side + 12, mu, 11, i ? "left" : "right");
      api.circle(ax.X(v), ax.Y(M1_2.vout(v, W12, p.ratio * W12)), 4, mu);
    });
    api.circle(ax.X(c.vm), ax.Y(c.vm), 4, ink); api.label("VM", ax.X(c.vm) + 8, ax.Y(c.vm) - 2, ink, 12);
    if (api.scene === "vtc") {
      const vo = M1_2.vout(p.vi, W12, p.ratio * W12);
      api.line(ax.X(p.vi), py + side, ax.X(p.vi), ax.Y(vo), amber, 1.5, [2, 3]);
      api.circle(ax.X(p.vi), ax.Y(vo), 6, amber, ink);
    } else {
      // noisy low input [0, noise] and noisy high input [VDD - noise, VDD] on the x axis
      const lowOk = p.noise <= nm.VIL - nm.VOL + 1e-9, highOk = p.noise <= nm.VOH - nm.VIH + 1e-9;
      api.rect(ax.X(0), py + side - 8, ax.X(p.noise) - ax.X(0), 8, lowOk ? amber : red);
      api.rect(ax.X(VDD12 - p.noise), py + side - 8, ax.X(VDD12) - ax.X(VDD12 - p.noise), 8, highOk ? amber : red);
      // what the next stage sees
      const yL = M1_2.vout(p.noise, W12, p.ratio * W12), yH = M1_2.vout(VDD12 - p.noise, W12, p.ratio * W12);
      api.circle(ax.X(p.noise), ax.Y(yL), 5, lowOk ? amber : red); api.circle(ax.X(VDD12 - p.noise), ax.Y(yH), 5, highOk ? amber : red);
    }
    // right: the margin bars
    const bx = px + side + w * 0.07, bw = Math.max(40, w - bx - 20), by = py + 10, bh = side - 20, Y = (v) => by + bh - v / VDD12 * bh;
    api.label(api.T("电平与噪声容限", "Levels and margins"), bx, by - 2, ink, 12);
    const col = (x0, top, bot, color, text) => { api.rect(x0, Y(top), bw * 0.4, Y(bot) - Y(top), color); api.label(text, x0 + bw * 0.2, (Y(top) + Y(bot)) / 2, "#fff", 11, "center"); };
    col(bx, nm.VOH, nm.VIH, green, "NMH"); col(bx, nm.VIL, nm.VOL, green, "NML");
    [[nm.VOH, "VOH"], [nm.VIH, "VIH"], [nm.VIL, "VIL"], [nm.VOL, "VOL"]].forEach(([v, n]) => api.label(n + " " + api.fmt(v, 2), bx + bw * 0.45, Y(v), mu, 11));
    if (api.scene === "enc") {
      api.line(bx - 6, Y(p.noise), bx + bw * 0.4 + 6, Y(p.noise), amber, 2);
      api.line(bx - 6, Y(VDD12 - p.noise), bx + bw * 0.4 + 6, Y(VDD12 - p.noise), amber, 2);
    }
  },
});

function check12(api) {
  const p = api.p, c = vtc12(p.ratio), nm = c.nm;
  if (api.scene === "vtc") {
    if (Math.abs(c.vm - VDD12 / 2) < 0.01) api.done("vm");
    if (Math.abs(p.ratio - 1) < 1e-9 && Math.abs(p.vi - nm.VIL) <= 0.015) api.done("vil");
    return;
  }
  const m = Math.min(nm.NML, nm.NMH);
  if (Math.abs(p.ratio - R12) < 0.1 && p.noise <= m + 1e-9 && p.noise >= m - 0.05) api.done("noise");
}
