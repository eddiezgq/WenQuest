// 实验 52.3 夹紧力与切削力的平衡（配 52.3、52.4 节）。
// 键槽：切削力随每齿进给量按 fz^(1−mc) 变化（基准值由程序 ex52_3 按逐齿积分算出、并核对本文件的常数），
// 需要的夹紧力取四个条件的最大值（不被抬起、不滑出 V 形块、不绕轴线转动、背离挡板的轴向分力不打滑）；
// 两个移动压板，M10 螺柱，定扭矩扳手：W = M/(r2·tan(λ + φ′) + r′·μ)，再乘杠杆比。
// 斜楔：W = Q/(tan φ + tan(α + φ))，自锁 α ≤ 2φ；圆偏心：自锁 2e/D ≤ μ。
const C52 = { FZ0: 0.03, MC: 0.14, FY0: 115.7, FZL0: 28.0, FXB0: 43.1, G: 20, RATIO: 0.528, COUNT: 2, D2: 9.026, LEAD: 1.5, R_END: 6.75,
              RF: 20.15, RC: 16.3, RV: 20.15, Z_STRAP: 686, SIG_ALLOW: 300 };

function eval52(api) {
  const p = api.p, sc = api.scene, mu = p.mu, phi = Math.atan(mu);
  if (sc === "keyway") {
    const s = Math.pow(p.fz / C52.FZ0, 1 - C52.MC);
    const Fy = C52.FY0 * s, Fz = C52.FZL0 * s, Fxb = C52.FXB0 * s, K = p.K, h = Math.PI / 4;
    const fr = mu + mu / Math.sin(h), frm = mu * C52.RC + mu * C52.RV / Math.sin(h);
    const req = {
      lift: K * Fz - C52.G,
      slide: K * Fy * Math.tan(h) - C52.G,
      rotate: (K * Fy * C52.RF - mu * C52.G * C52.RV / Math.sin(h)) / frm,
      axial: (K * Fxb - mu * C52.G / Math.sin(h)) / fr,
    };
    let gov = "lift";
    for (const k in req) { req[k] = Math.max(0, req[k]); if (req[k] > req[gov]) gov = k; }
    const lam = Math.atan(C52.LEAD / (Math.PI * C52.D2)), phe = Math.atan(mu / Math.cos(Math.PI / 6));
    const Ws = p.M * 1000 / (C52.D2 / 2 * Math.tan(lam + phe) + C52.R_END * mu);   // 每个螺柱的轴向力
    const have = Ws * C52.RATIO * C52.COUNT;
    const sigma = Ws * (50 / 90) * 40 / C52.Z_STRAP;                                // 压板螺栓孔处的弯曲应力
    return { sc, Fy, Fz, Fxb, req, gov, need: req[gov], have, Ws, sigma, ok: have >= req[gov], strong: sigma <= C52.SIG_ALLOW };
  }
  if (sc === "wedge") {
    const a = p.alpha * Math.PI / 180;
    const W = p.Q / (Math.tan(phi) + Math.tan(a + phi));
    return { sc, W, i: W / p.Q, lock: a <= 2 * phi + 1e-12, limit: 2 * phi * 180 / Math.PI, ideal: p.Q / Math.tan(a) };
  }
  // 圆偏心（γ = 90°，升角最大的位置）
  const R = p.D / 2, al = Math.atan(p.e / R), rho = R / Math.cos(al);   // γ = 90° 处的升角（最大升角 asin(e/R) 与它相差很小）
  const W = p.Q * 100 / (rho * Math.tan(al + phi) + (p.D / 8) * mu);
  return { sc, W, lift: al * 180 / Math.PI, lock: 2 * p.e / p.D <= mu + 1e-12, Dmin: 2 / mu, ratio: p.D / p.e };
}

function check52(api, s) {
  const e = eval52(api), p = api.p;
  s.e = e;
  if (e.sc === "keyway" && e.ok && e.strong && p.M <= 3 + 1e-9) api.done("torque");
  if (e.sc === "keyway" && !e.strong) api.done("over");
  if (e.sc === "wedge" && e.lock && p.alpha >= e.limit - 1.0) api.done("wedge");
  if (e.sc === "ecc" && e.lock && e.W >= 1300 && p.e >= 2.5 - 1e-9 && Math.abs(p.Q - 80) < 1e-9 && Math.abs(p.mu - 0.1) < 1e-9) api.done("ecc");
}

WQ.lab({
  title: ["实验 52.3 夹紧力与切削力的平衡", "Lab 52.3 Clamping force against cutting force"],
  goal: ["夹紧力要足够大，使工件在切削力、重力、惯性力作用下不离开定位元件；又不能太大，否则压坏工件、压弯夹具。本实验先算 SH-301 铣键槽需要多大夹紧力、定扭矩扳手拧到多少合适，再看斜楔和圆偏心为什么能自锁、什么时候不能自锁。",
         "The clamping force must keep the work on its locators against cutting forces, weight and inertia, but not so large that it marks the work or bends the fixture. First find how much clamping SH-301's keyway milling needs and what torque to set, then see why wedges and eccentrics self-lock and when they do not."],
  scenes: [
    { id: "keyway", name: ["SH-301 铣键槽：压板", "SH-301 keyway: strap clamps"],
      params: { fz: { value: 0.03 }, mu: { value: 0.16 }, K: { value: 3.4 }, M: { value: 5 } },
      problem: { title: ["工厂问题：压板拧多紧才合适？", "Factory problem: how tight should the straps be?"],
                 text: ["键槽铣夹具 JJ-301-50 用两个移动压板压住轴。操作工习惯用长扳手使劲拧，有一次压板断了。要定一个拧紧扭矩写进工序卡：既保证铣削时工件不动，又不压坏压板。",
                        "Fixture JJ-301-50 holds the shaft with two strap clamps. Operators tend to heave on a long wrench, and once a strap broke. Set a tightening torque for the operation sheet that keeps the work still yet does not overload the strap."] } },
    { id: "wedge", name: ["斜楔", "Wedge"],
      params: { alpha: { value: 6 }, mu: { value: 0.1 }, Q: { value: 100 } },
      problem: { title: ["斜楔为什么松手不退？", "Why does a wedge stay put?"],
                 text: ["气缸推斜楔夹紧工件，气缸卸压后工件仍然夹得住吗？楔角大一点，行程省一些，可还能自锁吗？",
                        "A cylinder drives a wedge to clamp the work. Does it still hold when the cylinder is vented? A larger angle saves stroke — but does it still self-lock?"] } },
    { id: "ecc", name: ["圆偏心", "Eccentric"],
      params: { e: { value: 2 }, D: { value: 40 }, mu: { value: 0.1 }, Q: { value: 80 } },
      problem: { title: ["偏心手柄一扳就夹紧，振动会松吗？", "An eccentric clamps with one flick — will vibration loosen it?"],
                 text: ["偏心夹紧快，适合小批量的钻模。偏心距大，行程大、能适应工件尺寸的变化，可偏心距太大就不能自锁。手柄长 100 mm。",
                        "An eccentric clamps fast and suits small-batch drill jigs. A larger eccentricity gives more stroke and tolerates size variation, but too much and it will not self-lock. Handle length 100 mm."] } },
  ],
  params: [
    { id: "fz", name: ["每齿进给量 fz", "Feed per tooth fz"], min: 0.01, max: 0.1, step: 0.005, value: 0.03, unit: "mm", digits: 3 },
    { id: "mu", name: ["摩擦系数 μ", "Friction coefficient μ"], min: 0.05, max: 0.3, step: 0.01, value: 0.16, unit: "", digits: 2 },
    { id: "K", name: ["安全系数 K", "Safety factor K"], min: 1.5, max: 6, step: 0.1, value: 3.4, unit: "", digits: 1 },
    { id: "M", name: ["拧紧扭矩 M", "Tightening torque M"], min: 0.5, max: 25, step: 0.5, value: 5, unit: "N·m", digits: 1 },
    { id: "alpha", name: ["楔角 α", "Wedge angle α"], min: 2, max: 30, step: 0.5, value: 6, unit: "°", digits: 1 },
    { id: "Q", name: ["原始作用力 Q", "Input force Q"], min: 20, max: 200, step: 5, value: 100, unit: "N", digits: 0 },
    { id: "e", name: ["偏心距 e", "Eccentricity e"], min: 0.5, max: 5, step: 0.1, value: 2, unit: "mm", digits: 1 },
    { id: "D", name: ["偏心轮直径 D", "Eccentric diameter D"], min: 20, max: 80, step: 1, value: 40, unit: "mm", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["计算", "Compute"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  legend: [{ color: "var(--red)", name: ["需要的夹紧力", "required clamping force"] }, { color: "var(--accent)", name: ["机构给出的夹紧力", "force the mechanism gives"] }],
  tasks: [
    { id: "torque", text: ["键槽：μ = 0.16、K = 3.4 时，找出能保证夹紧的最小扭矩；扭矩不超过 3 N·m 时就能满足。", "Keyway: with μ = 0.16 and K = 3.4, find the smallest torque that holds; it should be within 3 N·m."],
      demo: { scene: "keyway", set: { fz: 0.03, mu: 0.16, K: 3.4, M: 2.5 } } },
    { id: "over", text: ["键槽：把扭矩加大到压板的弯曲应力超过许用值 300 MPa（45 钢调质的屈服强度约 355 MPa 除以 1.2），记下这时的扭矩，和工人用长扳手随手拧的 22.5 N·m 比较。", "Keyway: raise the torque until the strap stress passes 300 MPa (about 355 MPa yield of quenched-and-tempered 1045 divided by 1.2); note the torque and compare with the 22.5 N·m an operator applies with a long wrench."],
      demo: { scene: "keyway", set: { M: 22 } } },
    { id: "wedge", text: ["斜楔：μ = 0.1 时，找到仍能自锁的最大楔角（误差 1° 以内）。", "Wedge: with μ = 0.1, find the largest angle that still self-locks (within 1°)."],
      demo: { scene: "wedge", set: { mu: 0.1, alpha: 11 } } },
    { id: "ecc", text: ["圆偏心：μ = 0.1、手力 Q = 80 N 不变，为了适应工件尺寸的变化，偏心距至少 2.5 mm。选 D，使它能自锁、夹紧力不小于 1300 N。", "Eccentric: with μ = 0.1 and Q = 80 N fixed, the eccentricity must be at least 2.5 mm to cope with size variation. Choose D so it self-locks and gives at least 1300 N."],
      demo: { scene: "ecc", set: { mu: 0.1, D: 50, e: 2.5, Q: 80 } } },
  ],
  think: ["斜楔和圆偏心的自锁条件里都没有作用力 Q。为什么自锁只取决于角度和摩擦系数？机床振动时自锁还可靠吗？",
          "Neither the wedge nor the eccentric self-locking condition contains the input force Q. Why does self-locking depend only on angle and friction? Is it still reliable when the machine vibrates?"],

  reset(api, s) { check52(api, s); },
  update(dt, api, s) { check52(api, s); api.stop(); },
  readouts(api, s) {
    const e = s.e || eval52(api), f = api.fmt, T = api.T;
    if (e.sc === "keyway") {
      const g = { lift: T("不被抬起", "no lift-off"), slide: T("不滑出 V 形块", "stays in the V"), rotate: T("不绕轴线转动", "no rotation"), axial: T("轴向不打滑", "no axial slip") }[e.gov];
      return [
        [["横向 / 向上 / 背离挡板的切削力峰值", "Peak lateral / upward / away-from-stop force"], `${f(e.Fy, 0)} / ${f(e.Fz, 0)} / ${f(e.Fxb, 0)} N`],
        [["需要的夹紧力（起控制作用的条件）", "Required clamping force (governing)"], `${f(e.need, 0)} N · ${g}`],
        [["两个压板给出的夹紧力", "Force from both straps"], `${f(e.have, 0)} N · ${e.ok ? T("够", "enough") : T("不够", "not enough")}`],
        [["压板弯曲应力 / 许用 300 MPa", "Strap bending stress / 300 MPa allowed"], `${f(e.sigma, 0)} MPa · ${e.strong ? T("安全", "safe") : T("过载", "overloaded")}`]];
    }
    if (e.sc === "wedge") return [
      [["夹紧力 W / 增力比", "Clamping force W / ratio"], `${f(e.W, 0)} N / ${f(e.i, 2)}`],
      [["无摩擦时的夹紧力", "Frictionless force"], `${f(e.ideal, 0)} N`],
      [["自锁界限 2φ", "Self-locking limit 2φ"], `${f(e.limit, 1)}° · ${e.lock ? T("自锁", "self-locks") : T("不自锁", "does not lock")}`]];
    return [
      [["夹紧力 W（γ = 90°）", "Clamping force W (γ = 90°)"], `${f(e.W, 0)} N`],
      [["最大升角", "Largest lift angle"], `${f(e.lift, 2)}°`],
      [["D/e / 自锁要求 D/e ≥ 2/μ", "D/e / need D/e ≥ 2/μ"], `${f(e.ratio, 1)} / ${f(e.Dmin, 1)} · ${e.lock ? T("自锁", "self-locks") : T("不自锁", "does not lock")}`]];
  },
  draw(api, s) {
    const e = s.e || eval52(api), { w, h } = api, css = api.css, p = api.p, T = api.T;
    if (e.sc === "keyway") {
      const cx = w * 0.27, ap = h * 0.78, R = Math.min(w, h) * 0.16, cy = ap - R / Math.sin(Math.PI / 4);
      api.line(cx - h * 0.4, ap - h * 0.4, cx, ap, css("--ink"), 2); api.line(cx, ap, cx + h * 0.4, ap - h * 0.4, css("--ink"), 2);
      api.circle(cx, cy, R, null, css("--ink"));
      api.rect(cx - R * 0.3, cy - R - 2, R * 0.6, R * 0.25, css("--amber"), null);
      api.arrow(cx, cy - R - 50, cx, cy - R - 4, css("--accent"), 4);
      api.label(T("夹紧力 W", "clamping W"), cx + 8, cy - R - 40, css("--accent"), 12);
      api.arrow(cx - R * 0.3, cy - R + 4, cx - R * 0.3 - 40, cy - R + 4, css("--red"), 3);
      api.label("Fy", cx - R * 0.3 - 56, cy - R + 4, css("--red"), 12);
      api.arrow(cx + R * 0.35, cy - R, cx + R * 0.35, cy - R - 28, css("--warm") || css("--red"), 3);
      api.label("Fz", cx + R * 0.35 + 6, cy - R - 22, css("--red"), 12);
    } else if (e.sc === "wedge") {
      const x0 = w * 0.06, y0 = h * 0.62, L = w * 0.42, a = p.alpha * Math.PI / 180, H = Math.min(L * Math.tan(a), h * 0.4);
      const ctx = api.ctx;
      ctx.beginPath(); ctx.moveTo(x0, y0); ctx.lineTo(x0 + L, y0); ctx.lineTo(x0 + L, y0 - H); ctx.closePath();
      ctx.fillStyle = css("--amber"); ctx.fill();
      api.rect(x0 + L * 0.55, y0 - H - 50, L * 0.35, 50 - 2, null, css("--ink"));
      api.label(T("工件", "work"), x0 + L * 0.72, y0 - H - 25, css("--ink"), 12, "center");
      api.arrow(x0 - 10 + L + 50, y0 - H / 2, x0 + L + 4, y0 - H / 2, css("--accent"), 3);
      api.label("Q", x0 + L + 56, y0 - H / 2 - 12, css("--accent"), 12);
      api.label(`α = ${api.fmt(p.alpha, 1)}°`, x0 + 10, y0 + 18, css("--ink"), 12);
    } else {
      const cx = w * 0.27, cy = h * 0.5, R = Math.min(w, h) * 0.2, k = R / (p.D / 2), ex = p.e * k;
      api.circle(cx + ex, cy, R, null, css("--ink"));
      api.circle(cx, cy, 4, css("--ink"));
      api.circle(cx + ex, cy, 3, css("--red"));
      api.line(cx, cy, cx - R * 1.6, cy - R * 0.9, css("--ink"), 4);
      api.label(T("手柄", "handle"), cx - R * 1.6, cy - R * 0.9 - 14, css("--ink"), 12);
      api.label(`e = ${api.fmt(p.e, 1)}`, cx + ex + 6, cy + 14, css("--red"), 12);
      api.rect(cx - R, cy + R + 6, 2 * R + ex * 2, 16, css("--muted"), null);
    }
    // 右侧：需要与给出（或自锁）的比较条
    const bx = w * 0.6, bw = w * 0.35;
    if (e.sc === "keyway") {
      const top = Math.max(e.need, e.have) * 1.1;
      api.rect(bx, h * 0.35, bw * e.need / top, 20, css("--red"), null, 3);
      api.rect(bx, h * 0.35 + 30, bw * e.have / top, 20, e.ok ? css("--accent") : css("--muted"), null, 3);
      api.label(T("需要", "required"), bx, h * 0.35 - 10, css("--red"), 12);
      api.label(T("给出", "available"), bx, h * 0.35 + 64, css("--accent"), 12);
    } else {
      api.label(e.lock ? T("自锁 ✓", "self-locking ✓") : T("不自锁 ✗", "not self-locking ✗"), bx + bw / 2, h * 0.45, e.lock ? css("--green") : css("--red"), 20, "center");
    }
  },
});
