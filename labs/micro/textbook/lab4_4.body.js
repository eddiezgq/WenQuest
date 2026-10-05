// 实验 4.4 串扰（配 4.4 节）。受害线与干扰线在 met2 上平行，干扰线以上升时间 tr 跳变 VDD；受害线接一个参考反相器，
// 由 size 倍反相器保持在 0。峰值噪声按式 (4.4.2)，耦合电容按 Magic 工艺文件的侧壁公式（M4_4.xtalk，与书中程序 4.4.1 同一模型）。
// 右图是受害线的噪声波形：干扰线上升期间按 τ 充电，之后经驱动器按 e^(−t/τ) 泄放；虚线是参考反相器的噪声容限。
const P44 = M4_4.P, Q44 = P44.problems.p44, R44 = P44.kn / P44.kp;
const NMx = M4_4.noiseMargins(P44.Wmin, R44 * P44.Wmin), NM44 = Math.min(NMx.NML, NMx.NMH);
const S0_44 = P44.wires.layers[Q44.layer].smin;
const x44 = (p) => M4_4.xtalk(Q44.layer, Q44.w_um, p.s, p.L, p.size, p.tr * 1e-12);
const pk44 = (s, size, tr, L) => M4_4.xtalk(Q44.layer, Q44.w_um, s, L, size, tr * 1e-12)[3];
const near44 = (a, b) => Math.abs(a - b) < 1e-6;

WQ.lab({
  title: ["实验 4.4 串扰", "Lab 4.4 Crosstalk"],
  goal: ["编码器信号线与一条 PWM 线平行：调间距、受害线的驱动、干扰线的边沿和平行长度，看噪声峰值与噪声容限，找出把噪声压到容限以下的办法。",
         "An encoder line runs beside a PWM line: vary the spacing, the victim's driver, the aggressor's edge and the parallel length; compare the noise peak with the noise margin and find ways to bring it below."],
  scenes: [
    { id: "enc", robot: true, name: ["编码器线与 PWM 线", "Encoder line beside a PWM line"], hide: [],
      problem: { title: ["机器人问题：PWM 一跳，编码器线会不会误计", "Robot problem: does a PWM edge make the encoder count wrong"],
                 text: ["两线在 met2 上以最小间距平行 500 μm，编码器线由最小反相器驱动，PWM 边沿 100 ps。噪声峰值超过噪声容限了吗？怎样压下去？",
                        "The lines run side by side for 500 μm at minimum spacing on met2; the encoder line has a minimum driver and the PWM edge is 100 ps. Does the noise peak exceed the margin, and how can it be reduced?"] } },
  ],
  params: [
    { id: "s", name: ["间距", "Spacing"], min: 0.14, max: 0.84, step: 0.02, value: 0.14, unit: "μm", digits: 2 },
    { id: "size", name: ["受害线驱动（参考反相器的倍数，1 倍即最小反相器）", "Victim driver (× reference inverter; 1× = minimum inverter)"], min: 1, max: 8, step: 1, value: 1, unit: "", digits: 0 },
    { id: "tr", name: ["干扰线的上升时间", "Aggressor rise time"], min: 20, max: 1000, step: 10, value: 100, unit: "ps", digits: 0 },
    { id: "L", name: ["平行长度", "Parallel length"], min: 50, max: 1000, step: 25, value: 500, unit: "μm", digits: 0 },
  ],
  tasks: [
    { id: "both", robot: true, text: ["间距加倍（0.28 μm）、驱动加到 4 倍：噪声峰值是否低于噪声容限？", "Double the spacing (0.28 μm) and use a 4× driver: is the peak below the noise margin?"],
      demo: { scene: "enc", set: { s: 0.28, size: 4, tr: 100, L: 500 }, press: [], wait: 1 } },
    { id: "space", text: ["驱动 2 倍、边沿 100 ps、500 μm：找到噪声峰值低于噪声容限的最小间距（以 0.02 μm 为步长）。", "2× driver, 100 ps edge, 500 μm: find the smallest spacing (0.02 μm steps) with the peak below the margin."],
      demo: { scene: "enc", set: { size: 2, tr: 100, L: 500, s: 0.38 }, press: [], wait: 1 } },
    { id: "short", text: ["最小间距、最小驱动、边沿 100 ps：平行长度最长能到多少（以 25 μm 为步长）？", "Minimum spacing, minimum driver, 100 ps edge: how long can the lines run in parallel (25 μm steps)?"],
      demo: { scene: "enc", set: { s: 0.14, size: 1, tr: 100, L: 100 }, press: [], wait: 1 } },
  ],
  think: ["干扰线的边沿放慢到 1 ns，噪声怎样变？为什么平行长度缩短时噪声下降得不如间距加大那么快？",
          "What happens to the noise when the aggressor's edge slows to 1 ns? Why does shortening the parallel run reduce the noise less effectively than widening the spacing?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["受害线电压", "victim voltage"], color: "#c0392b" }, { name: ["噪声容限", "noise margin"], color: "#e67e22" }],
  reset(api, s) { check44(api); },
  readouts(api, s) {
    const f = api.fmt, [Cc, Cg, dvf, pk, tau] = x44(api.p);
    return [[["耦合电容 Cc / 对地电容 Cg", "Coupling Cc / ground Cg"], f(Cc * 1e15, 1) + " / " + f(Cg * 1e15, 1) + " fF"],
            [["悬空时的跳动", "Floating victim"], f(dvf, 2) + " V"],
            [["τ = R(Cc + Cg)", "τ = R(Cc + Cg)"], f(tau * 1e12, 0) + " ps"],
            [["噪声峰值", "Noise peak"], f(pk, 3) + " V " + (pk < NM44 ? api.T("（低于容限）", "(below margin)") : api.T("（超过容限）", "(above margin)"))],
            [["噪声容限", "Noise margin"], f(NM44, 3) + " V"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, mu = css("--muted"), ink = css("--ink"), red = "#c0392b", blue = "#1d6fb8", amber = "#e67e22";
    const p = api.p, [Cc, Cg, dvf, pk, tau] = x44(p), VDD = P44.VDD, tr = p.tr * 1e-12;
    // 上：两条平行线，间距按比例
    const x0 = w * 0.1, len = w * 0.8 * p.L / 1000, y1 = h * 0.08, gap = 6 + 40 * (p.s - 0.14) / 0.7;
    api.line(x0, y1, x0 + len, y1, blue, 4); api.label("PWM", x0 - 6, y1 + 4, blue, 11, "right");
    api.line(x0, y1 + gap, x0 + len, y1 + gap, red, 4); api.label(api.T("编码器", "encoder"), x0 - 6, y1 + gap + 4, red, 11, "right");
    api.label(api.fmt(p.L, 0) + " μm", x0 + len + 6, y1 + gap / 2 + 4, mu, 11, "left");
    // 下：噪声波形
    const T = Math.max(3 * tr, tr + 5 * tau), pts = [];
    for (let i = 0; i <= 200; i++) {
      const t = T * i / 200, k = VDD * Cc / (Cc + Cg);
      const v = t <= tr ? k * tau / tr * (1 - Math.exp(-t / tau)) : k * tau / tr * (1 - Math.exp(-tr / tau)) * Math.exp(-(t - tr) / tau);
      pts.push([t * 1e12, v]);
    }
    const px = w * 0.1, py = h * 0.3, pw = w * 0.84, ph = h * 0.56;
    const ax = api.plot(px, py, pw, ph, [{ pts, color: red }, { pts: [[0, NM44], [T * 1e12, NM44]], color: amber }],
      { xmin: 0, xmax: T * 1e12, ymin: 0, ymax: 1.3, xlabel: "t / ps", ylabel: "V" });
    api.label(api.fmt(pk, 2) + " V", ax.X(tr * 1e12) + 6, ax.Y(pk) - 6, pk < NM44 ? "#2e7d32" : red, 12, "left");
    api.label("0", px, py + ph + 13, mu, 10, "center"); api.label(api.fmt(T * 1e12, 0), px + pw, py + ph + 13, mu, 10, "right");
    api.label(api.T("噪声容限", "noise margin"), px + pw - 4, ax.Y(NM44) - 5, amber, 11, "right");
  },
});

function check44(api) {
  const p = api.p;
  if (near44(p.s, 0.28) && p.size === 4 && p.tr === 100 && p.L === 500 && pk44(p.s, 4, 100, 500) < NM44) api.done("both");
  if (p.size === 2 && p.tr === 100 && p.L === 500 && pk44(p.s, 2, 100, 500) < NM44 && pk44(p.s - 0.02, 2, 100, 500) >= NM44) api.done("space");
  if (near44(p.s, S0_44) && p.size === 1 && p.tr === 100 && pk44(S0_44, 1, 100, p.L) < NM44 && pk44(S0_44, 1, 100, p.L + 25) >= NM44) api.done("short");
}
