// 实验 8.6 物理引擎的步长（配 8.5、8.6 节）。
// 落地场景：网球（58 g）从 1.0 m 落到地面。接触方式 0 为罚函数（地面劲度 k，阻尼使恢复系数约 0.75，只推不拉），
// 1 为冲量法（穿入地面就放回地面、法向速度乘 −0.75）；积分用半隐式欧拉法。“测量”栏给出第一次反弹的高度与参考值
// （罚函数、0.1 ms 步长）之比。任务 1、2：找出反弹高度与参考值相差不超过 10%、且所有更小的步长也都满足的最大步长
// （0.1 ms 一档）：k = 30 kN/m 时为 0.5 ms（一次接触约 9 步），k = 300 kN/m 时为 0.1 ms。ωh < 2 只是必要条件：
// 接触只有一两步时，即使在这个界限以内，反弹也可能高出好几倍（接触力时有时无，又有阻尼，线性稳定性分析不够用）。
// 穿墙场景：半径 2 cm 的小球以速度 v 飞向 10 cm 厚的墙，引擎只在每一步的位置检查是否碰到墙。保证不穿墙（无论从哪里出发）
// 要求一步走过的距离不超过墙厚加球的直径：vh ≤ 0.14 m。任务 3：v = 60 m/s 时满足这一条件的最大步长（1 ms 一档）为 2 ms。
// 任务 4：开启连续碰撞检测（检查每一步扫过的整段路径），在 33 ms、100 m/s 下挡住小球。
const g86 = 9.81, M86 = 0.058, E86 = 0.75, WALL86 = 5.0, THK86 = 0.10, R86 = 0.02;
function bounce86(h, k, contact, keep) {                                 // 返回第一次反弹的最高点与轨迹（3 s 内）
  const z = -Math.log(E86) / Math.sqrt(Math.PI ** 2 + Math.log(E86) ** 2), c = 2 * z * Math.sqrt(k * M86);
  let y = 1, v = 0, t = 0, rising = false, top = NaN, minY = 0;
  const pts = keep ? [[0, 1]] : null;
  while (t < 3) {
    if (contact === 0) { const F = -M86 * g86 + (y < 0 ? Math.max(0, -k * y - c * v) : 0); v += h * F / M86; y += h * v; }
    else { v -= g86 * h; y += h * v; if (y < 0) { y = 1e-9; v = -E86 * v; } }
    t += h; minY = Math.min(minY, y);
    if (keep && pts.length < 40000) pts.push([t, y]);
    if (!rising && v > 0 && t > 0.3) rising = true;
    if (rising && v <= 0 && isNaN(top)) { top = y; if (!keep) break; }
    if (y > 1e4) { if (isNaN(top)) top = Infinity; break; }
  }
  return { top, pts, minY };
}
const REF86 = {}, REFP86 = {}, B86 = {};
const bcache86 = (h, k, contact) => { const key = `${h}|${k}|${contact}`; if (!(key in B86)) B86[key] = bounce86(h, k, contact, true); return B86[key]; };
const ref86 = (k) => (REF86[k] = REF86[k] || bounce86(1e-4, k, 0, false).top);
function good86(hms, k) { return Math.abs(bounce86(hms / 1000, k, 0, false).top / ref86(k) - 1) <= 0.10; }
function maxgood86(k) { let i = 1; while (i < 200 && good86(i / 10, k)) i++; return (i - 1) / 10; }   // 0.1 ms 一档，从小往大第一次不满足之前
function tunnel86(v, h, ccd) {                                          // 返回每一步的位置，以及是否被墙挡住
  const xs = []; let x = 0;
  for (let n = 0; n < 20000 && x < 9; n++) {
    const nx = x + v * h;
    const hitNow = nx + R86 >= WALL86 && nx - R86 <= WALL86 + THK86;
    const swept = ccd && x + R86 < WALL86 && nx - R86 > WALL86 + THK86;
    xs.push(x);
    if (hitNow || swept || (ccd && nx + R86 >= WALL86 && x - R86 <= WALL86 + THK86)) { xs.push(Math.min(nx, WALL86 - R86)); return { xs, blocked: true }; }
    x = nx;
  }
  xs.push(x);
  return { xs, blocked: false };
}

WQ.lab({
  title: ["实验 8.6 物理引擎的步长", "Lab 8.6 Time steps in a physics engine"],
  goal: ["看步长怎样影响物理引擎里的接触：罚函数接触何时“弹飞”，冲量法为什么稳定；快速小球何时穿墙，连续碰撞检测怎样解决。",
         "See how the time step affects contact in a physics engine: when penalty contact launches the ball, why impulses stay stable, when a fast ball tunnels through a wall, and how continuous collision detection fixes it."],
  scenes: [
    { id: "drop", robot: true, name: ["网球落地", "A ball hits the floor"], hide: ["v", "h2", "ccd"],
      problem: { title: ["机器人问题：仿真步长取多大才可信？", "Robot problem: how large a step can you trust?"],
                 text: ["在机器人仿真中，地面常用一个很硬的弹簧表示（罚函数）。选接触方式、地面劲度 k 和步长 h，点“开始”，看网球从 1.0 m 落下后的运动。灰线是步长 0.1 ms 的参考结果。ωh < 2（ω = √(k/m)）只是必要条件，看看步长多大时结果还可信。",
                        "Robot simulators often model the floor as a very stiff spring (penalty contact). Choose the contact model, floor stiffness k and step h, press “Start” and watch the ball dropped from 1.0 m. The grey line is the 0.1 ms reference. ωh < 2 (ω = √(k/m)) is only a necessary condition; find how large a step still gives trustworthy results."] } },
    { id: "wall", name: ["游戏里的穿墙", "Tunnelling in a game"], hide: ["contact", "hms", "k"],
      problem: { title: ["生活中的例子：子弹为什么会穿墙", "Everyday example: why bullets pass through walls"],
                 text: ["半径 2 cm 的小球以速度 v 飞向 10 cm 厚的墙。引擎只在每一步的位置检查是否碰到墙。调速度和步长，点“开始”；再试试开启连续碰撞检测。",
                        "A ball of radius 2 cm flies at speed v towards a 10 cm wall. The engine only checks for contact at the position after each step. Adjust speed and step and press “Start”; then try continuous collision detection."] } },
  ],
  params: [
    { id: "contact", name: ["接触：0 罚函数，1 冲量法", "Contact: 0 penalty, 1 impulse"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "k", name: ["地面劲度 k", "Floor stiffness k"], min: 10, max: 300, step: 10, value: 30, unit: "kN/m", digits: 0 },
    { id: "hms", name: ["步长 h", "Step h"], min: 0.1, max: 20, step: 0.1, value: 5, unit: "ms", digits: 1 },
    { id: "v", name: ["小球速度 v", "Ball speed v"], min: 10, max: 100, step: 5, value: 30, unit: "m/s", digits: 0 },
    { id: "h2", name: ["步长 h", "Step h"], min: 1, max: 33, step: 1, value: 17, unit: "ms", digits: 0 },
    { id: "ccd", name: ["连续碰撞检测：0 关，1 开", "Continuous collision detection: 0 off, 1 on"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--red)", name: ["仿真", "simulation"] }, { color: "var(--muted)", name: ["参考（0.1 ms）", "reference (0.1 ms)"] }],
  tasks: [
    { id: "s30", robot: true, text: ["网球落地：罚函数，k = 30 kN/m。从 0.1 ms 起每次加 0.1 ms，找出反弹高度与参考值相差不超过 10% 的最大步长（比它小的步长也都要满足），提交。一次接触有几步？", "Floor: penalty, k = 30 kN/m. Raise the step from 0.1 ms in 0.1 ms increments and find the largest step whose bounce is within 10% of the reference (all smaller steps must pass too); submit. How many steps does one contact span?"],
      demo: { scene: "drop", set: { contact: 0, k: 30, hms: 0.5 }, press: ["start", "submit"], wait: 2 } },
    { id: "s300", robot: true, text: ["网球落地：地面劲度增大到 k = 300 kN/m，同样的要求下最大步长是多少？与 k = 30 kN/m 相比缩小了多少倍，与 √(m/k) 的变化相符吗？", "Floor: with k = 300 kN/m, what is the largest step under the same rule? By what factor did it shrink, and does that match √(m/k)?"],
      demo: { scene: "drop", set: { contact: 0, k: 300, hms: 0.1 }, press: ["start", "submit"], wait: 2 } },
    { id: "tun", text: ["穿墙：v = 60 m/s，不开连续碰撞检测。保证无论从哪里出发都不穿墙的最大步长是多少（1 ms 一档）？调到这个值，提交。", "Wall: v = 60 m/s, no continuous detection. What is the largest step (1 ms steps) that guarantees no tunnelling wherever the ball starts? Set it and submit."],
      demo: { scene: "wall", set: { v: 60, ccd: 0, h2: 2 }, press: ["start", "submit"], wait: 2 } },
    { id: "ccd", text: ["穿墙：开启连续碰撞检测，在步长 33 ms、速度 100 m/s 下挡住小球，提交。", "Wall: turn on continuous detection and stop the ball at a 33 ms step and 100 m/s; submit."],
      demo: { scene: "wall", set: { v: 100, ccd: 1, h2: 33 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["ωh < 2 以内的步长，罚函数的反弹为什么仍可能差好几倍？冲量法在 1/60 s 的步长下为什么不会弹飞，它又丢掉了什么？游戏为什么对子弹用射线检测，而不是减小步长？",
          "Why can the penalty bounce be off by several times even with ωh < 2? Why does the impulse method not launch the ball at 1/60 s, and what does it give up? Why do games use ray casts for bullets instead of smaller steps?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; },
  change(api, s) { s.msg = ""; },
  start(api, s) { s.ran = true; },
  update(dt, api, s) { if (api.t > 3) api.stop(); },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    const near = (a, b) => Math.abs(a - b) < 1e-6;
    if (api.scene === "drop" && p.contact === 0 && s.ran) {
      const right = Math.abs(p.hms - maxgood86(p.k * 1000)) < 1e-6;
      if (right && near(p.k, 30)) { api.done("s30"); ok = true; }
      if (right && near(p.k, 300)) { api.done("s300"); ok = true; }
    }
    if (api.scene === "wall" && s.ran) {
      if (p.ccd === 0 && near(p.v, 60) && p.v * p.h2 / 1000 <= THK86 + 2 * R86 && p.v * (p.h2 + 1) / 1000 > THK86 + 2 * R86) { api.done("tun"); ok = true; }
      if (p.ccd === 1 && near(p.v, 100) && near(p.h2, 33) && tunnel86(p.v, p.h2 / 1000, 1).blocked) { api.done("ccd"); ok = true; }
    }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "drop") {
      const k = p.k * 1000, w = Math.sqrt(k / M86), B = bcache86(p.hms / 1000, k, p.contact), r = B.top / ref86(k);
      return [[["ωh（罚函数）", "ωh (penalty)"], f(w * p.hms / 1000, 2)],
        [["第一次反弹高度 / 参考值", "First bounce / reference"], !s.ran ? "—" : isFinite(r) ? f(r, 2) : api.T("弹飞了", "launched")], sub];
    }
    const T = tunnel86(p.v, p.h2 / 1000, p.ccd);
    return [[["每步走过的距离", "Distance per step"], f(p.v * p.h2, 0) + " mm"], [["结果", "Result"], !s.ran ? "—" : T.blocked ? api.T("被墙挡住", "stopped by the wall") : api.T("穿墙而过", "passed through")], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), red = css("--red"), mut = css("--muted");
    if (api.scene === "drop") {
      const k = p.k * 1000, G = api.graph({ x: 60, y: 24, w: w - 90, h: h - 70, xmin: 0, xmax: 3, ymin: -0.1, ymax: 1.6, xlabel: "t / s", ylabel: api.T("高度 / m", "height / m") }).axes();
      REFP86[k] = REFP86[k] || bounce86(1e-4, k, 0, true).pts.filter((q, i) => i % 20 === 0);   // 参考曲线只算一次
      G.pts(REFP86[k], mut, 3);
      if (s.ran) {
        const P = bcache86(p.hms / 1000, k, p.contact).pts.filter((q) => q[0] <= Math.max(0.01, api.t));
        G.pts(P.map((q) => [q[0], Math.max(-0.1, Math.min(1.6, q[1]))]), red, 2);
      }
      G.hline(0, ink, []);
      return;
    }
    const sc = (w - 80) / 9, y0 = h * 0.5, X = (x) => 40 + x * sc;
    api.rect(X(WALL86), y0 - 70, THK86 * sc, 140, css("--panel"), ink, 2);
    api.label(api.T("墙 10 cm", "wall 10 cm"), X(WALL86) - 20, y0 - 80, mut, 12);
    if (s.ran) {
      const T = tunnel86(p.v, p.h2 / 1000, p.ccd), n = Math.min(T.xs.length, 1 + Math.floor(api.t * 30));
      for (let i = 0; i < n; i++) api.circle(X(T.xs[i]), y0, Math.max(3, R86 * sc), i === n - 1 ? red : "rgba(192,57,43,0.25)", null);
    }
    api.label(api.T("圆点：每一步结束时小球的位置（引擎只在这些位置检查碰撞）", "dots: the ball after each step (the only places checked for contact)"), 12, 20, mut, 12);
  },
});
