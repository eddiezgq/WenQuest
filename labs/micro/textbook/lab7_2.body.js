// 实验 7.2 SRAM 单元的蝴蝶曲线（配 7.2 节）。6 管单元：存取管为最小宽度，下拉管 = CR 倍，上拉管 = PR 倍。
// 曲线用手算模型实时计算（M7_2.sramCurve，平方律，与书中程序 conventions/mos.py 一致）；SNM 用 Seevinck 法。
// 旁边给 SKY130 仿真值（params.json 的 sram_sim，calib/calib_sram.py；读出 SNM 按 CR 插值、PR = 1，写入裕量按 PR 插值、CR = 2）。
const VDD72 = M7_2.P.VDD, LIM72 = M7_2.P.problems.p72.snm_min_frac * VDD72;
const CRMIN72 = (() => { for (let c = 1; c <= 3.0001; c += 0.25) if (M7_2.sramSimSnm(c, 'read') >= LIM72) return Math.round(c * 100) / 100; return 3; })();
function lobes72(xs, ys) {   // 两瓣里最大的正方形：[[边长, x0, y0], …]（与书中程序 7.2.1 的 lobes 同一算法）
  const s2 = Math.SQRT2, cmp = (p, q) => p[0] - q[0] || p[1] - q[1];
  const a = xs.map((x, i) => [(x - ys[i]) / s2, (x + ys[i]) / s2]).sort(cmp), b = xs.map((x, i) => [(ys[i] - x) / s2, (ys[i] + x) / s2]).sort(cmp);
  const at = (c, u) => {
    if (u <= c[0][0] || u >= c[c.length - 1][0]) return null;
    for (let i = 0; i < c.length - 1; i++) if (c[i][0] <= u && u <= c[i + 1][0]) {
      const t = c[i + 1][0] > c[i][0] ? (u - c[i][0]) / (c[i + 1][0] - c[i][0]) : 0; return c[i][1] + t * (c[i + 1][1] - c[i][1]);
    }
    return null;
  };
  const best = { 1: [0, 0, 0, 0], '-1': [0, 0, 0, 0] };
  for (let i = 1; i < 400; i++) {
    const u = -VDD72 / s2 + 2 * VDD72 / s2 * i / 400, va = at(a, u), vb = at(b, u);
    if (va === null || vb === null) continue;
    const sg = va > vb ? 1 : -1;
    if (Math.abs(va - vb) > best[sg][0]) best[sg] = [Math.abs(va - vb), u, va, vb];
  }
  return [1, -1].map((sg) => {
    const [dv, u, va, vb] = best[sg], xa = (u + va) / s2, ya = (va - u) / s2, xb = (u + vb) / s2, yb = (vb - u) / s2;
    return [dv / s2, Math.min(xa, xb), Math.min(ya, yb)];
  });
}

WQ.lab({
  title: ["实验 7.2 SRAM 单元的蝴蝶曲线", "Lab 7.2 Butterfly curves of an SRAM cell"],
  goal: ["故障录波缓冲的 6 管单元：调单元比和上拉比，看保持与读出时的蝴蝶曲线和静态噪声容限，以及写入裕量，找出读写都可靠的尺寸。",
         "The 6T cell of the fault-recording buffer: vary the cell and pull-up ratios, watch the hold and read butterfly curves, the static noise margin and the write margin, and find sizes that read and write reliably."],
  scenes: [
    { id: "cell", robot: true, name: ["录波缓冲的单元", "The buffer's cell"], hide: [],
      problem: { title: ["机器人问题：读不坏、写得进", "Robot problem: no read upset, still writable"],
                 text: ["要求读出 SNM 与写入裕量都不小于 0.2·VDD = 0.36 V。单元比、上拉比各取多少？",
                        "Both read SNM and write margin must be at least 0.2·VDD = 0.36 V. Choose the cell and pull-up ratios."] } },
  ],
  params: [
    { id: "cr", name: ["单元比 CR = W下拉/W存取", "Cell ratio CR = W_PD/W_PG"], min: 1, max: 3, step: 0.25, value: 1, unit: "", digits: 2 },
    { id: "pr", name: ["上拉比 PR = W上拉/W存取", "Pull-up ratio PR = W_PU/W_PG"], min: 1, max: 3, step: 0.5, value: 1, unit: "", digits: 1 },
    { id: "mode", name: ["状态（1 保持，2 读出）", "State (1 hold, 2 read)"], min: 1, max: 2, step: 1, value: 2, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "crmin", robot: true, text: ["读出状态：按仿真值找出读出 SNM ≥ 0.36 V 的最小单元比。", "Read state: find the smallest cell ratio whose simulated read SNM ≥ 0.36 V."],
      demo: { scene: "cell", set: { cr: 1.5, pr: 1, mode: 2 }, press: [], wait: 1 } },
    { id: "hold", text: ["CR = 2：切到保持状态，比较保持与读出的 SNM。", "CR = 2: switch to hold and compare the hold and read SNM."],
      demo: { scene: "cell", set: { cr: 2, pr: 1, mode: 1 }, press: [], wait: 1 } },
    { id: "pr3", text: ["CR = 2：把上拉比加到 3，写入裕量还满足要求吗？", "CR = 2: raise the pull-up ratio to 3. Is the write margin still enough?"],
      demo: { scene: "cell", set: { cr: 2, pr: 3, mode: 2 }, press: [], wait: 1 } },
  ],
  think: ["读出时蝴蝶曲线的哪一部分变了？为什么增大单元比能让眼睛变大？", "Which part of the butterfly changes in the read state? Why does a larger cell ratio enlarge the eyes?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["传输特性（模型）", "transfer curves (model)"], color: "#1d6fb8" }, { name: ["最大正方形", "largest squares"], color: "#e67e22" }],
  reset(api, s) {
    const p = api.p, mode = p.mode === 1 ? 'hold' : 'read';
    s.c = M7_2.sramCurve(p.cr, p.pr, mode, 0.01);
    s.sq = lobes72(s.c.xs, s.c.ys);
    s.snm = M7_2.sramSnm(p.cr, p.pr, mode);
    s.wt = M7_2.sramWriteTrip(p.cr, p.pr);
    check72(api);
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, ok = (v) => (v >= LIM72 ? api.T("满足", "ok") : api.T("不满足", "fails"));
    const simR = M7_2.sramSimSnm(p.cr, 'read'), simH = M7_2.sramSimSnm(p.cr, 'hold'), simW = M7_2.sramSimWrite(p.pr);
    return [[["SNM（模型，当前状态）", "SNM (model, this state)"], f(s.snm * 1000, 0) + " mV"],
            [["SNM 仿真：读出 / 保持（PR = 1）", "SNM sim.: read / hold (PR = 1)"], f(simR * 1000, 0) + " / " + f(simH * 1000, 0) + " mV，" + api.T("读出", "read ") + ok(simR)],
            [["写入裕量：模型（当前 CR）/ 仿真（CR = 2）", "Write margin: model (this CR) / sim. (CR = 2)"], f(s.wt * 1000, 0) + " / " + f(simW * 1000, 0) + " mV，" + ok(simW)],
            [["六管总宽", "Total width of six FETs"], f(2 * (p.cr + p.pr + 1) * M7_2.P.Wmin, 2) + " μm"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, mu = css("--muted"), ink = css("--ink"), blue = "#1d6fb8";
    const sz = Math.min(w * 0.6, h * 0.82), x0 = (w - sz) / 2 + w * 0.05, y0 = h * 0.06;
    const ax = api.plot(x0, y0, sz, sz, [{ pts: s.c.xs.map((x, i) => [x, s.c.ys[i]]), color: blue }, { pts: s.c.xs.map((x, i) => [s.c.ys[i], x]), color: blue }],
                        { xmin: 0, xmax: VDD72, ymin: 0, ymax: VDD72, xlabel: "Q / V", ylabel: "QB / V" });
    s.sq.forEach(([e, xa, ya]) => {
      if (e <= 0) return;
      api.rect(ax.X(xa), ax.Y(ya + e), ax.X(xa + e) - ax.X(xa), ax.Y(ya) - ax.Y(ya + e), "rgba(230,126,34,0.35)");
    });
    api.label("0", x0, y0 + sz + 13, mu, 10, "center");
    api.label(api.fmt(VDD72, 1), x0 + sz, y0 + sz + 26, mu, 10, "right");
    api.label((api.p.mode === 1 ? api.T("保持", "hold") : api.T("读出", "read")) + "  SNM " + api.fmt(s.snm * 1000, 0) + " mV", x0 + sz - 6, y0 + 18, ink, 12, "right");
  },
});

function check72(api) {
  const p = api.p;
  if (p.mode === 2 && Math.abs(p.cr - CRMIN72) < 1e-9) api.done("crmin");
  if (p.mode === 1 && p.cr === 2) api.done("hold");
  if (p.pr === 3 && p.cr === 2) api.done("pr3");
}
