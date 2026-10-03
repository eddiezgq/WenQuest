// 实验 1.5 游标卡尺与螺旋测微器（配 1.5 节）。画面上是真实的刻度，读数要自己读：
// 卡尺读数 = 主尺整毫米 + 对齐的游标格数 × 0.02 mm；千分尺读数 = 套筒读数（0.5 mm 一格）+ 微分筒格数 × 0.01 mm（估读一位）。
// 转接盘各位置的外径和厚度是固定的一组数（学生事先不知道，与正文算例不同）；记录的数据放在闭包里，重置时不丢。
const POS15 = { D: [62.98, 62.98, 62.96, 62.94, 63.00, 62.96, 62.98, 62.96, 62.94, 62.98], h: [8.014, 8.012, 8.013, 8.015, 8.013], coin: [24.98] };
const rec15 = { D: [], h: [], coin: [], i: { D: 0, h: 0, coin: 0 }, ok: { D: 0, h: 0, coin: 0 } };
const key15 = (sc) => (sc === "caliper" ? "D" : sc === "micro" ? "h" : "coin");
const truth15 = (sc) => { const k = key15(sc); return POS15[k][rec15.i[k] % POS15[k].length]; };
const mine15 = (api) => (api.scene === "micro" ? api.p.sleeve + 0.01 * api.p.div : api.p.mm + 0.02 * api.p.n);
function U15() {     // 由记录的外径算扩展不确定度（k = 2）：A 类 s/√n 与 B 类 0.03/√3 合成
  const x = rec15.D, n = x.length, m = x.reduce((a, b) => a + b, 0) / n;
  const s = Math.sqrt(x.reduce((a, b) => a + (b - m) * (b - m), 0) / (n - 1));
  return 2 * Math.sqrt(s * s / n + 0.03 * 0.03 / 3);
}

WQ.lab({
  title: ["实验 1.5 游标卡尺与螺旋测微器", "Lab 1.5 Vernier caliper and micrometer"],
  goal: ["学会读游标卡尺和螺旋测微器，在不同位置重复测量，用 A 类和 B 类评定写出带不确定度的测量结果。",
         "Learn to read a vernier caliper and a micrometer, repeat the measurement at different places, and report the result with A- and B-type uncertainties."],
  scenes: [
    { id: "caliper", robot: true, name: ["卡尺测转接盘外径", "Caliper: adapter-plate diameter"], hide: ["sleeve", "div"],
      problem: { title: ["机器人问题：UR5e 夹爪转接盘的来料检验", "Robot problem: inspecting the UR5e gripper adapter plate"],
                 text: ["图样要求外径 63.00 mm、公差 −0.05～0 mm。用分度值 0.02 mm 的卡尺（最大允许误差 ±0.03 mm）在不同位置测外径。",
                        "The drawing asks for a diameter of 63.00 mm, tolerance −0.05 to 0 mm. Measure it at several places with a 0.02 mm caliper (maximum permissible error ±0.03 mm)."] } },
    { id: "micro", robot: true, name: ["千分尺测转接盘厚度", "Micrometer: plate thickness"], hide: ["mm", "n", "look", "Uhat"],
      problem: { title: ["机器人问题：转接盘的厚度", "Robot problem: the plate's thickness"],
                 text: ["用分度值 0.01 mm 的螺旋测微器（最大允许误差 ±0.004 mm）测厚度，估读到 0.001 mm。", "Measure the thickness with a 0.01 mm micrometer (±0.004 mm), estimating to 0.001 mm."] } },
    { id: "coin", name: ["卡尺测一元硬币", "Caliper: a 1-yuan coin"], hide: ["sleeve", "div", "Uhat"],
      problem: { title: ["生活中的例子：一元硬币有多大", "Everyday example: how big is a 1-yuan coin"],
                 text: ["用卡尺量一枚一元硬币的直径。", "Measure the diameter of a 1-yuan coin with the caliper."] } },
  ],
  params: [
    { id: "mm", name: ["主尺读数（整毫米）", "Main scale (whole mm)"], min: 0, max: 100, step: 1, value: 60, unit: "mm", digits: 0 },
    { id: "n", name: ["与主尺对齐的游标格数", "Vernier line that lines up"], min: 0, max: 49, step: 1, value: 0, digits: 0 },
    { id: "look", name: ["放大镜位置（游标第几格）", "Magnifier at vernier line"], min: 0, max: 49, step: 1, value: 0, digits: 0 },
    { id: "sleeve", name: ["套筒读数", "Sleeve reading"], min: 0, max: 24.5, step: 0.5, value: 7.5, unit: "mm", digits: 1 },
    { id: "div", name: ["微分筒格数（估读一位）", "Thimble divisions (one estimated digit)"], min: 0, max: 49.9, step: 0.1, value: 0, digits: 1 },
    { id: "Uhat", name: ["你算出的外径扩展不确定度 U", "Your expanded uncertainty U"], min: 0, max: 0.1, step: 0.001, value: 0.05, unit: "mm", digits: 3 },
  ],
  buttons: [{ id: "record", name: ["记录我的读数", "Record my reading"], primary: true }, { id: "next", name: ["换个位置", "Another place"] },
            { id: "sweep", name: ["自动记录全部位置", "Record all places"] }, { id: "clear", name: ["清空记录", "Clear records"] }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "cal", robot: true, text: ["卡尺：调“主尺读数”和“对齐的游标格数”，读对一次外径（点“记录我的读数”核对）。", "Caliper: set the whole millimetres and the aligned vernier line to read the diameter correctly once (press “Record my reading”)."],
      demo: { scene: "caliper", set: { mm: 62, n: 49 }, press: ["clear", "record"], wait: 1 } },
    { id: "mic", robot: true, text: ["千分尺：读对一次厚度（估读一位，误差不超过 0.002 mm）。", "Micrometer: read the thickness correctly once (estimated digit within 0.002 mm)."],
      demo: { scene: "micro", set: { sleeve: 8, div: 1.4 }, press: ["clear", "record"], wait: 1 } },
    { id: "coin", text: ["硬币：读出一元硬币的直径。", "Coin: read the diameter of a 1-yuan coin."],
      demo: { scene: "coin", set: { mm: 24, n: 49 }, press: ["record"], wait: 1 } },
    { id: "U", robot: true, text: ["记录外径的 10 个位置，自己算出扩展不确定度 U（k = 2），把“你算出的 U”调到正确值 ±0.0035 mm 以内（修约后的 0.04 也算对）。", "Record the diameter at all 10 places, compute U (k = 2) yourself and set “Your U” within ±0.0035 mm (the rounded 0.04 also counts)."],
      demo: { scene: "caliper", set: { Uhat: 0.037 }, press: ["clear", "sweep"], wait: 1 } },
  ],
  think: ["卡尺读数的分散（A 类）和卡尺本身的最大允许误差（B 类），哪一个对结果影响大？多测几次能不能把 U 减到 0.01 mm 以下？",
          "Which matters more here, the scatter of readings (A-type) or the caliper's own error (B-type)? Can more readings bring U below 0.01 mm?"],

  reset(api, s) {},
  action(id, api, s) {
    const k = key15(api.scene), P = POS15[k];
    if (id === "clear") { rec15[k].length = 0; rec15.i[k] = 0; s.msg = ""; }
    if (id === "next") { rec15.i[k] = (rec15.i[k] + 1) % P.length; s.msg = ""; }
    if (id === "sweep") { rec15[k].length = 0; for (let j = 0; j < P.length; j++) rec15[k].push(P[j]); rec15.i[k] = 0; s.msg = api.T("已记录全部位置", "all places recorded"); }
    if (id === "record") {
      const t = truth15(api.scene), m = mine15(api), tol = api.scene === "micro" ? 0.0021 : 0.001;
      if (Math.abs(m - t) <= tol) {
        rec15[k].push(Math.round(m * 1000) / 1000); rec15.ok[k]++;
        s.msg = api.T("读对了，已记录。点“换个位置”再测。", "Correct, recorded. Press “Another place” and measure again.");
        if (k === "D") api.done("cal"); if (k === "h") api.done("mic"); if (k === "coin") api.done("coin");
      } else if (k === "h" && Math.abs(Math.abs(m - t) - 0.5) < 0.01)
        s.msg = api.T("差了 0.5 mm：看看微分筒边缘左边，基准线下方的半毫米线有没有露出来。", "Off by 0.5 mm: check whether a half-millimetre mark below the line shows left of the thimble edge.");
      else s.msg = api.T(k === "h" ? "读数不对，再看看套筒和微分筒的刻度。" : "读数不对，再看看刻度（放大镜可以移动）。",
                         k === "h" ? "Not quite. Look again at the sleeve and thimble." : "Not quite. Look again (move the magnifier).");
    }
    check15(api);
  },
  change(api, s, pid) { if (pid === "Uhat") check15(api); },
  readouts(api, s) {
    const f = api.fmt, k = key15(api.scene), list = rec15[k];
    const rows = [[["我的读数", "My reading"], f(mine15(api), api.scene === "micro" ? 3 : 2) + " mm"],
                  [["位置", "Place"], `${rec15.i[k] + 1} / ${POS15[k].length}`],
                  [["已记录", "Recorded"], String(list.length) + (list.length ? "：" + list.slice(-4).map((x) => x.toFixed(api.scene === "micro" ? 3 : 2)).join(", ") : "")]];
    if (s.msg) rows.push([["提示", "Note"], s.msg]);
    return rows;
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, ctx = api.ctx;
    const t = truth15(api.scene);
    if (api.scene === "micro") { drawMicro15(api, t); return; }
    // ---- 上：整把卡尺（每毫米 sc 像素）
    const x0 = w * 0.05, sc = (w * 0.9) / 150, yb = h * 0.18;
    api.rect(x0 - 20, yb, w * 0.9 + 30, 22, css("--panel"), css("--ink"));
    for (let m = 0; m <= 150; m++) { const x = x0 + m * sc, L = m % 10 === 0 ? 12 : m % 5 === 0 ? 8 : 5; api.line(x, yb, x, yb + L, css("--ink"), 1); if (m % 10 === 0) api.label(String(m / 10), x, yb + 21, css("--muted"), 10, "center"); }
    api.rect(x0 - 20, yb, 20, 70, css("--muted"));                                   // 固定量爪
    const xv = x0 + t * sc;
    api.rect(xv, yb + 22, 49 * sc, 16, css("--soft"), css("--ink"));                // 游标
    api.rect(xv, yb, 14, 70, css("--muted"));                                       // 活动量爪
    const isCoin = api.scene === "coin";
    api.rect(x0, yb + 40, t * sc, 26, isCoin ? css("--amber") : "#b8c4cc", css("--ink"));   // 被测件
    api.label(api.T(isCoin ? "硬币" : "转接盘", isCoin ? "coin" : "plate"), x0 + t * sc / 2, yb + 58, css("--ink"), 12, "center");
    // 放大镜框
    const look = api.p.look, cx = xv + look * 0.98 * sc;
    api.ctx.strokeStyle = css("--red"); api.ctx.lineWidth = 1.5; api.ctx.strokeRect(cx - 2.1 * sc, yb - 4, 4.2 * sc, 46);
    // ---- 下：放大镜中的刻度（每毫米 Z 像素）
    const Z = 150, top = h * 0.5, mid = w / 2, c0 = t + look * 0.98;            // 放大镜中心对应的主尺位置
    api.rect(w * 0.04, top - 10, w * 0.92, h * 0.42, css("--panel"), css("--line"));
    api.label(api.T("放大镜", "magnifier"), w * 0.05, top + 6, css("--muted"), 11);
    const X = (pos) => mid + (pos - c0) * Z;
    for (let m = Math.floor(c0 - 3); m <= Math.ceil(c0 + 3); m++) {
      const x = X(m); if (x < w * 0.05 || x > w * 0.95) continue;
      const L = m % 10 === 0 ? 46 : m % 5 === 0 ? 36 : 26;
      api.line(x, top + 70 - L, x, top + 70, css("--ink"), 2);
      api.label(String(m), x, top + 70 - L - 6, css("--ink"), 13, "center");
    }
    api.line(w * 0.05, top + 70, w * 0.95, top + 70, css("--ink"), 1);
    for (let k = 0; k <= 50; k++) {
      const x = X(t + k * 0.98); if (x < w * 0.05 || x > w * 0.95) continue;
      const L = k % 5 === 0 ? 30 : 20;
      api.line(x, top + 72, x, top + 72 + L, css("--blue"), 2);
      api.label(String(k), x, top + 72 + L + 14, css("--blue"), k % 5 === 0 ? 13 : 10, "center");
    }
    api.label(api.T("主尺（mm）", "main scale (mm)"), w * 0.8, top + 6, css("--muted"), 11);
    api.label(api.T("游标（数字为格数，每格 0.02 mm）", "vernier (numbers count lines, 0.02 mm each)"), w * 0.06, top + 128, css("--blue"), 11);
  },
});

function drawMicro15(api, t) {
  const { w, h } = api, css = api.css;
  const sleeveEnd = Math.floor(t / 0.5) * 0.5, frac = (t - sleeveEnd) / 0.01;          // 微分筒上的格数（0–50）
  const Z = 70, x0 = w * 0.08, yref = h * 0.5, edge = x0 + t * Z * 0 + (w * 0.55);      // 套筒在左，微分筒边缘固定在画面中部
  const X = (mm) => edge - (t - mm) * Z;
  api.rect(x0, yref - 30, edge - x0, 60, css("--soft"), css("--ink"));
  api.line(x0, yref, edge, yref, css("--ink"), 2);                                     // 基准线
  for (let m = Math.ceil((t - (edge - x0) / Z) * 2) / 2; m <= t + 1e-9; m += 0.5) {
    const x = X(m); if (x < x0) continue;
    const whole = Math.abs(m - Math.round(m)) < 1e-9;
    api.line(x, yref, x, yref + (whole ? -16 : 14), css("--ink"), 2);
    if (whole && Math.round(m) % 5 === 0) api.label(String(Math.round(m)), x, yref - 22, css("--ink"), 13, "center");
  }
  api.label(api.T("套筒：上方每格 1 mm，下方是半毫米线", "sleeve: 1 mm above the line, half-mm marks below"), x0, yref + 52, css("--muted"), 11);
  // 微分筒
  api.rect(edge, yref - 120, 90, 240, css("--panel"), css("--ink"));
  const sp = 22;                                                                       // 一格的像素
  for (let j = Math.floor(frac) - 6; j <= Math.ceil(frac) + 6; j++) {
    const y = yref - (j - frac) * sp; if (y < yref - 116 || y > yref + 116) continue;
    const jj = ((j % 50) + 50) % 50;
    api.line(edge, y, edge + (jj % 5 === 0 ? 34 : 20), y, css("--blue"), 2);
    if (jj % 5 === 0) api.label(String(jj), edge + 40, y + 5, css("--blue"), 13);
  }
  api.label(api.T("微分筒：每格 0.01 mm", "thimble: 0.01 mm per mark"), edge + 100, yref - 100, css("--blue"), 11);
  api.label(api.T("（转一圈 0.5 mm）", "(0.5 mm per turn)"), edge + 100, yref - 84, css("--muted"), 11);
}

function check15(api) {
  if (rec15.D.length >= 10 && Math.abs(api.p.Uhat - U15()) <= 0.0035) api.done("U");
}
