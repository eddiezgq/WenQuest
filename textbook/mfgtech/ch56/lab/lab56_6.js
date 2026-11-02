// 实验 56.6 加工方案链（配 56.6 节）。加工方法的数据与数字工厂工艺标准 factory/digital/std/route_methods.yaml 相同（逐行抄录），
// 检查规则与 factory/digital/hub/route.py 的 check_chain 相同：
//   第一环不能是“要接在别的方法之后”的方法；后一环要接在 follows 列出的方法之后；
//   上一环（或毛坯）的公差等级（取上一环经济精度的下限 IT_max）要不粗于这一环要求的 prev_IT，否则“跳级”；
//   淬硬以后的各环要能加工淬硬钢（hard_ok）；
//   热处理以后不再加工时：最后一环的 IT_min 降一级（HEAT_DISTORT = 1）要满足图纸，且要求 Ra < 1.6 的表面热处理后还要精加工；
//   否则最后一环的 IT_min 要满足图纸的 IT，Ra_min 要满足图纸的 Ra。
// 毛坯相当的公差等级：热轧圆钢 IT14、铸件 IT15（BLANK_IT）。工时按每环示意值相加（只作比较用）。
const METH = [
  {"key": "od_rough_turn", "feature": "外圆", "method_zh": "粗车", "method_en": "rough turning", "IT_min": 11, "IT_max": 13, "Ra_min_um": 12.5, "Ra_max_um": 50, "hard_ok": false, "prev_IT": 16, "follows": []},
  {"key": "od_semi_turn", "feature": "外圆", "method_zh": "半精车", "method_en": "semi-finish turning", "IT_min": 8, "IT_max": 10, "Ra_min_um": 3.2, "Ra_max_um": 6.3, "hard_ok": false, "prev_IT": 13, "follows": ["od_rough_turn"]},
  {"key": "od_finish_turn", "feature": "外圆", "method_zh": "精车", "method_en": "finish turning", "IT_min": 7, "IT_max": 8, "Ra_min_um": 0.8, "Ra_max_um": 1.6, "hard_ok": false, "prev_IT": 11, "follows": ["od_rough_turn", "od_semi_turn"]},
  {"key": "od_rough_grind", "feature": "外圆", "method_zh": "粗磨", "method_en": "rough grinding", "IT_min": 7, "IT_max": 8, "Ra_min_um": 0.8, "Ra_max_um": 1.6, "hard_ok": true, "prev_IT": 10, "follows": ["od_semi_turn", "od_finish_turn"]},
  {"key": "od_finish_grind", "feature": "外圆", "method_zh": "精磨", "method_en": "finish grinding", "IT_min": 6, "IT_max": 7, "Ra_min_um": 0.1, "Ra_max_um": 0.8, "hard_ok": true, "prev_IT": 9, "follows": ["od_semi_turn", "od_finish_turn", "od_rough_grind"]},
  {"key": "od_superfinish", "feature": "外圆", "method_zh": "超精加工", "method_en": "superfinishing", "IT_min": 5, "IT_max": 5, "Ra_min_um": 0.012, "Ra_max_um": 0.1, "hard_ok": true, "prev_IT": 7, "follows": ["od_finish_grind"]},
  {"key": "hole_drill", "feature": "孔", "method_zh": "钻", "method_en": "drilling", "IT_min": 11, "IT_max": 13, "Ra_min_um": 12.5, "Ra_max_um": 50, "hard_ok": false, "prev_IT": 16, "follows": []},
  {"key": "hole_core_drill", "feature": "孔", "method_zh": "扩", "method_en": "core drilling", "IT_min": 10, "IT_max": 11, "Ra_min_um": 6.3, "Ra_max_um": 12.5, "hard_ok": false, "prev_IT": 13, "follows": ["hole_drill"]},
  {"key": "hole_rough_bore", "feature": "孔", "method_zh": "粗镗", "method_en": "rough boring", "IT_min": 12, "IT_max": 13, "Ra_min_um": 6.3, "Ra_max_um": 12.5, "hard_ok": false, "prev_IT": 16, "follows": []},
  {"key": "hole_semi_bore", "feature": "孔", "method_zh": "半精镗", "method_en": "semi-finish boring", "IT_min": 9, "IT_max": 10, "Ra_min_um": 3.2, "Ra_max_um": 6.3, "hard_ok": false, "prev_IT": 13, "follows": ["hole_rough_bore", "hole_core_drill"]},
  {"key": "hole_ream", "feature": "孔", "method_zh": "铰", "method_en": "reaming", "IT_min": 7, "IT_max": 9, "Ra_min_um": 0.8, "Ra_max_um": 3.2, "hard_ok": false, "prev_IT": 11, "follows": ["hole_drill", "hole_core_drill", "hole_semi_bore"]},
  {"key": "hole_finish_bore", "feature": "孔", "method_zh": "精镗", "method_en": "finish boring", "IT_min": 7, "IT_max": 8, "Ra_min_um": 0.8, "Ra_max_um": 1.6, "hard_ok": false, "prev_IT": 10, "follows": ["hole_semi_bore"]},
  {"key": "hole_grind", "feature": "孔", "method_zh": "磨孔", "method_en": "internal grinding", "IT_min": 6, "IT_max": 8, "Ra_min_um": 0.4, "Ra_max_um": 0.8, "hard_ok": true, "prev_IT": 9, "follows": ["hole_semi_bore", "hole_ream", "hole_finish_bore"]},
  {"key": "hole_fine_bore", "feature": "孔", "method_zh": "精细镗（金刚镗）", "method_en": "fine boring", "IT_min": 6, "IT_max": 7, "Ra_min_um": 0.05, "Ra_max_um": 0.4, "hard_ok": false, "prev_IT": 9, "follows": ["hole_semi_bore", "hole_finish_bore"]},
  {"key": "plane_rough_mill", "feature": "平面", "method_zh": "粗铣", "method_en": "rough milling", "IT_min": 11, "IT_max": 13, "Ra_min_um": 6.3, "Ra_max_um": 25, "hard_ok": false, "prev_IT": 16, "follows": []},
  {"key": "plane_finish_mill", "feature": "平面", "method_zh": "精铣", "method_en": "finish milling", "IT_min": 8, "IT_max": 10, "Ra_min_um": 1.6, "Ra_max_um": 3.2, "hard_ok": false, "prev_IT": 13, "follows": ["plane_rough_mill"]},
  {"key": "key_mill", "feature": "键槽", "method_zh": "铣键槽", "method_en": "keyway milling", "IT_min": 8, "IT_max": 9, "Ra_min_um": 3.2, "Ra_max_um": 6.3, "hard_ok": false, "prev_IT": 16, "follows": []},
  {"key": "gear_hob", "feature": "齿面", "method_zh": "滚齿", "method_en": "hobbing", "IT_min": 7, "IT_max": 8, "Ra_min_um": 1.6, "Ra_max_um": 3.2, "hard_ok": false, "prev_IT": 16, "follows": []},
  {"key": "gear_shave", "feature": "齿面", "method_zh": "剃齿", "method_en": "shaving", "IT_min": 6, "IT_max": 7, "Ra_min_um": 0.4, "Ra_max_um": 0.8, "hard_ok": false, "prev_IT": 8, "follows": ["gear_hob"]},
  {"key": "gear_grind", "feature": "齿面", "method_zh": "磨齿", "method_en": "gear grinding", "IT_min": 3, "IT_max": 6, "Ra_min_um": 0.2, "Ra_max_um": 0.8, "hard_ok": true, "prev_IT": 8, "follows": ["gear_hob", "gear_shave"]},
  {"key": "gear_hone", "feature": "齿面", "method_zh": "珩齿", "method_en": "gear honing", "IT_min": 6, "IT_max": 7, "Ra_min_um": 0.2, "Ra_max_um": 0.8, "hard_ok": true, "prev_IT": 8, "follows": ["gear_hob", "gear_shave", "gear_grind"]},
];
const MK = Object.fromEntries(METH.map((m) => [m.key, m]));
const FEAT = { od: "外圆", hole: "孔", gear: "齿面" };
const BLANK = { od: ["热轧圆钢", 14], hole: ["铸件（孔已铸出）", 15], gear: ["精车后的齿坯", 11] };
const HEAT_DISTORT = 1, HEAT_RA = 1.6;
const MIN6 = { 粗车: 7, 半精车: 6, 精车: 6, 粗磨: 5, 精磨: 6, 超精加工: 8, 钻: 2, 扩: 2, 粗镗: 4, 半精镗: 4, 铰: 3, 精镗: 5, 磨孔: 8, "精细镗（金刚镗）": 8, 滚齿: 22, 剃齿: 12, 磨齿: 30, 珩齿: 10 };
function list6(sc) { return METH.filter((m) => m.feature === FEAT[sc]); }
function chain6(api) {
  const p = api.p, L = list6(api.scene), keys = [];
  for (let i = 1; i <= 4; i++) { const k = Math.round(p["s" + i]); if (k > 0 && L[k - 1]) keys.push(L[k - 1].key); }
  return keys;
}
function check6(keys, it, ra, hfrom, blankIt) {       // hfrom：从第几环起在淬硬之后（null：不淬硬）
  const out = [], grades = [];
  let prev = blankIt;
  keys.forEach((k, i) => {
    const m = MK[k], fol = m.follows || [];
    if (i === 0 && fol.length) out.push(`${m.method_zh}不能做第一道（它要接在${fol.map((x) => MK[x].method_zh).join("、")}之后）`);
    else if (i > 0 && !fol.includes(keys[i - 1])) out.push(`${m.method_zh}一般不接在${MK[keys[i - 1]].method_zh}之后`);
    if (prev > m.prev_IT) out.push(`${m.method_zh} 之前只到 IT${prev}，粗于它要求的 IT${m.prev_IT}——中间缺了一环（“跳级”）`);
    if (hfrom !== null && i >= hfrom && !m.hard_ok) out.push(`${m.method_zh} 排在淬硬之后：淬硬钢加工不动，淬硬后只能磨（或磨齿、珩齿）`);
    prev = m.IT_max; grades.push([m.IT_min, m.IT_max, m.Ra_min_um, m.Ra_max_um]);
  });
  if (!keys.length) return { out: ["还没有选加工方法"], grades };
  const last = MK[keys[keys.length - 1]];
  if (hfrom !== null && hfrom >= keys.length) {
    if (last.IT_min + HEAT_DISTORT > it) out.push(`热处理后不再精加工，${last.method_zh}的 IT${last.IT_min} 再降约 1 级就达不到要求的 IT${it}`);
    if (ra !== null && ra < HEAT_RA) out.push(`要求 Ra ${ra} µm 的表面热处理后还要精加工（磨）`);
    return { out, grades };
  }
  if (last.IT_min > it) out.push(`最后一环${last.method_zh}的经济精度 IT${last.IT_min}–IT${last.IT_max} 达不到要求的 IT${it}`);
  if (ra !== null && last.Ra_min_um > ra + 1e-9) out.push(`最后一环${last.method_zh}的粗糙度 Ra ${last.Ra_min_um}–${last.Ra_max_um} µm 达不到要求的 Ra ${ra} µm`);
  return { out, grades };
}
function eval6(api) {
  const p = api.p, sc = api.scene, keys = chain6(api), ht = Math.round(p.ht), hard = Math.round(p.hard) === 1;
  const ra = sc === "gear" ? null : p.ra;
  let hfrom = ht > 0 ? Math.min(ht, keys.length) : null;
  const r = check6(keys, Math.round(p.it), ra, hfrom, BLANK[sc][1]);
  if (hard && hfrom === null) r.out.push("图纸要求淬硬（渗碳淬火），方案链里还没有安排热处理");
  if (!hard && hfrom !== null) r.out.push("这个表面不要求淬硬，不必插入热处理");
  const min = keys.reduce((a, k) => a + (MIN6[MK[k].method_zh] || 5), 0);
  return { keys, hfrom, ...r, ok: keys.length > 0 && r.out.length === 0, min };
}
function zh6(api, r) {
  const names = r.keys.map((k) => api.T(MK[k].method_zh, MK[k].method_en));
  if (r.hfrom !== null) names.splice(r.hfrom, 0, api.T("热处理", "heat treatment"));
  return names.join(" → ") || "—";
}
const S6 = (o) => ({ s1: { value: 0 }, s2: { value: 0 }, s3: { value: 0 }, s4: { value: 0 }, ht: { value: 0 }, ...o });

WQ.lab({
  title: ["实验 56.6 加工方案链", "Lab 56.6 Process chains"],
  goal: ["给一个表面的要求（公差等级、粗糙度、是否淬硬后加工），从加工方法里一步步拼出方案链，系统按数字工厂的加工方法表检查每一环：接得上吗、跳级了吗、淬硬后还能不能加工、最后达到图纸了吗。",
         "Given a surface's requirement (IT grade, Ra, hardened or not), build a chain of methods step by step; the system checks every link against the digital factory's method table: does it connect, does it skip a stage, can it cut hardened steel, does the last step meet the drawing?"],
  scenes: [
    { id: "od", name: ["外圆（SH-101）", "Outside diameter (SH-101)"],
      params: S6({ it: { value: 6 }, ra: { value: 0.8 }, hard: { value: 1 } }),
      problem: { title: ["工程问题：SH-101 轴承位和密封轴颈的方案链", "Engineering problem: chains for SH-101's bearing seats and seal journal"],
                 text: ["SH-101 轴承位 Ø25 k6（IT6、Ra 0.8），密封轴颈 Ø24 h8（IT8、Ra 0.8），都在渗碳淬火以后加工到尺寸。从热轧圆钢开始，每个表面经过哪几种加工方法？", "SH-101's bearing seats (IT6, Ra 0.8) and seal journal (IT8, Ra 0.8), both finished after carburizing. From hot-rolled bar, which methods does each surface go through?"] } },
    { id: "hole", name: ["孔（铸出的孔）", "Bore (cored)"], hide: ["hard"],
      params: S6({ it: { value: 7 }, ra: { value: 1.6 }, hard: { value: 0 } }),
      problem: { title: ["工程问题：铸件上 IT7 的孔", "Engineering problem: an IT7 bore in a casting"],
                 text: ["机器人底座铸件上的轴承孔已经铸出，要求 IT7、Ra 1.6，不淬硬。铸出的孔能不能直接铰？", "A robot base casting has a cored bearing bore, IT7, Ra 1.6, not hardened. Can the cored hole be reamed directly?"] } },
    { id: "gear", robot: true, name: ["齿面（SH-101 齿轮）", "Tooth flanks (SH-101 gear)"], hide: ["ra"],
      params: S6({ it: { value: 8 }, ra: { value: 1.6 }, hard: { value: 1 } }),
      problem: { title: ["机器人问题：减速器齿轮 8 级与 6 级", "Robot problem: grade 8 and grade 6 reducer gears"],
                 text: ["SH-101 的齿轮 m2 z24 要 8 级，渗碳淬火。机器人关节的精密减速器要 6 级——方案链差在哪里？（这里用公差等级代表齿轮精度等级。）", "SH-101's gear is grade 8, carburized; a precision robot reducer needs grade 6 — where do the chains differ? (Here the IT grade stands for the gear accuracy grade.)"] } },
  ],
  params: [
    { id: "it", name: ["图纸要求的公差等级 IT", "Required IT grade"], min: 5, max: 12, step: 1, value: 6, unit: "", digits: 0 },
    { id: "ra", name: ["图纸要求的粗糙度 Ra", "Required Ra"], min: 0.1, max: 12.5, step: 0.1, value: 0.8, unit: "µm", digits: 1 },
    { id: "hard", name: ["淬硬后加工（0 否、1 是）", "Finished after hardening (0 no, 1 yes)"], min: 0, max: 1, step: 1, value: 1, unit: "", digits: 0 },
    { id: "s1", name: ["第 1 环（0 空；序号见右侧方法表）", "Step 1 (0 empty; numbers in the method list)"], min: 0, max: 8, step: 1, value: 0, unit: "", digits: 0 },
    { id: "s2", name: ["第 2 环", "Step 2"], min: 0, max: 8, step: 1, value: 0, unit: "", digits: 0 },
    { id: "s3", name: ["第 3 环", "Step 3"], min: 0, max: 8, step: 1, value: 0, unit: "", digits: 0 },
    { id: "s4", name: ["第 4 环", "Step 4"], min: 0, max: 8, step: 1, value: 0, unit: "", digits: 0 },
    { id: "ht", name: ["热处理排在第几环之后（0 没有）", "Heat treatment after step (0 none)"], min: 0, max: 4, step: 1, value: 0, unit: "", digits: 0 },
  ],
  legend: [{ color: "var(--accent)", name: ["每一环后的公差等级", "IT after each step"] }, { color: "var(--warm)", name: ["每一环后的 Ra", "Ra after each step"] }, { color: "var(--red)", name: ["图纸要求、热处理", "drawing, heat treatment"] }],
  tasks: [
    { id: "bearing", text: ["SH-101 轴承位：IT6、Ra 0.8，淬硬后加工。拼出一条可行的方案链。", "SH-101 bearing seat: IT6, Ra 0.8, after hardening. Build a valid chain."],
      demo: { scene: "od", set: { it: 6, ra: 0.8, hard: 1, s1: 1, s2: 2, s3: 3, s4: 5, ht: 3 }, press: [], wait: 1 } },
    { id: "seal", text: ["密封轴颈：IT8、Ra 0.8，淬硬后加工。为什么热处理后还得磨一刀？", "Seal journal: IT8, Ra 0.8, after hardening. Why is a grind still needed after hardening?"],
      demo: { scene: "od", set: { it: 8, ra: 0.8, hard: 1, s1: 1, s2: 2, s3: 4, s4: 0, ht: 2 }, press: [], wait: 1 } },
    { id: "gear", text: ["齿面 6 级（渗碳淬火）：方案链是什么？8 级为什么滚齿后淬火就够了？", "Grade-6 flanks (carburized): what chain? Why is hobbing then hardening enough for grade 8?"],
      demo: { scene: "gear", set: { it: 6, hard: 1, s1: 1, s2: 3, s3: 0, s4: 0, ht: 1 }, press: [], wait: 1 } },
    { id: "hole", text: ["铸出的孔 IT7、Ra 1.6：拼出一条可行的方案链。", "Cored bore IT7, Ra 1.6: build a valid chain."],
      demo: { scene: "hole", set: { it: 7, ra: 1.6, s1: 3, s2: 4, s3: 5, s4: 0, ht: 0 }, press: [], wait: 1 } },
    { id: "jump", text: ["拼一条“跳级”的外圆方案链（例如粗车后直接精磨），看系统给出什么意见、为什么不行。", "Build an OD chain that skips a stage (e.g. rough turning straight to finish grinding); read why it fails."],
      demo: { scene: "od", set: { it: 6, ra: 0.8, hard: 0, s1: 1, s2: 5, s3: 0, s4: 0, ht: 0 }, press: [], wait: 1 } },
  ],
  think: ["方法表里的经济精度是一般生产条件下的范围。机床精度很高、操作很熟练时，能不能少一环？少一环要承担什么风险？", "The table gives economic accuracy under normal conditions. With a very accurate machine and a skilled operator, could a link be dropped? What risk would that carry?"],

  reset(api, s) {},
  update(dt, api, s) { api.stop(); },
  readouts(api) {
    const p = api.p, r = eval6(api), T = api.T, sc = api.scene, it = Math.round(p.it), hard = Math.round(p.hard) === 1;
    if (r.ok && sc === "od" && it === 6 && Math.abs(p.ra - 0.8) < 1e-9 && hard) api.done("bearing");
    if (r.ok && sc === "od" && it === 8 && Math.abs(p.ra - 0.8) < 1e-9 && hard) api.done("seal");
    if (r.ok && sc === "gear" && it === 6 && hard) api.done("gear");               // 8 级的结果在读数里一并给出
    if (r.ok && sc === "hole" && it === 7 && Math.abs(p.ra - 1.6) < 1e-9 && !hard) api.done("hole");
    if (sc === "od" && r.out.some((x) => x.includes("跳级") || x.includes("不接在"))) api.done("jump");
    const L = list6(sc);
    const rows = [
      [["方法表（序号）", "method list (no.)"], L.map((m, i) => `${i + 1} ${T(m.method_zh, m.method_en)}`).join("  ")],
      [["毛坯", "blank"], T(BLANK[sc][0], BLANK[sc][0]) + ` ≈ IT${BLANK[sc][1]}`],
      [["方案链", "chain"], zh6(api, r)],
      [["检查结果", "check"], r.ok ? T("可行：每一环都接得上，最后达到图纸", "valid: every link connects and the drawing is met") : r.out.slice(0, 3).join("；")],
      [["工时（示意，只作比较）", "time (illustr., for comparison)"], api.fmt(r.min, 0) + " min"],
    ];
    if (sc === "gear") {
      const g8 = check6(["gear_hob"], 8, null, 1, BLANK.gear[1]);
      rows.push([["对照：8 级“滚齿 → 热处理”", "check: grade 8 hob → harden"], g8.out.length ? g8.out.join("；") : T("可行（滚齿按 7 级做，淬火降一级正好 8 级）", "valid (hob to 7, hardening costs one grade)")]);
    }
    return rows;
  },
  draw(api) {
    const r = eval6(api), { w, h } = api, css = api.css, p = api.p, sc = api.scene;
    const names = [api.T("毛坯", "blank")], its = [BLANK[sc][1]], ras = [50];
    r.keys.forEach((k, i) => { names.push(api.T(MK[k].method_zh, MK[k].method_en)); its.push(MK[k].IT_max); ras.push(MK[k].Ra_max_um); });
    const n = names.length, xs = names.map((_, i) => i);
    const ptsIt = [], ptsRa = [];
    xs.forEach((x, i) => { if (i) { ptsIt.push([x - 1, its[i - 1]]); ptsRa.push([x - 1, Math.log10(ras[i - 1])]); } ptsIt.push([x, its[i]]); ptsRa.push([x, Math.log10(ras[i])]); });
    const P = api.plot(w * 0.08, h * 0.06, w * 0.86, h * 0.38, [{ pts: ptsIt.map(([x, y]) => [x, -y]), color: css("--accent") }],
                       { xmin: -0.3, xmax: Math.max(n - 1, 1) + 0.3, ymin: -16, ymax: -4, xlabel: "", ylabel: api.T("公差等级 IT（向上越精）", "IT grade (finer upwards)") });
    api.line(P.X(-0.3), P.Y(-Math.round(p.it)), P.X(Math.max(n - 1, 1) + 0.3), P.Y(-Math.round(p.it)), css("--red"), 1, [5, 4]);
    xs.forEach((x, i) => { api.circle(P.X(x), P.Y(-its[i]), 4, css("--accent")); api.label("IT" + its[i], P.X(x), P.Y(-its[i]) - 9, css("--accent"), 11, "center"); });
    if (sc !== "gear") {
      const Q = api.plot(w * 0.08, h * 0.56, w * 0.86, h * 0.32, [{ pts: ptsRa, color: css("--warm") }],
                         { xmin: -0.3, xmax: Math.max(n - 1, 1) + 0.3, ymin: -1.2, ymax: 1.8, xlabel: "", ylabel: api.T("Ra / µm（对数）", "Ra / µm (log)") });
      api.line(Q.X(-0.3), Q.Y(Math.log10(p.ra)), Q.X(Math.max(n - 1, 1) + 0.3), Q.Y(Math.log10(p.ra)), css("--red"), 1, [5, 4]);
      xs.forEach((x, i) => { api.circle(Q.X(x), Q.Y(Math.log10(ras[i])), 4, css("--warm")); api.label(String(ras[i]), Q.X(x), Q.Y(Math.log10(ras[i])) - 9, css("--warm"), 11, "center"); });
    }
    xs.forEach((x, i) => api.label(names[i], P.X(x), h * 0.95, css("--ink"), 12, "center"));
    if (r.hfrom !== null) { api.line(P.X(r.hfrom + 0.5), h * 0.04, P.X(r.hfrom + 0.5), h * 0.9, css("--red"), 3); api.label(api.T("热处理", "heat"), P.X(r.hfrom + 0.5) + 4, h * 0.05, css("--red"), 12); }
  },
});
