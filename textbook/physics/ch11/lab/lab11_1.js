// 实验 11.1 四足机器人跳下台阶：落地冲击与腿部缓冲（配 11.1 节）。
// 腿的场景：Go2（按 15 kg 计）从高 h 的台阶上落下，腿的控制器让腿表现为弹簧—阻尼器：F = kx + cẋ（x 为身体下降量，阻尼比 0.3），
// 脚离地（x < 0）时力为零；腿的最大行程 120 mm，超过就“到底”。画地面力（以体重计）和身体下降量随时间的变化。
// 测力台场景（测量型）：机器人从台上“跳”下，起跳时有一个向上的速度（学生不知道），测力台给出从落地到身体停止下降的冲量 ∫F dt 和时间 Δt；
// 学生由动量定理求落地前的速度。生活场景：人从 0.8 m 高处跳下，屈膝缓冲距离 d，按恒力估算地面力 F = mg(1 + h/d)。
const g111 = 9.81, M111 = 15, W111 = M111 * g111, TRAVEL111 = 0.12, ZETA111 = 0.3, UP111 = 0.8, KPLATE111 = 5000, HPLATE111 = 0.25;
function land111(k, h, up = 0, T = 0.6, dt = 2e-5) {                       // 返回采样点 [t, F/W, x] 和统计量
  const c = 2 * ZETA111 * Math.sqrt(k * M111);
  let x = 0, v = Math.sqrt(up * up + 2 * g111 * h), t = 0, J = 0, tStop = null, Fm = 0, xm = 0;
  const v0 = v, pts = [[0, 0, 0]];
  let n = 0;
  while (t < T) {
    let F = x > 0 ? Math.max(0, k * x + c * v) : 0;
    if (x > TRAVEL111) F = Math.max(F, k * x + c * v + 2e6 * (x - TRAVEL111));   // 到底：机械限位，非常硬
    v += (g111 - F / M111) * dt; x += v * dt; t += dt;
    if (tStop === null) { J += F * dt; if (v <= 0) tStop = t; }
    Fm = Math.max(Fm, F); xm = Math.max(xm, x);
    if (++n % 50 === 0) pts.push([t, F / W111, x]);
  }
  return { pts, Fm: Fm / W111, xm, J, tStop, v0 };
}
let PLATE111 = null;                                                         // 测力台已经测过一次（调滑块后读数仍在）
const person111 = (d) => 1 + 0.8 / d;                                        // 人：F/W = 1 + h/d

WQ.lab({
  title: ["实验 11.1 四足机器人跳下台阶：落地冲击与腿部缓冲", "Lab 11.1 A quadruped jumping down a step: landing impact and leg cushioning"],
  goal: ["看腿的软硬怎样改变落地时的地面力和身体下降量，找出既不超力、又不“到底”的腿部刚度；由测力台的冲量求落地速度，验证动量定理。",
         "See how leg stiffness changes the landing force and how far the body sinks, find a stiffness that neither overloads nor bottoms out, and use a force plate's impulse to get the landing speed, checking the impulse–momentum theorem."],
  scenes: [
    { id: "legs", robot: true, name: ["腿的软硬", "Leg stiffness"], hide: ["vhat", "d"],
      problem: { title: ["机器人问题：腿要调多软？", "Robot problem: how soft should the legs be?"],
                 text: ["Go2 从台阶上跳下，腿的电机让每条腿像一根弹簧加一个阻尼器。腿太硬，落地冲击大，关节减速器受不了；腿太软，身体下沉太多，腿会“到底”（超过 120 mm 的行程）。调台阶高度和腿的刚度 k，点“开始”。",
                        "Go2 jumps down a step; its motors make each leg act like a spring and a damper. Too stiff and the impact overloads the joint gearboxes; too soft and the body sinks so far the legs bottom out (beyond 120 mm of travel). Set the step height and leg stiffness k and press “Start”."] } },
    { id: "plate", robot: true, name: ["测力台", "Force plate"], hide: ["h", "k", "d"],
      problem: { title: ["机器人问题：落地前一瞬间有多快？", "Robot problem: how fast was it just before touchdown?"],
                 text: ["Go2 从 0.25 m 高的台子上跳下，起跳时还有一个向上的速度，所以落地速度不能只用高度算。测力台记下了地面力。读出从落地到身体停止下降的冲量 ∫F dt 和时间 Δt，用动量定理求落地前的速度，调到“你算的落地速度”，提交。",
                        "Go2 jumps off a 0.25 m platform with some upward speed at take-off, so the height alone does not give the landing speed. A force plate records the ground force. Read the impulse ∫F dt and the time Δt from touchdown until the body stops sinking, get the landing speed from the impulse–momentum theorem, set “Your landing speed” and submit."] } },
    { id: "life", name: ["人跳下", "A person jumping down"], hide: ["h", "k", "vhat"],
      problem: { title: ["生活中的例子：从 0.8 m 高处跳下要屈膝多少", "Everyday example: how far to bend the knees jumping down 0.8 m"],
                 text: ["人从 0.8 m 高处跳下，落地后屈膝下蹲距离 d 停下。设下蹲时地面力不变，它是体重的多少倍？调 d，点“开始”。",
                        "A person jumps down 0.8 m and stops by bending the knees through a distance d. Taking the ground force as constant while crouching, how many body weights is it? Set d and press “Start”."] } },
  ],
  params: [
    { id: "h", name: ["台阶高度 h", "Step height h"], min: 0.1, max: 0.6, step: 0.05, value: 0.3, unit: "m", digits: 2 },
    { id: "k", name: ["腿的刚度 k", "Leg stiffness k"], min: 1000, max: 30000, step: 500, value: 20000, unit: "N/m", digits: 0 },
    { id: "vhat", name: ["你算的落地速度", "Your landing speed"], min: 0, max: 4, step: 0.01, value: 0, unit: "m/s", digits: 2 },
    { id: "d", name: ["屈膝下蹲距离 d", "Knee-bend distance d"], min: 0.02, max: 0.5, step: 0.01, value: 0.05, unit: "m", digits: 2 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--red)", name: ["地面力 / 体重", "ground force / body weight"] }, { color: "var(--blue)", name: ["身体下降量", "body drop"] }],
  tasks: [
    { id: "k", robot: true, text: ["腿的软硬：h = 0.30 m，调 k，使地面力峰值不超过体重的 4.5 倍、身体下降不超过 120 mm，运行后提交。", "Leg stiffness: with h = 0.30 m choose k so the peak force is at most 4.5 body weights and the body sinks at most 120 mm; run, then submit."],
      demo: { scene: "legs", set: { h: 0.3, k: 5000 }, press: ["start", "submit"], wait: 2 } },
    { id: "v0", robot: true, text: ["测力台：由冲量和时间求落地前的速度，提交（相差 0.05 m/s 以内）。比较只按 0.25 m 高度算出的速度。", "Force plate: from the impulse and the time find the landing speed and submit (within 0.05 m/s). Compare with the speed from the 0.25 m height alone."],
      demo: { scene: "plate", set: { vhat: 2.35 }, press: ["start", "submit"], wait: 2 } },
    { id: "d", text: ["人跳下：找出地面力不超过体重 5 倍所需的最小下蹲距离（按 0.01 m 一档），运行后提交。", "Person: find the smallest crouch distance (in 0.01 m steps) that keeps the ground force at most 5 body weights; run, then submit."],
      demo: { scene: "life", set: { d: 0.2 }, press: ["start", "submit"], wait: 1 } },
  ],
  think: ["为什么腿太硬、太软都不行？阻尼比加大，峰值力和下降量各怎样变？测力台上，为什么冲量 ∫F dt 比 mv₀ 大，多出来的是什么？",
          "Why are both too-stiff and too-soft legs bad? With more damping, how do the peak force and the sinking change? On the force plate, why is ∫F dt larger than mv₀, and what is the extra?"],

  reset(api, s) { s.msg = s.msg || ""; s.ran = false; s.r = null; s.shown = 0; },
  start(api, s) {
    s.ran = true; const p = api.p;
    if (api.scene === "legs") s.r = land111(p.k, p.h);
    if (api.scene === "plate") s.r = land111(KPLATE111, HPLATE111, UP111);
  },
  change(api, s) { s.ran = false; },
  update(dt, api, s) {
    if (api.scene === "life") { if (api.t > 1) api.stop(); return; }
    s.shown = api.t / 2;                                                   // 动画放慢 1/2：0.6 s 的过程放 1.2 s
    if (s.shown >= 0.6) { s.shown = 0.6; if (api.scene === "plate") PLATE111 = s.r; api.stop(); }
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "legs" && s.ran && Math.abs(p.h - 0.3) < 1e-9 && s.r.Fm <= 4.5 && s.r.xm <= TRAVEL111) { api.done("k"); ok = true; }
    const pr = s.ran ? s.r : PLATE111;
    if (api.scene === "plate" && pr && Math.abs(p.vhat - pr.v0) <= 0.05) { api.done("v0"); ok = true; }
    if (api.scene === "life" && s.ran && person111(p.d) <= 5 + 1e-9 && person111(p.d - 0.01) > 5 + 1e-9) { api.done("d"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "life") return [[["下蹲距离 d", "Crouch d"], f(p.d, 2) + " m"], [["地面力 / 体重", "Ground force / body weight"], s.ran ? f(person111(p.d), 2) : "—"], sub];
    const r = s.ran && s.r && s.shown >= 0.6 ? s.r : api.scene === "plate" && !s.ran ? PLATE111 : null;
    if (api.scene === "plate")
      return [[["冲量 ∫F dt（落地到停止下降）", "Impulse ∫F dt (touchdown to lowest point)"], r ? f(r.J, 2) + " N·s" : "—"],
        [["时间 Δt", "Time Δt"], r ? f(r.tStop * 1000, 1) + " ms" : "—"], [["机器人质量", "Robot mass"], "15 kg"], sub];
    return [[["地面力峰值 / 体重", "Peak force / body weight"], r ? f(r.Fm, 2) : "—"], [["身体最大下降量", "Largest body drop"], r ? f(r.xm * 1000, 0) + " mm" : "—"],
      [["腿", "Legs"], r ? (r.xm > TRAVEL111 ? api.T("到底了！", "bottomed out!") : api.T("没有到底", "within travel")) : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mut = css("--muted"), red = css("--red"), blue = css("--blue");
    if (api.scene === "life") {
      const F = person111(p.d), bx = w * 0.3, gy = h * 0.8;
      api.line(w * 0.1, gy, w * 0.9, gy, ink, 2);
      api.rect(bx - 20, gy - 170 + (s.ran ? p.d * 200 : 0), 40, 120 - (s.ran ? p.d * 200 : 0), css("--amber"), ink, 6);
      api.circle(bx, gy - 190 + (s.ran ? p.d * 200 : 0), 18, css("--amber"), ink);
      if (s.ran) { api.arrow(bx + 60, gy, bx + 60, gy - Math.min(220, 30 * F), red, 3); api.label(api.T(`${api.fmt(F, 1)} 倍体重`, `${api.fmt(F, 1)} × body weight`), bx + 80, gy - 30 * Math.min(F, 7), red, 14); }
      return;
    }
    const r = s.r, upto = s.shown;
    // 左：机器人示意
    const gx = w * 0.16, gy = h * 0.8, drop = r ? (r.pts.find((q) => q[0] >= upto) || r.pts[r.pts.length - 1])[2] : 0;
    api.line(w * 0.03, gy, w * 0.3, gy, ink, 2);
    if (api.scene === "plate") api.rect(gx - 60, gy - 6, 120, 6, blue);
    const by = gy - 90 + Math.max(0, drop) * 400;
    api.rect(gx - 50, by - 24, 100, 24, css("--accent"), ink, 5);
    [-35, 35].forEach((dx) => { api.line(gx + dx, by, gx + dx - 12, (by + gy) / 2, ink, 3); api.line(gx + dx - 12, (by + gy) / 2, gx + dx, gy, ink, 3); });
    // 右：曲线
    const G = api.graph({ x: w * 0.38, y: h * 0.1, w: w * 0.58, h: h * 0.72, xmin: 0, xmax: 0.6, ymin: 0, ymax: 10,
      xlabel: "t / s", ylabel: api.T("红：地面力 / 体重　蓝：下降量 / (20 mm)", "red: force / weight　blue: drop / (20 mm)") }).axes();
    G.hline(4.5, red); G.hline(TRAVEL111 / 0.02, blue);
    if (r) {
      const q = r.pts.filter((a) => a[0] <= upto);
      G.pts(q.map((a) => [a[0], Math.min(10, a[1])]), red, 2); G.pts(q.map((a) => [a[0], Math.max(0, a[2]) / 0.02]), blue, 2);
    }
  },
});
