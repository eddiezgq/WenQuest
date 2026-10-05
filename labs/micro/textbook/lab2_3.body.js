// 实验 2.3 逻辑努力：寄存器地址译码器（配 2.3 节）。三个场景是三种结构：2 级（三输入与非 + 反相器）、
// 3 级（反相器 + 三输入与非 + 反相器）、4 级（两个反相器 + 三输入与非 + 反相器）。电容以参考反相器的输入电容 Cinv 为 1，
// 延时以 τ 为单位：每级 d = g·b·C(下一级)/C(本级) + p。第一级的输入电容由地址线的驱动能力定死，学生调后面各级的输入电容。
// 右侧同时给出各结构在最优尺寸下的手算延时，以及换用 SKY130 仿真 g、p 的延时。
const Q23 = M2_3.P.problems.p23, SIM23 = M2_3.P.gates_sim;
const GN23 = M2_3.leG("nand", Q23.n_addr), PN23 = M2_3.leP("nand", Q23.n_addr), PI23 = M2_3.leP("inv", 1);
const TAU23 = M2_3.tau() * 1e12, H23 = Q23.Cout_units / Q23.Cin_units, B23 = Q23.branch;
const ST23 = {   // 每级：[名称, g, p, 本级输出的分支数, 是否为与非门]
  s2: [["NAND3", GN23, PN23, 1, 1], ["INV", 1, PI23, 1, 0]],
  s3: [["INV", 1, PI23, B23, 0], ["NAND3", GN23, PN23, 1, 1], ["INV", 1, PI23, 1, 0]],
  s4: [["INV", 1, PI23, 1, 0], ["INV", 1, PI23, B23, 0], ["NAND3", GN23, PN23, 1, 1], ["INV", 1, PI23, 1, 0]],
};
const PIDS23 = ["c2", "c3", "c4"];
function path23(scene, p, sim) {
  const st = ST23[scene], caps = [scene === "s2" ? Q23.Cin_units / B23 : Q23.Cin_units];
  for (let i = 1; i < st.length; i++) caps.push(p[PIDS23[i - 1]]);
  caps.push(Q23.Cout_units);
  const gs = st.map((s) => (sim && s[4] ? SIM23.gates["nand" + Q23.n_addr + "_A"].g : s[1]));
  const ps = st.map((s) => (sim ? (s[4] ? SIM23.gates["nand" + Q23.n_addr + "_A"].p : SIM23.p_inv) : s[2]));
  const f = st.map((s, i) => gs[i] * s[3] * caps[i + 1] / caps[i]);
  const D = f.reduce((a, b) => a + b, 0) + ps.reduce((a, b) => a + b, 0);
  return { caps, f, D, P: ps.reduce((a, b) => a + b, 0) };
}
function opt23(scene, sim) {
  const st = ST23[scene];
  const gs = st.map((s) => (sim && s[4] ? SIM23.gates["nand" + Q23.n_addr + "_A"].g : s[1]));
  const ps = st.map((s) => (sim ? (s[4] ? SIM23.gates["nand" + Q23.n_addr + "_A"].p : SIM23.p_inv) : s[2]));
  return M2_3.pathDelay(gs, ps, B23, H23).D;
}

WQ.lab({
  title: ["实验 2.3 逻辑努力：地址译码器", "Lab 2.3 Logical effort: an address decoder"],
  goal: ["用逻辑努力给寄存器地址译码器选级数、定尺寸：读出每级的努力和总延时，找到最快的结构，把各级尺寸调到最优。",
         "Use logical effort to choose the number of stages and the sizes of a register address decoder: read each stage effort and the total delay, find the fastest structure and size it optimally."],
  scenes: [
    { id: "s2", robot: true, name: ["2 级：与非 + 反相器", "2 stages: NAND + INV"], hide: ["c3", "c4"], params: { c2: { min: 0.5, max: 20, step: 0.05, value: 8 } },
      problem: { title: ["机器人问题：8 个控制寄存器的地址译码", "Robot problem: decoding 8 control registers"],
                 text: ["每个地址位最多呈现 2 Cinv，每条输出驱动约 32 Cinv，每个地址位接 4 个与非门。先算路径努力 F，再调反相器的尺寸。",
                        "Each address bit may present at most 2 Cinv, each output drives about 32 Cinv, and each address bit feeds 4 NAND gates. Work out the path effort F, then size the inverter."] } },
    { id: "s3", robot: true, name: ["3 级：反相器 + 与非 + 反相器", "3 stages: INV + NAND + INV"], hide: ["c4"],
      params: { c2: { min: 0.5, max: 20, step: 0.05, value: 1 }, c3: { min: 1, max: 32, step: 0.05, value: 16 } },
      problem: { title: ["加一级输入反相器", "Add an input inverter"],
                 text: ["输入反相器产生地址的反码，再送给与非门。路径努力不变，寄生延时多了一个反相器。各级怎样分摊努力最快？",
                        "The input inverter produces the complement of the address bit. The path effort is unchanged but there is one more parasitic delay. How should the effort be shared?"] } },
    { id: "s4", name: ["4 级：两个反相器 + 与非 + 反相器", "4 stages: 2 INV + NAND + INV"], hide: [],
      params: { c2: { min: 0.5, max: 20, step: 0.05, value: 4 }, c3: { min: 0.5, max: 20, step: 0.05, value: 4 }, c4: { min: 1, max: 32, step: 0.05, value: 16 } },
      problem: { title: ["再多一级呢", "And one more stage?"],
                 text: ["4 级时每级努力更小，但寄生延时又多一份。它比 3 级快还是慢？",
                        "With 4 stages each effort is smaller, but there is one more parasitic delay. Is it faster or slower than 3 stages?"] } },
  ],
  params: [
    { id: "c2", name: ["第 2 级输入电容 / Cinv", "Stage 2 input capacitance / Cinv"], min: 0.5, max: 20, step: 0.05, value: 8, unit: "", digits: 2 },
    { id: "c3", name: ["第 3 级输入电容 / Cinv", "Stage 3 input capacitance / Cinv"], min: 0.5, max: 32, step: 0.05, value: 16, unit: "", digits: 2 },
    { id: "c4", name: ["第 4 级输入电容 / Cinv", "Stage 4 input capacitance / Cinv"], min: 1, max: 32, step: 0.05, value: 16, unit: "", digits: 2 },
  ],
  tasks: [
    { id: "two", robot: true, text: ["2 级结构：调反相器尺寸，使总延时不超过这种结构最小延时的 1.01 倍。", "2 stages: size the inverter so the delay is within 1 % of this structure's minimum."],
      demo: { scene: "s2", set: { c2: 3.2 }, press: [], wait: 1 } },
    { id: "three", robot: true, text: ["3 级结构：调两级的尺寸，使总延时不超过最小延时的 1.01 倍。这时三级的努力有什么关系？", "3 stages: size both stages to within 1 % of the minimum delay. How do the three stage efforts compare?"],
      demo: { scene: "s3", set: { c2: 2.35, c3: 6.85 }, press: [], wait: 1 } },
    { id: "four", text: ["4 级结构也调到最优（1 % 以内），和 3 级比较，说明哪种最快、为什么。", "Size the 4-stage structure to within 1 % too, compare with 3 stages, and explain which is fastest."],
      demo: { scene: "s4", set: { c2: 6.35, c3: 5.05, c4: 10.1 }, press: [], wait: 1 } },
  ],
  think: ["换用仿真的 g、p 后，三种结构的延时都变小了，最快的结构变了吗？如果输出还要驱动 300 μm 的连线，H 怎样变，结论会变吗？",
          "With the simulated g and p all three structures get faster; does the fastest one change? If the output also drives a 300 μm wire, how does H change, and does the conclusion?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["每级努力 f", "stage effort f"], color: "#1d6fb8" }, { name: ["最优 F^(1/N)", "optimum F^(1/N)"], color: "#2e7d32" }],
  reset(api, s) { check23(api); },
  readouts(api, s) {
    const f = api.fmt, r = path23(api.scene, api.p, false), N = ST23[api.scene].length, F = GN23 * B23 * H23;
    return [[["路径努力 F = G·B·H", "Path effort F = G·B·H"], f(F, 1)],
            [["每级努力", "Stage efforts"], r.f.map((x) => f(x, 2)).join(" / ")],
            [["最优每级努力 F^(1/N)", "Optimal stage effort"], f(Math.pow(F, 1 / N), 2)],
            [["总延时（手算）", "Total delay (hand model)"], f(r.D, 2) + " τ ≈ " + f(r.D * TAU23, 0) + " ps"],
            [["本结构最小延时", "Minimum for this structure"], f(opt23(api.scene, false), 2) + " τ"],
            [["本尺寸换用仿真 g、p", "These sizes with SPICE g, p"], f(path23(api.scene, api.p, true).D, 2) + " τ"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ink = css("--ink"), mu = css("--muted"), blue = "#1d6fb8", green = "#2e7d32", amber = "#e67e22";
    const st = ST23[api.scene], r = path23(api.scene, api.p, false), N = st.length, F = GN23 * B23 * H23, fopt = Math.pow(F, 1 / N);
    // top: the chain, gate size ∝ sqrt(input capacitance)
    const y = h * 0.2, x0 = w * 0.06, x1 = w * 0.86, dx = (x1 - x0) / N;
    api.line(x0 - 16, y, x0, y, ink, 2); api.label(api.T("地址", "addr"), x0 - 18, y - 14, mu, 11);
    st.forEach((g, i) => {
      const c = r.caps[i], sz = Math.max(8, Math.min(dx * 0.35, 9 * Math.sqrt(c))), cx = x0 + dx * (i + 0.5);
      if (g[4]) { api.rect(cx - sz * 0.6, y - sz, sz * 1.0, sz * 2, null, blue); api.circle(cx + sz * 0.5, y, 4, null, blue); api.label("&", cx - sz * 0.1, y, blue, 12, "center"); }
      else { api.line(cx - sz * 0.6, y - sz, cx - sz * 0.6, y + sz, blue, 2); api.line(cx - sz * 0.6, y - sz, cx + sz * 0.4, y, blue, 2); api.line(cx - sz * 0.6, y + sz, cx + sz * 0.4, y, blue, 2); api.circle(cx + sz * 0.5, y, 4, null, blue); }
      api.line(x0 + dx * i, y, cx - sz * 0.6, y, ink, 2); api.line(cx + sz * 0.5 + 4, y, x0 + dx * (i + 1), y, ink, 2);
      api.label(api.fmt(c, 2), cx, y + sz + 14, mu, 11, "center");
      if (g[3] > 1) api.label("×" + g[3], x0 + dx * (i + 1) - 8, y - 12, amber, 11, "center");
    });
    api.rect(x1 + 6, y - 14, 10, 28, amber); api.label(Q23.Cout_units + " Cinv", x1 + 20, y, amber, 11);
    // bottom: stage efforts against the optimum
    const by = h * 0.45, bh = h * 0.42, fmax = Math.max(12, ...r.f) * 1.1, Y = (v) => by + bh - v / fmax * bh;
    api.line(x0, Y(fopt), x1, Y(fopt), green, 1.5, [5, 4]); api.label("F^(1/N) = " + api.fmt(fopt, 2), x1, Y(fopt) - 10, green, 11, "right");
    r.f.forEach((v, i) => {
      const cx = x0 + dx * (i + 0.5);
      api.rect(cx - dx * 0.18, Y(v), dx * 0.36, by + bh - Y(v), blue);
      api.label(api.fmt(v, 2), cx, Y(v) - 10, ink, 11, "center");
      api.label(st[i][0], cx, by + bh + 12, mu, 11, "center");
    });
  },
});

function check23(api) {
  const r = path23(api.scene, api.p, false), ok = r.D <= 1.01 * opt23(api.scene, false);
  if (!ok) return;
  if (api.scene === "s2") api.done("two");
  if (api.scene === "s3") api.done("three");
  if (api.scene === "s4") api.done("four");
}
