// 实验 54.7 均值–极差图与判异（配 54.7 节）。过程：SH-301 轴承位 Ø35 k6（35.002–35.018），正常时均值 35.009、σ = 1.2 µm（算例 54.7.1 的重复性）。
// 共 25 个子组；前 10 组是正常过程，用来求控制限（x̿ ± A₂R̄，R 图 D₃R̄–D₄R̄）；从第“开始”组起加入变化：均值偏移、分散变大、逐组漂移。
// 判异规则与 hub/spc.py 的 special_causes 相同（规则 1–4）；常数 A₂、D₃、D₄、d₂ 与 hub/spc.py 相同。
const A2_ = { 2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308 };
const D3_ = { 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223 };
const D4_ = { 2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777 };
const MU0 = 35.009, SG0 = 0.0012, LSL = 35.002, USL = 35.018, K = 25, K1 = 10;
function rng57(seed) { let a = seed * 2654435761 >>> 0; return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
function rules57(z) {           // 规则 1–4：返回 [{rule, index}]，同一规则连续触发只记第一点
  const hit = (r, i) => {
    if (r === 1) return Math.abs(z[i]) > 3;
    if (r === 4) return i >= 7 && (z.slice(i - 7, i + 1).every((x) => x > 0) || z.slice(i - 7, i + 1).every((x) => x < 0));
    const [m, k, lim] = r === 2 ? [3, 2, 2] : [5, 4, 1];
    if (i < m - 1) return false;
    const w = z.slice(i - m + 1, i + 1);
    return [1, -1].some((sg) => w.filter((x) => sg * x > lim).length >= k && sg * z[i] > lim);
  };
  const out = [];
  for (const r of [1, 2, 3, 4]) { let prev = false; z.forEach((_, i) => { const h = hit(r, i); if (h && !prev) out.push({ rule: r, index: i }); prev = h; }); }
  return out.sort((a, b) => a.index - b.index || a.rule - b.rule);
}
function sim57(p) {
  const R = rng57(Math.round(p.seed)), n = Math.round(p.n), st = Math.round(p.start) - 1;
  const g = () => { const u = Math.max(R(), 1e-12), v = R(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); };
  const groups = [];
  for (let k = 0; k < K; k++) {
    const after = k >= st, mu = MU0 + (after ? p.shift * SG0 + p.drift * SG0 * (k - st + 1) : 0), sg = SG0 * (after ? p.spread : 1);
    groups.push(Array.from({ length: n }, () => mu + sg * g()));
  }
  const xb = groups.map((x) => x.reduce((a, b) => a + b, 0) / n), rr = groups.map((x) => Math.max(...x) - Math.min(...x));
  const c = xb.slice(0, K1).reduce((a, b) => a + b, 0) / K1, rb = rr.slice(0, K1).reduce((a, b) => a + b, 0) / K1;
  const ucl = c + A2_[n] * rb, lcl = c - A2_[n] * rb, s3 = (ucl - c);
  const hx = rules57(xb.map((x) => 3 * (x - c) / s3)), hr = rr.map((r, i) => ({ i, r })).filter((q) => q.r > D4_[n] * rb || q.r < D3_[n] * rb - 1e-12).map((q) => q.i);
  const muE = MU0 + p.shift * SG0, sgE = SG0 * p.spread;           // 变化以后的过程（不计漂移）
  const cpk = Math.min(USL - muE, muE - LSL) / (3 * sgE), cp = (USL - LSL) / (6 * sgE);
  const firstX = hx.find((h) => h.index >= st), firstR = hr.find((i) => i >= st);
  const falseX = hx.filter((h) => h.index < st).length;
  return { xb, rr, c, rb, ucl, lcl, uclR: D4_[n] * rb, lclR: D3_[n] * rb, hx, hr, st, cp, cpk, firstX, firstR, falseX, n };
}

WQ.lab({
  title: ["实验 54.7 均值–极差图与判异", "Lab 54.7 X̄–R charts and the run rules"],
  goal: ["在 SH-301 轴承位的过程里加入一种变化——均值偏移、分散变大或逐组漂移，看均值图、极差图在第几组报警、用的是哪条规则；改子组容量，看报警快慢；算变化以后的工序能力。",
         "Add one change to the SH-301 bearing-seat process — a mean shift, a wider spread or a drift — and see which subgroup and which rule raises the alarm on the X̄ and R charts; change the subgroup size and see how fast it reacts; and find the capability after the change."],
  scenes: [
    { id: "chart", name: ["SH-301 轴承位 Ø35 k6", "SH-301 bearing seat Ø35 k6"],
      problem: { title: ["工程问题：控制图怎样比超差件更早发现问题", "Engineering problem: how a control chart sees trouble before parts go out of tolerance"],
                 text: ["质检员每个修整周期抽检一组。等到零件超差才处理，已经晚了；控制图上的点一旦“不随机”，就要停下来找原因。不同的变化在均值图、极差图上的表现不同。",
                        "The inspector samples one subgroup per dressing cycle. Waiting for out-of-tolerance parts is too late; once the points stop looking random, stop and look for the cause. Different changes show up differently on the X̄ and R charts."] } },
  ],
  params: [
    { id: "shift", name: ["均值偏移（σ 的倍数）", "Mean shift (in σ)"], min: 0, max: 3, step: 0.1, value: 0, unit: "σ", digits: 1 },
    { id: "spread", name: ["分散变为原来的", "Spread × "], min: 1, max: 2.5, step: 0.1, value: 1, unit: "×", digits: 1 },
    { id: "drift", name: ["每组漂移（σ 的倍数）", "Drift per subgroup (in σ)"], min: 0, max: 0.5, step: 0.05, value: 0, unit: "σ", digits: 2 },
    { id: "start", name: ["变化从第几组开始", "Change starts at subgroup"], min: 11, max: 20, step: 1, value: 13, unit: "", digits: 0 },
    { id: "n", name: ["子组容量 n", "Subgroup size n"], min: 2, max: 10, step: 1, value: 5, unit: "", digits: 0 },
    { id: "seed", name: ["随机数种子（换一批数据）", "Random seed (another batch)"], min: 1, max: 20, step: 1, value: 1, unit: "", digits: 0 },
  ],
  legend: [{ color: "var(--accent)", name: ["子组均值 / 极差", "subgroup mean / range"] }, { color: "var(--red)", name: ["控制限、报警点", "limits, alarms"] }],
  tasks: [
    { id: "shift", text: ["均值偏移 1.5σ（从第 13 组起）：均值图在第几组报警？哪条规则？极差图有没有反应？", "A 1.5σ mean shift from subgroup 13: when and by which rule does the X̄ chart alarm? Does the R chart react?"],
      demo: { scene: "chart", set: { shift: 1.5, spread: 1, drift: 0, start: 13, n: 5, seed: 1 }, press: [], wait: 1 } },
    { id: "spread", text: ["分散变为 2 倍：哪张图先报警？", "Spread × 2: which chart alarms first?"],
      demo: { scene: "chart", set: { shift: 0, spread: 2, drift: 0, start: 13, n: 5, seed: 1 }, press: [], wait: 1 } },
    { id: "drift", text: ["每组漂移 0.3σ：报警用的是哪条规则？与均值偏移有什么不同？", "A drift of 0.3σ per subgroup: which rule alarms? How does it differ from a shift?"],
      demo: { scene: "chart", set: { shift: 0, spread: 1, drift: 0.3, start: 13, n: 5, seed: 1 }, press: [], wait: 1 } },
    { id: "size", text: ["均值偏移 1σ：子组容量取 8，变化后几组以内报警？取 2 呢？", "A 1σ shift: with n = 8, how many subgroups until the alarm? With n = 2?"],
      demo: { scene: "chart", set: { shift: 1, spread: 1, drift: 0, start: 13, n: 8, seed: 1 }, press: [], wait: 1 } },
    { id: "cpk", text: ["分散变为 1.5 倍时，均值偏移多少，变化后的 Cpk 降到 1.33？", "With the spread × 1.5, how large a shift brings the Cpk after the change down to 1.33?"],
      demo: { scene: "chart", set: { shift: 1.5, spread: 1.5, drift: 0, start: 13, n: 5, seed: 1 }, press: [], wait: 1 } },
  ],
  think: ["为什么 SH-301 的子组按一个修整周期取（10 件一组），而不是随便 5 件一组？如果子组跨过修整点，极差图会怎样？", "Why are SH-301's subgroups one dressing cycle (10 parts) rather than any 5? What would the R chart show if a subgroup straddled a dressing?"],

  reset(api, s) { s.r = sim57(api.p); },
  update(dt, api, s) { s.r = sim57(api.p); api.stop(); },
  readouts(api, s) {
    const p = api.p, r = s.r || sim57(p), T = api.T, f = (v) => api.fmt(v, 4);
    const delay = r.firstX ? r.firstX.index - r.st + 1 : null;
    if (Math.abs(p.shift - 1.5) < 0.05 && p.spread === 1 && p.drift === 0 && r.firstX) api.done("shift");
    if (p.shift === 0 && Math.abs(p.spread - 2) < 0.05 && p.drift === 0 && r.firstR !== undefined) api.done("spread");
    if (p.shift === 0 && p.spread === 1 && Math.abs(p.drift - 0.3) < 0.03 && r.firstX) api.done("drift");
    if (Math.abs(p.shift - 1) < 0.05 && p.spread === 1 && p.drift === 0 && p.n >= 8 && r.firstX && delay <= 3) api.done("size");
    if (Math.abs(p.spread - 1.5) < 0.05 && Math.abs(r.cpk - 1.33) < 0.035) api.done("cpk");
    return [
      [["控制限（前 10 组）", "limits (first 10 subgroups)"], `x̿ = ${f(r.c)}，UCL = ${f(r.ucl)}，LCL = ${f(r.lcl)}；R̄ = ${api.fmt(r.rb * 1000, 2)} µm`],
      [["均值图第一次报警（变化后）", "first X̄ alarm after the change"], r.firstX ? T(`第 ${r.firstX.index + 1} 组，规则 ${r.firstX.rule}（变化后第 ${delay} 组）`, `subgroup ${r.firstX.index + 1}, rule ${r.firstX.rule} (${delay} after)`) : T("没有报警", "none")],
      [["极差图第一次报警（变化后）", "first R alarm after the change"], r.firstR !== undefined ? T(`第 ${r.firstR + 1} 组`, `subgroup ${r.firstR + 1}`) : T("没有报警", "none")],
      [["变化前的误报警", "false alarms before the change"], String(r.falseX)],
      [["变化以后的 Cp / Cpk", "Cp / Cpk after the change"], api.fmt(r.cp, 2) + " / " + api.fmt(r.cpk, 2) + (r.cpk < 1.33 ? T("（低于 1.33）", " (below 1.33)") : "")],
    ];
  },
  draw(api, s) {
    const r = s.r || sim57(api.p), { w, h } = api, css = api.css;
    const panel = (y0, hh, vals, c, u, l, hits, lab) => {
      const lo = Math.min(l, ...vals), hi = Math.max(u, ...vals), pad = (hi - lo) * 0.15;
      const X = (i) => w * 0.1 + w * 0.85 * i / (K - 1), Y = (v) => y0 + hh - (v - lo + pad) / (hi - lo + 2 * pad) * hh;
      api.rect(w * 0.1 + w * 0.85 * (r.st - 0.5) / (K - 1), y0, w * 0.85 * (K - r.st + 0.5) / (K - 1), hh, "rgba(192,80,77,0.08)");
      [[c, css("--muted")], [u, css("--red")], [l, css("--red")]].forEach(([v, col]) => api.line(X(0), Y(v), X(K - 1), Y(v), col, 1));
      for (let i = 1; i < K; i++) api.line(X(i - 1), Y(vals[i - 1]), X(i), Y(vals[i]), css("--accent"), 1.5);
      vals.forEach((v, i) => api.circle(X(i), Y(v), hits.includes(i) ? 6 : 3, hits.includes(i) ? css("--red") : css("--accent")));
      api.label(lab, w * 0.1, y0 - 6, css("--muted"), 12);
    };
    panel(h * 0.08, h * 0.38, r.xb, r.c, r.ucl, r.lcl, r.hx.map((q) => q.index), api.T("均值图 X̄（mm）", "X̄ chart (mm)"));
    panel(h * 0.58, h * 0.32, r.rr, r.rb, r.uclR, r.lclR, r.hr, api.T("极差图 R（mm）", "R chart (mm)"));
  },
});
