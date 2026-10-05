// 实验 7.4 车厢里和转台上（配 7.4 节，转台场景也用到 7.5 节）。
// 加速 AGV 场景：三个行程的加速度学生不知道（0.85、1.62、2.35 m/s²），AGV 加速 3 s 后匀速；吊牌按阻尼摆动趋于 tan θ = a/g。
// 视角 0：地面参考系（拉力与重力的合力 ma 使吊牌加速）；视角 1：车厢参考系（拉力、重力、惯性力 −ma 平衡）。由偏角求 a，提交，2% 以内。
// 转台场景：转台以 α = 1.0 rad/s² 从静止加速，零件放在离轴 r 处，μ_s = 0.38（不知道），μ_k = 0.30。
// 需要的静摩擦力 m√((ω²r)² + (rα)²) 超过 μ_s mg 时开始滑动；之后在地面参考系里积分：动摩擦力与相对台面的速度反向。
// 视角 1 画转台上看到的轨迹（向外并弯向后方，科里奥利力）。由开始滑动时的转速求 μ_s，提交，2% 以内。
// 生活场景：汽车 0→100 km/h 匀加速用时 t，杯子直径 8 cm，水面离杯口 1.0 cm；水面倾角 tan θ = a/g，(d/2)tan θ > 1.0 cm 就洒。
const g74 = 9.81, RUN74 = [0.85, 1.62, 2.35], MUS74 = 0.38, MUK74 = 0.30, AL74 = 1.0, RT74 = 0.35;
const spill74 = (t100) => 0.04 * (27.78 / t100) / g74 > 0.010;

WQ.lab({
  title: ["实验 7.4 车厢里和转台上", "Lab 7.4 Inside a vehicle and on a turntable"],
  goal: ["在加速的车厢和转动的转台上观察，加上惯性力，牛顿定律照样能用；与地面上的分析比较。",
         "Watch from an accelerating vehicle and a turning table: add inertial forces and Newton's laws still work; compare with the analysis from the ground."],
  scenes: [
    { id: "agv", robot: true, name: ["加速的 AGV", "An accelerating AGV"], hide: ["r", "muhat", "t100"],
      problem: { title: ["机器人问题：用吊牌测 AGV 的加速度", "Robot problem: measure the AGV's acceleration with a hanging tag"],
                 text: ["AGV 的车厢顶上挂着一个小吊牌。选一个行程，点“开始”，AGV 加速 3 s 后匀速行驶。读出加速时吊牌稳定的偏角，求加速度，调到滑块上，提交。切换视角，比较地面上和车厢里的受力图。",
                        "A small tag hangs from the AGV's roof. Pick a run and press “Start”: the AGV accelerates for 3 s, then cruises. Read the steady angle while accelerating, work out the acceleration, set it and submit. Switch views to compare the force diagrams from the ground and from the vehicle."] } },
    { id: "turn", robot: true, name: ["转台上的零件", "A part on a turntable"], hide: ["run", "ahat", "t100"],
      problem: { title: ["机器人问题：零件在转台上放多远才不会滑出？", "Robot problem: how far out can a part sit on a turntable?"],
                 text: ["分度转台从静止匀加速（α = 1.0 rad/s²），零件放在离轴 r 处。点“开始”，记下零件开始滑动时的转速，求零件与台面之间的 μ_s，提交。切换视角，看地面上和转台上看到的轨迹有什么不同。",
                        "An indexing table speeds up from rest (α = 1.0 rad/s²) with a part at radius r. Press “Start”, note the speed at which the part starts to slide, find μ_s between part and table and submit. Switch views to see how the path looks from the ground and from the table."] } },
    { id: "life", name: ["车里的一杯水", "A cup of water in a car"], hide: ["run", "view", "ahat", "r", "muhat"],
      problem: { title: ["生活中的例子：起步太猛，杯里的水会洒", "Everyday example: a hard start spills your drink"],
                 text: ["杯子放在汽车的杯架上，直径 8 cm，水面离杯口 1.0 cm。汽车由静止匀加速到 100 km/h，用时 t。t 至少多长水才不洒（0.5 s 一档）？先算，再试，提交。",
                        "A cup 8 cm across sits in the car's holder, filled to 1.0 cm below the rim. The car accelerates uniformly from rest to 100 km/h in time t. How long must t be at least for nothing to spill (0.5 s steps)? Work it out, try it, submit."] } },
  ],
  params: [
    { id: "run", name: ["行程", "Run"], min: 1, max: 3, step: 1, value: 1, unit: "", digits: 0 },
    { id: "view", name: ["视角：0 地面上看，1 车厢或转台上看", "View: 0 from the ground, 1 riding along"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "ahat", name: ["你测得的加速度 a", "Your acceleration a"], min: 0, max: 3, step: 0.01, value: 0, unit: "m/s²", digits: 2 },
    { id: "r", name: ["零件离轴 r", "Part radius r"], min: 0.05, max: 0.30, step: 0.01, value: 0.15, unit: "m", digits: 2 },
    { id: "muhat", name: ["你测得的 μ_s", "Your μ_s"], min: 0.1, max: 1, step: 0.005, value: 0.1, unit: "", digits: 3 },
    { id: "t100", name: ["0→100 km/h 的时间 t", "0–100 km/h time t"], min: 4, max: 20, step: 0.5, value: 8, unit: "s", digits: 1 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"] }, { id: "reset", name: ["重置", "Reset"] }, { id: "submit", name: ["提交", "Submit"], primary: true }],
  legend: [{ color: "var(--ink)", name: ["真实的力", "real forces"] }, { color: "var(--orange)", name: ["惯性力（只在车厢、转台上看时画）", "inertial force (riding along only)"] }],
  tasks: [
    { id: "acc", robot: true, text: ["加速的 AGV：选行程 2，由吊牌的偏角求出加速度，提交（2% 以内）。", "AGV: choose run 2, find the acceleration from the tag's angle and submit (within 2%)."],
      demo: { scene: "agv", set: { run: 2, ahat: 1.62 }, press: ["start", "submit"], wait: 2 } },
    { id: "mu", robot: true, text: ["转台：由零件开始滑动时的转速求出 μ_s，提交（2% 以内）。", "Turntable: find μ_s from the speed at which the part starts to slide and submit (within 2%)."],
      demo: { scene: "turn", set: { r: 0.15, muhat: 0.38 }, press: ["start", "submit"], wait: 2 } },
    { id: "cup", text: ["车里的一杯水：找出水不洒的最短加速时间（0.5 s 一档），提交。", "Cup of water: find the shortest time to 100 km/h that does not spill (0.5 s steps) and submit."],
      demo: { scene: "life", set: { t100: 11.5 }, press: ["start", "submit"], wait: 2 } },
  ],
  think: ["在车厢里看，吊牌静止，为什么拉力不竖直？惯性力的反作用力在哪里？转台上看到的零件为什么不是沿半径直线滑出，而是弯向后方？",
          "Seen from inside, the tag is at rest; why is the string not vertical? Where is the reaction to the inertial force? Why does the part on the table not slide straight out along the radius but curve backwards?"],

  reset(api, s) {
    s.x = 0; s.v = 0; s.th = 0; s.om = 0; s.maxdev = 0; s.phi = 0; s.w = 0; s.slip = false; s.wslip = 0; s.P = null; s.V = null; s.trail = []; s.off = false; s.msg = s.msg || ""; s.spill = false;
  },
  change(api, s) { s.msg = ""; },
  update(dt, api, s) {
    const p = api.p, t = api.t;
    if (api.scene === "agv" || api.scene === "life") {
      const a = api.scene === "agv" ? (t < 3 ? RUN74[p.run - 1] : 0) : (s.v < 27.78 ? 27.78 / p.t100 : 0);
      s.v += a * dt; s.x += s.v * dt;
      const target = Math.atan(a / g74);
      const c = api.scene === "agv" ? 4 : 12;                                // 吊牌有阻尼地摆向 tan θ = a/g；水面按临界阻尼处理（不过冲，与稳态判定一致）
      s.om += (30 * (target - s.th) - c * s.om) * dt; s.th += s.om * dt;
      if (api.scene === "life" && 0.04 * Math.tan(Math.abs(target)) > 0.010) s.spill = true;
      if ((api.scene === "agv" && t > 5) || (api.scene === "life" && t > p.t100 + 1.5)) api.stop();
      return;
    }
    // 转台
    s.w = AL74 * t; s.phi = 0.5 * AL74 * t * t;
    if (!s.slip) {
      const need = Math.hypot(s.w * s.w * p.r, p.r * AL74);
      if (need > MUS74 * g74) {
        s.slip = true; s.wslip = s.w;
        s.P = [p.r * Math.cos(s.phi), p.r * Math.sin(s.phi)]; s.V = [-s.w * s.P[1], s.w * s.P[0]];
      }
    } else if (!s.off) {
      for (let k = 0; k < 10; k++) {                                         // 地面参考系：动摩擦力与相对台面的速度反向
        const h = dt / 10, ww = s.w, rx = s.V[0] + ww * s.P[1], ry = s.V[1] - ww * s.P[0], rv = Math.hypot(rx, ry) || 1e-9;
        s.V[0] -= MUK74 * g74 * rx / rv * h; s.V[1] -= MUK74 * g74 * ry / rv * h;
        s.P[0] += s.V[0] * h; s.P[1] += s.V[1] * h;
      }
      if (Math.hypot(s.P[0], s.P[1]) > RT74) s.off = true;
    }
    const pos = s.slip ? s.P : [p.r * Math.cos(s.phi), p.r * Math.sin(s.phi)];
    if (s.trail.length < 3000 && s.slip) s.trail.push([pos[0], pos[1], s.phi]);
    if (t > 15 || (s.off && t > s.wslip / AL74 + 1)) api.stop();
  },
  action(id, api, s) {
    if (id !== "submit") return;
    const p = api.p; let ok = false;
    if (api.scene === "agv" && p.run === 2 && Math.abs(p.ahat - RUN74[1]) <= 0.02 * RUN74[1]) { api.done("acc"); ok = true; }
    if (api.scene === "turn" && Math.abs(p.muhat - MUS74) <= 0.02 * MUS74) { api.done("mu"); ok = true; }
    if (api.scene === "life" && !spill74(p.t100) && spill74(p.t100 - 0.5)) { api.done("cup"); ok = true; }
    s.msg = ok ? api.T("对了", "correct") : api.T("还不满足任务要求", "not yet");
  },
  readouts(api, s) {
    const f = api.fmt, p = api.p, sub = [["提交结果", "Submission"], s.msg || "—"];
    if (api.scene === "agv") return [[["车速", "Speed"], f(s.v, 2) + " m/s"], [["吊牌偏角 θ", "Tag angle θ"], f(s.th * 180 / Math.PI, 1) + "°"], sub];
    if (api.scene === "turn") {
      const rpm = (w) => w * 60 / (2 * Math.PI);
      return [[["转台转速", "Table speed"], f(rpm(s.w), 1) + " r/min"], [["零件", "Part"], s.off ? api.T("滑出台面", "off the table") : s.slip ? api.T("滑动", "sliding") : api.T("随台转动", "turning with the table")],
        [["开始滑动时的转速", "Speed when it began to slide"], s.slip ? f(rpm(s.wslip), 1) + " r/min" : "—"], sub];
    }
    return [[["车速", "Speed"], f(s.v * 3.6, 0) + " km/h"], [["加速度", "Acceleration"], f(27.78 / p.t100, 2) + " m/s²"],
      [["水", "Water"], s.spill ? api.T("洒了", "spilled") : api.t > 0 ? api.T("没洒", "no spill") : "—"], sub];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, p = api.p, ink = css("--ink"), mut = css("--muted"), orange = css("--orange"), blue = css("--blue"), red = css("--red");
    if (api.scene === "agv") {
      const y0 = h * 0.8, ppm = w / 5;
      api.ground(y0, w, s.x * ppm, 50);
      const bx = w * 0.18, bw = w * 0.5, bh = h * 0.5;
      api.rect(bx, y0 - bh - 20, bw, bh, css("--panel"), ink, 8);
      api.circle(bx + bw * 0.2, y0 - 12, 12, ink); api.circle(bx + bw * 0.8, y0 - 12, 12, ink);
      const px = bx + bw * 0.5, py = y0 - bh - 20, L = bh * 0.55, tx = px - L * Math.sin(s.th), ty = py + L * Math.cos(s.th);
      api.line(px, py, tx, ty, ink, 2); api.rect(tx - 9, ty, 18, 24, css("--amber"), ink, 3);
      const cy = ty + 12, a = api.t < 3 && api.t > 0 ? RUN74[p.run - 1] : 0, k = 22;
      api.arrow(tx, cy, tx, cy + g74 * k * 0.4, ink, 2);                                        // 重力
      const T = g74 / Math.cos(s.th);
      api.arrow(tx, cy, tx + (px - tx) / L * T * k * 0.4, cy + (py - ty) / L * T * k * 0.4, ink, 2);   // 拉力
      if (p.view === 1 && a > 0) api.arrow(tx, cy, tx - a * k * 0.4, cy, orange, 3);           // 惯性力，与其他力同一比例
      if (p.view === 0 && a > 0) api.arrow(tx, cy - 30, tx + a * k * 0.4, cy - 30, red, 2);       // 合力 ma
      api.label(p.view ? api.T("车厢里看：拉力、重力和惯性力（橙）平衡", "Inside: tension, weight and the inertial force (orange) balance")
                       : api.T("地面上看：拉力与重力的合力（红）使吊牌随车加速", "From the ground: tension plus weight gives the net force (red) that accelerates the tag"), 12, 20, mut, 13);
      api.label(api.T("各力按同一比例画", "all forces to the same scale"), 12, 38, mut, 11);
      // 量角器
      for (let d = -30; d <= 30; d += 5) { const q = d * Math.PI / 180, r1 = L + 30, r2 = d % 10 ? L + 36 : L + 42;
        api.line(px + r1 * Math.sin(q), py + r1 * Math.cos(q), px + r2 * Math.sin(q), py + r2 * Math.cos(q), mut, 1);
        if (d % 10 === 0) api.label(String(Math.abs(d)), px + (L + 52) * Math.sin(q) - 6, py + (L + 52) * Math.cos(q) + 4, mut, 10); }
      return;
    }
    if (api.scene === "turn") {
      const cx = w * 0.4, cy = h * 0.5, sc = Math.min(w * 0.7, h * 0.9) / (2 * RT74 + 0.05), rot = p.view === 1 ? -s.phi : 0;
      const X = (x, y) => cx + sc * (x * Math.cos(rot) - y * Math.sin(rot)), Y = (x, y) => cy - sc * (x * Math.sin(rot) + y * Math.cos(rot));
      api.circle(cx, cy, RT74 * sc, css("--panel"), ink);
      for (let k = 0; k < 4; k++) { const q = s.phi + k * Math.PI / 2; api.line(X(0, 0), Y(0, 0), X(RT74 * Math.cos(q), RT74 * Math.sin(q)), Y(RT74 * Math.cos(q), RT74 * Math.sin(q)), mut, 1); }
      const ctx = api.ctx;
      if (s.trail.length > 1) {
        ctx.beginPath();
        s.trail.forEach(([x, y, ph], i) => {                                           // 轨迹：在所选参考系中画
          const xx = p.view === 1 ? x * Math.cos(-ph + s.phi) - y * Math.sin(-ph + s.phi) : x, yy = p.view === 1 ? x * Math.sin(-ph + s.phi) + y * Math.cos(-ph + s.phi) : y;
          const sx = X(xx, yy), sy = Y(xx, yy); i ? ctx.lineTo(sx, sy) : ctx.moveTo(sx, sy);
        });
        ctx.strokeStyle = red; ctx.lineWidth = 2; ctx.stroke();
      }
      const pos = s.slip ? s.P : [p.r * Math.cos(s.phi), p.r * Math.sin(s.phi)];
      api.rect(X(pos[0], pos[1]) - 8, Y(pos[0], pos[1]) - 8, 16, 16, css("--amber"), ink, 3);
      if (p.view === 1 && !s.slip && s.w > 0) {                                        // 转台上看：离心力（橙）与静摩擦力平衡
        const q = s.phi, ex = Math.cos(q), ey = Math.sin(q), Lf = Math.min(80, 6 * s.w * s.w * p.r * 4);
        const x0 = X(pos[0], pos[1]), y0 = Y(pos[0], pos[1]);
        api.arrow(x0, y0, x0 + (X(pos[0] + ex, pos[1] + ey) - x0) / sc * Lf, y0 + (Y(pos[0] + ex, pos[1] + ey) - y0) / sc * Lf, orange, 3);
        api.arrow(x0, y0, x0 - (X(pos[0] + ex, pos[1] + ey) - x0) / sc * Lf, y0 - (Y(pos[0] + ex, pos[1] + ey) - y0) / sc * Lf, ink, 2);
      }
      api.label(p.view ? api.T("转台上看（画面随台转动）：离心力（橙）与静摩擦力平衡", "Riding on the table: centrifugal force (orange) balances static friction")
                       : api.T("地面上看：静摩擦力提供向心力", "From the ground: static friction provides the centripetal force"), 12, 20, mut, 13);
      api.label(api.T("转台逆时针转动；红线：零件滑动后的轨迹", "table turns anticlockwise; red: path after slipping"), 12, 38, mut, 11);
      return;
    }
    // 车里的一杯水
    const cx = w * 0.4, base = h * 0.78, cw = 160, ch = 170;
    api.line(cx - cw / 2, base - ch, cx - cw / 2, base, ink, 3); api.line(cx + cw / 2, base - ch, cx + cw / 2, base, ink, 3); api.line(cx - cw / 2, base, cx + cw / 2, base, ink, 3);
    const lvl = base - ch + cw / 8, tn = Math.tan(s.th), dy = tn * cw / 2;
    const ctx = api.ctx;
    ctx.beginPath(); ctx.moveTo(cx - cw / 2, Math.max(base - ch, lvl - dy)); ctx.lineTo(cx + cw / 2, Math.max(base - ch, lvl + dy)); ctx.lineTo(cx + cw / 2, base); ctx.lineTo(cx - cw / 2, base); ctx.closePath();
    ctx.fillStyle = "rgba(29,111,184,0.35)"; ctx.fill();
    if (s.spill) for (let k = 0; k < 4; k++) api.circle(cx - cw / 2 - 10 - 8 * k, base - ch - 6 + 10 * k, 4, blue);   // 从后壁（左）洒出
    api.label(api.T("车向右加速，水面向后（左）抬高", "the car accelerates to the right; the water rises at the back (left)"), 12, 20, mut, 13);
    api.label(api.T("杯口", "rim"), cx + cw / 2 + 8, base - ch + 4, mut, 11);
  },
});
