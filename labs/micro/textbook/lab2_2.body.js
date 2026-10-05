// 实验 2.2 门的尺寸（配 2.2 节）。三个场景：n 输入与非门、n 输入或非门、关节使能的与或非门 EN = ¬(A + B·C)。
// 宽度以最小宽度 Wmin 为单位；电阻以参考反相器（Wn = Wmin、Wp = r·Wmin）的下拉、上拉电阻为 1；
// 输入电容以参考反相器的输入电容 Cinv 为 1（= 逻辑努力）。左图按宽度画出每个管子，右图是最坏情况的上拉、下拉电阻。
const R22 = M2_2.P.kn / M2_2.P.kp;
function gate22(scene, p) {
  if (scene === "nand") return { down: p.n / p.wn, up: R22 / p.wp, cin: [(p.wn + p.wp) / (1 + R22)], area: p.n * (p.wn + p.wp) / (1 + R22) };
  if (scene === "nor") return { down: 1 / p.wn, up: p.n * R22 / p.wp, cin: [(p.wn + p.wp) / (1 + R22)], area: p.n * (p.wn + p.wp) / (1 + R22) };
  // 与或非门：下拉 A 单独一路（宽 wna），B、C 串联（各 wn）；上拉 A 与 (B‖C) 串联（各 wp）
  return { down: Math.max(1 / p.wna, 2 / p.wn), up: 2 * R22 / p.wp, cin: [(p.wna + p.wp) / (1 + R22), (p.wn + p.wp) / (1 + R22)],
           area: (p.wna + 2 * p.wn + 3 * p.wp) / (1 + R22) };
}
const ok22 = (g) => Math.abs(g.down - 1) <= 0.05 && Math.abs(g.up - 1) <= 0.05;

WQ.lab({
  title: ["实验 2.2 门的尺寸", "Lab 2.2 Sizing gates"],
  goal: ["调门里 NMOS、PMOS 的宽度，看最坏情况的上拉、下拉电阻和每个输入的电容；按等效反相器定尺寸，比较与非门和或非门。",
         "Change the NMOS and PMOS widths of a gate and watch the worst-case pull-up and pull-down resistance and the input capacitance; size gates as equivalent inverters and compare NAND with NOR."],
  scenes: [
    { id: "nand", name: ["n 输入与非门", "n-input NAND"], hide: ["wna"],
      problem: { title: ["NMOS 串联、PMOS 并联", "Series NMOS, parallel PMOS"],
                 text: ["最坏情况下，下拉要经过全部 n 个串联的 NMOS，上拉只有一个 PMOS 导通。每个管子要多宽，才和参考反相器一样强？",
                        "In the worst case the pull-down goes through all n series NMOS and only one PMOS pulls up. How wide must each transistor be to match the reference inverter?"] } },
    { id: "nor", name: ["n 输入或非门", "n-input NOR"], hide: ["wna"],
      problem: { title: ["NMOS 并联、PMOS 串联", "Parallel NMOS, series PMOS"],
                 text: ["这回串联的是本来就弱的 PMOS。按等效反相器定尺寸后，每个输入的电容是多少？和同样输入数的与非门比一比。",
                        "Now the series devices are the weaker PMOS. After equivalent-inverter sizing, what is the input capacitance? Compare with a NAND of the same fan-in."] } },
    { id: "aoi", robot: true, name: ["关节使能门 EN = ¬(A + B·C)", "Joint enable gate EN = ¬(A + B·C)"], hide: ["n"],
      problem: { title: ["机器人问题：使能门的最坏情况", "Robot problem: the enable gate's worst case"],
                 text: ["A = 急停，B = 限位，C = 方向。下拉：A 单独一路，B、C 串联；上拉：A 与“B、C 并联”串联。让最坏情况的上拉、下拉都和参考反相器一样强，又不浪费面积。",
                        "A = e-stop, B = limit, C = direction. Pull-down: A alone, B and C in series; pull-up: A in series with B‖C. Make the worst-case pull-up and pull-down as strong as the reference inverter without wasting area."] } },
  ],
  params: [
    { id: "n", name: ["输入数 n", "Inputs n"], min: 2, max: 4, step: 1, value: 2, unit: "", digits: 0 },
    { id: "wn", name: ["NMOS 宽度（与或非门为 B、C）/ Wmin", "NMOS width (B, C for the AOI) / Wmin"], min: 1, max: 6, step: 0.25, value: 1, unit: "", digits: 2 },
    { id: "wna", name: ["与或非门 A 的 NMOS 宽度 / Wmin", "AOI: NMOS width of A / Wmin"], min: 1, max: 6, step: 0.25, value: 2, unit: "", digits: 2 },
    { id: "wp", name: ["PMOS 宽度 / Wmin", "PMOS width / Wmin"], min: 1, max: 12, step: 0.05, value: 2, unit: "", digits: 2 },
  ],
  tasks: [
    { id: "nand3", text: ["三输入与非门：调到等效反相器尺寸（最坏上拉、下拉电阻都与参考反相器相差不到 5 %）。", "NAND3: reach equivalent-inverter sizing (worst-case pull-up and pull-down within 5 % of the reference)."],
      demo: { scene: "nand", set: { n: 3, wn: 3, wp: 2.45 }, press: [], wait: 1 } },
    { id: "nor3", text: ["三输入或非门：同样调到等效反相器尺寸，读出每个输入的电容，与三输入与非门比较。", "NOR3: the same sizing; read the input capacitance and compare with the NAND3."],
      demo: { scene: "nor", set: { n: 3, wn: 1, wp: 7.3 }, press: [], wait: 1 } },
    { id: "aoi", robot: true, text: ["使能门：最坏上拉、下拉都与参考反相器相差不到 5 %，且 A 的 NMOS 不超过 1.25 Wmin（不浪费面积）。", "Enable gate: worst-case pull-up and pull-down within 5 % of the reference, with A's NMOS at most 1.25 Wmin."],
      demo: { scene: "aoi", set: { wna: 1, wn: 2, wp: 4.85 }, press: [], wait: 1 } },
  ],
  think: ["为什么并联的管子不能指望“几个一起导通”来降低电阻？如果把最晚到达的信号接到靠近输出的输入上，会快多少——这个实验的模型能回答吗？",
          "Why can't parallel transistors count on conducting together? How much faster is it to connect the latest signal to the input nearest the output — can this lab's model tell?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["NMOS（下拉）", "NMOS (pull-down)"], color: "#1d6fb8" }, { name: ["PMOS（上拉）", "PMOS (pull-up)"], color: "#c0392b" }],
  reset(api, s) { check22(api); },
  readouts(api, s) {
    const f = api.fmt, g = gate22(api.scene, api.p);
    const rows = [[["最坏下拉电阻 / 参考", "Worst pull-down / reference"], f(g.down, 2)],
                  [["最坏上拉电阻 / 参考", "Worst pull-up / reference"], f(g.up, 2)]];
    if (api.scene === "aoi") rows.push([["输入电容 A、B / Cinv", "Input cap A, B / Cinv"], f(g.cin[0], 2) + " / " + f(g.cin[1], 2)]);
    else rows.push([["每个输入的电容 / Cinv", "Input cap per input / Cinv"], f(g.cin[0], 2)]);
    rows.push([["总栅宽 / 参考反相器", "Total width / reference inverter"], f(g.area, 2)], [["r = k′n/k′p", "r = k′n/k′p"], f(R22, 2)]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mu = css("--muted");
    const blue = "#1d6fb8", red = "#c0392b", green = css("--green");
    const g = gate22(api.scene, p);
    // left: transistors as rectangles, width ∝ W
    const x0 = w * 0.06, x1 = w * 0.52, top = h * 0.1, mid = h * 0.5, bot = h * 0.9, unit = Math.min(10, (x1 - x0) / 30);
    api.line(x0, top, x1, top, mu, 2); api.label("VDD", x0, top - 10, mu, 11);
    api.line(x0, bot, x1, bot, mu, 2); api.label("GND", x0, bot + 12, mu, 11);
    api.line(x0, mid, x1 + 20, mid, ink, 2); api.label(api.T("输出", "out"), x1 + 24, mid, ink, 12);
    const box = (cx, y0, y1, wi, col, name) => {
      const ww = Math.max(4, wi * unit);
      api.rect(cx - ww / 2, y0 + 4, ww, y1 - y0 - 8, col);
      api.line(cx, y0, cx, y0 + 4, col, 2); api.line(cx, y1 - 4, cx, y1, col, 2);
      api.label(name, cx, (y0 + y1) / 2, "#fff", 11, "center");
    };
    const series = (cx, y0, y1, k, wi, col, names) => { const dy = (y1 - y0) / k; for (let i = 0; i < k; i++) box(cx, y0 + i * dy, y0 + (i + 1) * dy, wi, col, names[i]); };
    const parallel = (y0, y1, k, wi, col, names) => { for (let i = 0; i < k; i++) { const cx = x0 + (x1 - x0) * (i + 0.5) / k; box(cx, y0, y1, wi, col, names[i]); } };
    const names = ["A", "B", "C", "D"].slice(0, api.scene === "aoi" ? 3 : p.n);
    const cx = (x0 + x1) / 2;
    if (api.scene === "nand") { parallel(top, mid, p.n, p.wp, red, names); series(cx, mid, bot, p.n, p.wn, blue, names); }
    else if (api.scene === "nor") { series(cx, top, mid, p.n, p.wp, red, names); parallel(mid, bot, p.n, p.wn, blue, names); }
    else {
      const ym = (top + mid) / 2;
      box(cx, top, ym, p.wp, red, "A");
      box(x0 + (x1 - x0) * 0.3, ym, mid, p.wp, red, "B"); box(x0 + (x1 - x0) * 0.7, ym, mid, p.wp, red, "C");
      api.line(x0 + (x1 - x0) * 0.3, ym, x0 + (x1 - x0) * 0.7, ym, red, 2);
      box(x0 + (x1 - x0) * 0.3, mid, bot, p.wna, blue, "A");
      series(x0 + (x1 - x0) * 0.7, mid, bot, 2, p.wn, blue, ["B", "C"]);
    }
    // right: worst-case resistances relative to the reference
    const bx = w * 0.66, bw = w * 0.3, by = h * 0.12, bh = h * 0.7, ymax = 3;
    const Y = (v) => by + bh - Math.min(v, ymax) / ymax * bh;
    api.line(bx, Y(1), bx + bw, Y(1), green, 1.5, [5, 4]); api.label(api.T("参考反相器 = 1", "reference = 1"), bx + bw, Y(1) - 26, green, 11, "right");
    [[g.down, blue, api.T("下拉", "down")], [g.up, red, api.T("上拉", "up")]].forEach(([v, col, name], i) => {
      const x = bx + bw * (0.18 + 0.44 * i);
      api.rect(x, Y(v), bw * 0.24, by + bh - Y(v), col);
      api.label(api.fmt(v, 2), x + bw * 0.12, Y(v) - 10, ink, 12, "center");
      api.label(name, x + bw * 0.12, by + bh + 14, mu, 12, "center");
    });
    api.label(api.T("最坏情况电阻 / 参考", "worst-case R / reference"), bx, by - 12, ink, 12);
  },
});

function check22(api) {
  const p = api.p, g = gate22(api.scene, p);
  if (!ok22(g)) return;
  if (api.scene === "nand" && p.n === 3) api.done("nand3");
  if (api.scene === "nor" && p.n === 3) api.done("nor3");
  if (api.scene === "aoi" && p.wna <= 1.25 + 1e-9) api.done("aoi");
}
