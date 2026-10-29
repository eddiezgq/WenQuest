// 缝纫机设计软件帮助的动画与小计算器（第 49 轮）。数据在 DATA 里（build.py 由计算核心和真实计算结果生成）。
(function () {
  const css = (k) => getComputedStyle(document.documentElement).getPropertyValue(k).trim();
  const C = () => ({ ink: css("--ink"), muted: css("--muted"), line: css("--line"), soft: css("--soft"), paper: css("--paper"),
    accent: css("--accent"), accent2: css("--accent2"), ok: css("--ok"), bad: css("--bad"), warn: css("--warn"), gold: css("--gold") });
  const FONT = '"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",system-ui,sans-serif';
  function canvas(el, h) {
    const cv = document.createElement("canvas");
    el.appendChild(cv);
    const fit = () => { const w = el.clientWidth - 28; cv.width = w * devicePixelRatio; cv.height = h * devicePixelRatio; cv.style.height = h + "px"; };
    fit();
    addEventListener("resize", fit);
    const g = cv.getContext("2d");
    return { cv, g, W: () => cv.width / devicePixelRatio, H: h, begin() { g.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0); g.clearRect(0, 0, cv.width, cv.height); } };
  }
  function bar(el, html) { const b = document.createElement("div"); b.className = "bar"; b.innerHTML = html; el.appendChild(b); return b; }
  function cap(el, text) { const c = document.createElement("div"); c.className = "cap"; c.innerHTML = text; el.appendChild(c); return c; }
  function visible(el, fn) { // 滚到眼前才开始动，省电
    let on = false;
    new IntersectionObserver((es) => { on = es[0].isIntersecting; }).observe(el);
    let last = 0;
    (function loop(t) { if (on && !document.hidden) { fn(t, t - (last || t)); } last = t; requestAnimationFrame(loop); })(0);
  }
  function txt(g, s, x, y, col, size, align, bold) { g.fillStyle = col; g.font = `${bold ? "600 " : ""}${size || 13}px ${FONT}`; g.textAlign = align || "left"; g.fillText(s, x, y); }
  function arrow(g, x0, y0, x1, y1, col, w) {
    g.strokeStyle = col; g.fillStyle = col; g.lineWidth = w || 2; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke();
    const a = Math.atan2(y1 - y0, x1 - x0), s = 8 + (w || 2);
    g.beginPath(); g.moveTo(x1, y1); g.lineTo(x1 - s * Math.cos(a - 0.4), y1 - s * Math.sin(a - 0.4)); g.lineTo(x1 - s * Math.cos(a + 0.4), y1 - s * Math.sin(a + 0.4)); g.closePath(); g.fill();
  }
  function rbox(g, x, y, w, h, r, fill, stroke, lw) { g.beginPath(); g.roundRect(x, y, w, h, r); if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = lw || 1.5; g.stroke(); } }
  function jet(t) { // 0→1 蓝→青→绿→黄→红（应力云图常用色带）
    t = Math.max(0, Math.min(1, t));
    const r = Math.max(0, Math.min(1, 1.5 - Math.abs(4 * t - 3))), g = Math.max(0, Math.min(1, 1.5 - Math.abs(4 * t - 2))), b = Math.max(0, Math.min(1, 1.5 - Math.abs(4 * t - 1)));
    return `rgb(${(r * 255) | 0},${(g * 255) | 0},${(b * 255) | 0})`;
  }
  function plot(g, x, y, w, h, series, opt) { // 简单曲线图：series = [{y:[], col, label}]
    const c = C();
    const all = series.flatMap((s) => s.y).filter((v) => isFinite(v));
    let lo = Math.min(...all, opt.zero ? 0 : Infinity), hi = Math.max(...all);
    if (hi - lo < 1e-9) hi = lo + 1;
    rbox(g, x, y, w, h, 6, c.paper, c.line, 1);
    const X = (i, n) => x + 8 + ((w - 16) * i) / (n - 1), Y = (v) => y + h - 18 - ((h - 34) * (v - lo)) / (hi - lo);
    if (lo < 0 && hi > 0) { g.strokeStyle = c.line; g.lineWidth = 1; g.beginPath(); g.moveTo(x + 6, Y(0)); g.lineTo(x + w - 6, Y(0)); g.stroke(); }
    series.forEach((s) => {
      if (!s.y.length) return;
      g.strokeStyle = s.col; g.lineWidth = s.w || 2; g.setLineDash(s.dash || []); g.beginPath();
      s.y.forEach((v, i) => (i ? g.lineTo(X(i, s.y.length), Y(v)) : g.moveTo(X(i, s.y.length), Y(v)))); g.stroke(); g.setLineDash([]);
    });
    txt(g, opt.title || "", x + 10, y + 16, c.muted, 12);
    txt(g, hi.toFixed(opt.dec ?? 1), x + w - 8, y + 16, c.muted, 11, "right");
    txt(g, lo.toFixed(opt.dec ?? 1), x + w - 8, y + h - 6, c.muted, 11, "right");
    let lx = x + 10;
    series.forEach((s) => { if (!s.label) return; g.fillStyle = s.col; g.fillRect(lx, y + h - 13, 14, 3); txt(g, s.label, lx + 18, y + h - 6, c.muted, 11); lx += 30 + g.measureText(s.label).width; });
    return { X, Y };
  }

  const A = {};

  // ---------- 系统结构：一次改参数，数据怎么走 ----------
  A.arch = (el) => {
    const N = [
      { k: "web", x: 0.05, y: 0.06, w: 0.27, t: "网页版", s: "浏览器里用，来宾也能试算", d: "uni-app（Vue）写的网页，和问渠学习平台同一个网址。参数在左、结果在右；三维样机用 three.js，嵌的是教材的虚拟样机。" },
      { k: "fc", x: 0.68, y: 0.06, w: 0.27, t: "FreeCAD 工作台", s: "装进 FreeCAD 1.0", d: "“问渠缝纫机”工作台：设计对象的属性就是设计参数，零件是 FreeCAD 的参数化实体（OpenCASCADE），改了按 Ctrl+R 重算。" },
      { k: "core", x: 0.34, y: 0.27, w: 0.32, t: "计算核心 sewcore", s: "两边是同一份 Python 代码", d: "五种机型的公式、判据、试缝、零件尺寸，全部出自教材《缝纫机设计与制造》。网页版在服务器上调它，FreeCAD 在本机调它——同一组参数，结果一个字都不差。" },
      { k: "gw", x: 0.05, y: 0.5, w: 0.3, t: "问渠网关", s: "账号、项目、导出、AI、零件库", d: "FastAPI 写的接口服务：认人（学习平台账号或 FreeCAD 钥匙）、按单位隔离项目和零件库、出计算书和 STEP、调大模型、把计算任务交给数字工厂。" },
      { k: "ai", x: 0.68, y: 0.5, w: 0.27, t: "大模型", s: "国内 DeepSeek · 美国 Claude", d: "只负责“听懂一句话、起草、解释、写说明”。凡是影响合格不合格的判断，都回到计算核心重算；AI 写的数由程序逐个核对。没配模型时用规则版。" },
      { k: "cae", x: 0.34, y: 0.72, w: 0.32, t: "数字工厂计算服务", s: "Gmsh · CalculiX · pyLife · MuJoCo", d: "排队算有限元（Gmsh 网格 + CalculiX）、疲劳（pyLife 雨流计数 + Miner）、模态、多体动力学（MuJoCo）、拓扑减重（SIMP）、数控编程与试切。每个单位每天有次数上限。" },
      { k: "erp", x: 0.05, y: 0.86, w: 0.25, t: "ERP 与审批", s: "ERPNext 物料 · 设计审批", d: "零件库导出 ERPNext 物料导入表；要走版本的图纸，在数字工厂“设计发布与审批”或 FreeCAD“提交到问渠工厂”提交，批准后进物料和车间。" },
      { k: "files", x: 0.7, y: 0.86, w: 0.25, t: "出件", s: "计算书 · 调机卡 · STEP · DXF", d: "Word 计算书（含 CAE 结果、AI 设计说明）、调机卡、Excel 参数表与曲线、STEP 三维、DXF 平板轮廓、FreeCAD 宏、参数文件。" },
    ];
    const E = [["web", "core"], ["fc", "core"], ["core", "gw"], ["gw", "ai"], ["gw", "cae"], ["gw", "erp"], ["gw", "files"], ["fc", "gw"]];
    const S = canvas(el, 420), info = cap(el, "点任意一块看它做什么。小圆点是一次“改参数 → 重算 → 出件 / 送算”的数据。");
    let sel = null;
    const box = (n) => { const W = S.W(); return { x: n.x * W, y: n.y * 400 + 6, w: n.w * W, h: 52 }; };
    const mid = (n) => { const b = box(n); return [b.x + b.w / 2, b.y + b.h / 2]; };
    S.cv.addEventListener("click", (e) => {
      const r = S.cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
      sel = N.find((n) => { const b = box(n); return x > b.x && x < b.x + b.w && y > b.y && y < b.y + b.h; }) || null;
      info.innerHTML = sel ? `<b>${sel.t}</b>：${sel.d}` : "点任意一块看它做什么。";
    });
    visible(el, (t) => {
      const c = C(), g = S.g; S.begin();
      E.forEach(([a, b], i) => {
        const [x0, y0] = mid(N.find((n) => n.k === a)), [x1, y1] = mid(N.find((n) => n.k === b));
        g.strokeStyle = c.line; g.lineWidth = 2; g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke();
        const p = ((t / 2400 + i * 0.37) % 1);
        g.fillStyle = i % 2 ? c.accent2 : c.accent; g.beginPath(); g.arc(x0 + (x1 - x0) * p, y0 + (y1 - y0) * p, 4, 0, 7); g.fill();
      });
      N.forEach((n) => {
        const b = box(n), on = sel === n;
        rbox(g, b.x, b.y, b.w, b.h, 10, on ? c.paper : c.soft, on ? c.accent : c.line, on ? 2.5 : 1.5);
        txt(g, n.t, b.x + b.w / 2, b.y + 22, c.ink, 14.5, "center", true);
        txt(g, n.s, b.x + b.w / 2, b.y + 41, c.muted, 11.5, "center");
      });
    });
  };

  // ---------- AI 起草 → 计算核心把关 → 人拍板 ----------
  A.aiguard = (el) => {
    const steps = [
      ["一句话", "“转速提到 6000，其他尽量不动，全部合格”"],
      ["AI 起草", "第一稿：只把转速改成 6000"],
      ["计算核心重算", `新出现 ${DATA.ai.n_bad6} 盏红灯：${DATA.ai.bad6}`],
      ["退回 AI 再改", "把新出现的红灯交回 AI"],
      ["第二稿", "转速 6000、针杆组件质量 0.10 kg、机壳一阶固有频率 240 Hz"],
      ["计算核心重算", DATA.ai.ok6b ? "全部合格，没有新红灯" : "仍有红灯"],
      ["人看对照表", "改前 / 改后、每项为什么"],
      ["点“采用”", "这时才回填参数"],
    ];
    const S = canvas(el, 250), b = bar(el, '<button>重播</button><span class="cap">一个例子。AI 只起草；能不能用，由计算核心重算决定，最后由人点“采用”。</span>');
    let t0 = performance.now();
    b.querySelector("button").onclick = () => (t0 = performance.now());
    visible(el, (t) => {
      const c = C(), g = S.g; S.begin();
      const W = S.W(), k = Math.min(steps.length, Math.floor((t - t0) / 1300) + 1), cols = W < 640 ? 2 : 4, bw = (W - 20 * (cols + 1)) / cols;
      steps.forEach((s, i) => {
        const cx = 20 + (i % cols) * (bw + 20), cy = 14 + Math.floor(i / cols) * (W < 640 ? 0 : 110) + (W < 640 ? Math.floor(i / cols) * 58 : 0);
        const on = i < k, red = i === 2 || i === 3;
        rbox(g, cx, cy, bw, W < 640 ? 50 : 92, 10, on ? c.paper : c.soft, on ? (red ? c.bad : i >= 5 ? c.ok : c.accent) : c.line, on ? 2.2 : 1);
        txt(g, `${i + 1} ${s[0]}`, cx + 10, cy + 20, on ? c.ink : c.muted, 14, "left", true);
        if (W >= 640) { g.save(); g.font = `12px ${FONT}`; wrap(g, s[1], cx + 10, cy + 42, bw - 20, 17, on ? c.muted : c.line); g.restore(); }
      });
    });
    function wrap(g, s, x, y, w, lh, col) { g.fillStyle = col; let line = ""; for (const ch of s) { if (g.measureText(line + ch).width > w) { g.fillText(line, x, y); y += lh; line = ch; } else line += ch; } g.fillText(line, x, y); }
  };

  // ---------- 有限元四步（真实结果：FreeCAD 自带 Gmsh + CalculiX 算的针杆曲柄） ----------
  A.fea = (el) => {
    const F = DATA.fea, S = canvas(el, 340);
    const b = bar(el, '<button data-k="0">① 几何</button><button data-k="1">② 网格</button><button data-k="2">③ 约束与载荷</button><button data-k="3">④ 结果</button><button data-k="auto" class="on">自动播放</button>');
    const capEl = cap(el, "");
    let k = 0, auto = true, t0 = performance.now();
    const CAPS = ["① 几何：针杆曲柄（教材算例尺寸，设计参数一改它就跟着变）。",
      "② 网格：Gmsh 把零件剖成二次四面体（这里画的是上表面的三角形）。",
      `③ 约束与载荷：轴孔固定；曲柄销孔加一转里最大的连杆力 ${F.force.toFixed(0)} N（主轴转到针杆下止点时）。全部自动加，不用自己选面。`,
      `④ 结果：CalculiX 算出的等效应力（von Mises），最大 ${F.max} MPa，在销孔边上。这是真算的结果，不是示意。`];
    b.querySelectorAll("button").forEach((x) => (x.onclick = () => { auto = x.dataset.k === "auto"; if (!auto) k = +x.dataset.k; t0 = performance.now(); b.querySelectorAll("button").forEach((y) => y.classList.toggle("on", y === x)); }));
    const xs = F.x, zs = F.z, lo = { x: Math.min(...xs), z: Math.min(...zs) }, hi = { x: Math.max(...xs), z: Math.max(...zs) };
    visible(el, (t) => {
      if (auto) k = Math.floor((t - t0) / 2600) % 4;
      capEl.textContent = CAPS[k];
      const c = C(), g = S.g; S.begin();
      const W = S.W(), sc = Math.min((W * 0.62) / (hi.x - lo.x), 300 / (hi.z - lo.z)), ox = W * 0.38 - ((lo.x + hi.x) / 2) * sc, oz = 170 + ((lo.z + hi.z) / 2) * sc;
      const P = (i) => [ox + xs[i] * sc, oz - zs[i] * sc];
      F.t.forEach((tr) => {
        const [a, bb, cc] = tr.map(P);
        g.beginPath(); g.moveTo(...a); g.lineTo(...bb); g.lineTo(...cc); g.closePath();
        if (k === 3) { const s = (F.s[tr[0]] + F.s[tr[1]] + F.s[tr[2]]) / 3; g.fillStyle = jet(s / F.max); g.fill(); }
        else { g.fillStyle = k === 0 ? "#9fb3c6" : c.soft; g.fill(); }
        if (k === 1 || k === 2) { g.strokeStyle = c.muted; g.lineWidth = 0.4; g.stroke(); }
      });
      if (k === 2) {
        const [sx, sz] = [ox, oz]; g.strokeStyle = c.accent; g.lineWidth = 3; g.beginPath(); g.arc(sx, sz, 7 * sc, 0, 7); g.stroke();
        txt(g, "轴孔固定", sx + 8 * sc, sz - 6 * sc, c.accent, 13, "left", true);
        const px = ox, pz = oz + 15.5 * sc; arrow(g, px, pz, px, pz + 60, c.bad, 3); txt(g, `${F.force.toFixed(0)} N`, px + 10, pz + 50, c.bad, 13, "left", true);
      }
      if (k === 3) { // 色带
        const lx = W - 70; for (let i = 0; i < 160; i++) { g.fillStyle = jet(1 - i / 160); g.fillRect(lx, 40 + i, 16, 1.2); }
        txt(g, `${F.max} MPa`, lx - 4, 36, c.ink, 12, "left"); txt(g, "0", lx + 22, 204, c.muted, 12);
      }
    });
  };

  // ---------- 疲劳：每针一个循环 ----------
  A.fatigue = (el) => {
    const K = DATA.crank, F = DATA.fea, SD = DATA.fatigue.S_D, S = canvas(el, 300);
    const fmax = Math.max(...K.rod.map(Math.abs)), sig = K.rod.map((v) => (v / fmax) * F.max);
    const smax = Math.max(...sig), smin = Math.min(...sig), sa = (smax - smin) / 2, sm = (smax + smin) / 2;
    cap(el, `热点应力随主轴转角变（线弹性：应力 ∝ 连杆力）。一转 = 一针 = 一个大循环：应力幅约 ${sa.toFixed(1)} MPa，修正后的疲劳极限 ${SD.toFixed(0)} MPa——远在线下，寿命按“无限”看；转速、针杆质量一加，曲线整体变高，就可能越线。服务器上用 pyLife 的雨流计数 + Miner 累积损伤逐个表面点算。`);
    visible(el, (t) => {
      const c = C(), g = S.g; S.begin();
      const W = S.W(), i = Math.floor((t / 12) % 360);
      const p = plot(g, 10, 10, W * 0.6 - 16, 270, [{ y: sig, col: c.accent, label: "热点应力（MPa）" }], { title: "一转里的应力（主轴转角 0–360°）", zero: true });
      g.fillStyle = c.accent2; g.beginPath(); g.arc(p.X(i, 360), p.Y(sig[i]), 5, 0, 7); g.fill();
      // S-N 示意：横轴寿命（对数），纵轴应力幅
      const x0 = W * 0.62, w = W * 0.38 - 12, y0 = 10, h = 270;
      rbox(g, x0, y0, w, h, 6, c.paper, c.line, 1);
      txt(g, "S–N 曲线（应力幅 vs 循环次数）", x0 + 10, y0 + 16, c.muted, 12);
      const Y = (s) => y0 + h - 24 - ((h - 50) * s) / (SD * 2.2), X = (lg) => x0 + 14 + ((w - 28) * (lg - 3)) / 6;
      g.strokeStyle = c.ink; g.lineWidth = 2; g.beginPath(); g.moveTo(X(3), Y(SD * 2)); g.lineTo(X(7), Y(SD)); g.lineTo(X(9), Y(SD)); g.stroke();
      txt(g, `疲劳极限 ${SD.toFixed(0)} MPa`, X(7), Y(SD) - 8, c.ink, 11);
      g.setLineDash([4, 4]); g.strokeStyle = c.accent2; g.beginPath(); g.moveTo(X(3), Y(sa)); g.lineTo(X(9), Y(sa)); g.stroke(); g.setLineDash([]);
      txt(g, `本零件 ${sa.toFixed(1)} MPa`, X(3) + 4, Y(sa) - 6, c.accent2, 11);
      txt(g, "10³", X(3), y0 + h - 8, c.muted, 10, "center"); txt(g, "10⁶", X(6), y0 + h - 8, c.muted, 10, "center"); txt(g, "10⁹", X(9), y0 + h - 8, c.muted, 10, "center");
      void sm;
    });
  };

  // ---------- 多体动力学：刺布机构转一圈 ----------
  A.mbd = (el) => {
    const K = DATA.crank, S = canvas(el, 330);
    const b = bar(el, '<span>速度</span><input type="range" min="0.1" max="1.5" step="0.05" value="0.5"><button>暂停</button>');
    cap(el, `左边是曲柄滑块（曲柄 ${K.r} mm、连杆 ${K.l} mm、针杆组件 ${K.mr} kg、${K.n} r/min）；右边是驱动它要的主轴转矩：实线是本软件的公式，虚线是数字工厂用 MuJoCo 多体动力学真算的那一转${K.mujoco.length ? "" : "（本页没有带上）"}。两条线峰值相差 ${DATA.ai.mbd_diff}%。`);
    let sp = 0.5, run = true, ph = 0;
    b.querySelector("input").oninput = (e) => (sp = +e.target.value);
    b.querySelector("button").onclick = (e) => { run = !run; e.target.textContent = run ? "暂停" : "继续"; };
    visible(el, (t, dt) => {
      if (run) ph = (ph + dt * 0.36 * sp) % 360;
      const c = C(), g = S.g; S.begin();
      const W = S.W(), i = Math.floor(ph), a = (ph * Math.PI) / 180, s = 3.1;
      const cx = W * 0.18, cy = 74, pin = [cx + K.r * s * Math.sin(a), cy - K.r * s * Math.cos(a)];
      const yb = cy - K.r * s + K.pos[i] * s + K.l * s; // 针杆接头（上止点时在 cy - r + l… 往下）
      // 机架
      g.strokeStyle = c.line; g.lineWidth = 1; g.beginPath(); g.moveTo(cx, 20); g.lineTo(cx, 320); g.stroke();
      g.fillStyle = c.soft; g.fillRect(cx - 10, yb, 20, 140); g.strokeStyle = c.muted; g.strokeRect(cx - 10, yb, 20, 140);
      txt(g, "针杆", cx + 16, yb + 70, c.muted, 12);
      g.strokeStyle = c.accent; g.lineWidth = 7; g.lineCap = "round"; g.beginPath(); g.moveTo(cx, cy); g.lineTo(...pin); g.stroke();
      g.strokeStyle = c.gold; g.lineWidth = 5; g.beginPath(); g.moveTo(...pin); g.lineTo(cx, yb); g.stroke(); g.lineCap = "butt";
      g.fillStyle = c.ink; g.beginPath(); g.arc(cx, cy, 5, 0, 7); g.fill(); g.beginPath(); g.arc(...pin, 4, 0, 7); g.fill();
      txt(g, `主轴 ${i}°`, cx - 30, 16, c.ink, 12);
      const ser = [{ y: K.torque, col: c.accent, label: "公式" }];
      if (K.mujoco.length) ser.push({ y: K.mujoco, col: c.accent2, dash: [5, 4], label: "MuJoCo" });
      const p = plot(g, W * 0.38, 10, W * 0.62 - 10, 300, ser, { title: "刺布机构要的主轴转矩（N·m）", dec: 2 });
      g.strokeStyle = c.muted; g.lineWidth = 1; g.beginPath(); g.moveTo(p.X(i, 360), 26); g.lineTo(p.X(i, 360), 292); g.stroke();
      g.fillStyle = c.accent; g.beginPath(); g.arc(p.X(i, 360), p.Y(K.torque[i]), 5, 0, 7); g.fill();
    });
  };

  // ---------- 模态：机壳离共振多远（公式与判据同软件的“二阶共振”校核） ----------
  A.modal = (el) => {
    const D0 = DATA.frame, S = canvas(el, 250);
    const b = bar(el, `<span>转速</span><input type="range" min="2000" max="7000" step="100" value="${D0.n}"><b class="vn">${D0.n}</b><span>r/min　机壳一阶固有频率</span><input type="range" min="100" max="400" step="5" value="${D0.fn}"><b class="vf">${D0.fn}</b><span>Hz</span>`);
    const ci = cap(el, "");
    const [rn, rf] = b.querySelectorAll("input");
    visible(el, (t) => {
      const n = +rn.value, fn = +rf.value, f2 = (2 * n) / 60, ratio = f2 / fn;
      b.querySelector(".vn").textContent = n; b.querySelector(".vf").textContent = fn;
      const st = ratio <= 0.9 ? "ok" : ratio < 1.1 ? "bad" : "warn";
      ci.innerHTML = `平缝机整机惯性力里最麻烦的是<b>二阶</b>（每转两次）：二阶激振频率 = 2 × ${n} / 60 = ${f2.toFixed(0)} Hz，除以机壳一阶固有频率 = <b>${ratio.toFixed(2)}</b>，软件要求 ≤ 0.90。` +
        (st === "ok" ? "离共振够远。" : st === "bad" ? "<b style='color:var(--bad)'>接近共振，机器会抖、会响。</b>改机壳（加筋、加厚）把固有频率提上去，或者降转速。" : "已经越过共振区（超临界），起停时要穿过共振，一般不这样设计。") +
        " 一阶固有频率从哪来：“CAE 分析 → 机壳固有频率”上传机壳 STEP（或从零件库选），CalculiX 算模态，算完一键回填。左边的振型是示意。";
      const c = C(), g = S.g; S.begin();
      const W = S.W(), amp = Math.sin((t / 1000) * 2 * Math.PI * Math.min(3, f2 / 60)) * (st === "ok" ? 4 : st === "bad" ? 14 : 6);
      // C 形机壳示意：立柱 + 机臂，悬臂端随振型摆
      g.strokeStyle = c.accent; g.lineWidth = 16; g.lineCap = "round"; g.beginPath(); g.moveTo(60, 220); g.lineTo(W * 0.5, 220); g.stroke();
      g.beginPath(); g.moveTo(W * 0.46, 220); g.quadraticCurveTo(W * 0.46 + amp * 0.3, 140, W * 0.46 + amp * 0.6, 70); g.stroke();
      g.beginPath(); g.moveTo(W * 0.46 + amp * 0.6, 70); g.quadraticCurveTo(W * 0.3, 70 + amp * 0.4, 90 + amp, 70 + amp * 1.2); g.stroke(); g.lineCap = "butt";
      txt(g, "机臂", W * 0.25, 54, c.muted, 12); txt(g, "立柱", W * 0.5, 140, c.muted, 12); txt(g, "底板", W * 0.25, 246, c.muted, 12);
      // 频率对照条
      const x0 = W * 0.58, w = W * 0.4 - 10, X = (f) => x0 + (w * f) / 450;
      rbox(g, x0, 40, w, 150, 8, c.paper, c.line, 1);
      g.fillStyle = "rgba(180,35,24,.15)"; g.fillRect(X(fn * 0.9), 50, X(fn * 1.1) - X(fn * 0.9), 130);
      g.fillStyle = c.ink; g.fillRect(X(fn) - 1, 50, 2, 130); txt(g, `固有 ${fn} Hz`, X(fn), 196, c.ink, 12, "center");
      g.fillStyle = st === "ok" ? c.ok : c.bad; g.beginPath(); g.arc(X(f2), 115, 8, 0, 7); g.fill(); txt(g, `二阶激振 ${f2.toFixed(0)} Hz`, X(f2), 100, st === "ok" ? c.ok : c.bad, 12, "center", true);
      txt(g, "共振区", X(fn), 66, c.bad, 11, "center");
    });
  };

  // ---------- 拓扑减重：浏览器里真算一个小号 SIMP ----------
  A.topo = (el) => {
    const nx = 48, ny = 24, S = canvas(el, 260);
    const b = bar(el, '<span>留下的材料</span><input type="range" min="0.3" max="0.7" step="0.05" value="0.5"><b class="vv">50%</b><button>开始算</button><span class="st"></span>');
    cap(el, "这是在你的浏览器里真算的 SIMP 拓扑优化（和服务器“零件减重”同一个经典方法，网格小很多，只为看懂）：左边孔固定，右边孔往下拉，材料慢慢“长”到传力的路线上。服务器上用真实零件外形、一转里最大的那个力；算完<b>一定要送有限元复核</b>（强度、寿命）。");
    const vv = b.querySelector(".vv"), st = b.querySelector(".st"), inp = b.querySelector("input");
    inp.oninput = () => (vv.textContent = Math.round(inp.value * 100) + "%");
    let x = null, busy = false, it = 0;
    b.querySelector("button").onclick = () => { if (busy) return; x = new Float64Array(nx * ny).fill(+inp.value); it = 0; busy = true; step(); };
    const KE = lk();
    const ndof = 2 * (nx + 1) * (ny + 1), band = 2 * (ny + 1) + 4;   // 一个单元里自由度编号最大差 2(ny+1)+3
    const nid = (i, j) => i * (ny + 1) + j; // 节点：i 列 0..nx，j 行 0..ny（从上往下）
    const hole = (cx, cy, r) => (i, j) => (i + 0.5 - cx) ** 2 + (j + 0.5 - cy) ** 2 < r * r;
    const inL = hole(8, ny / 2, 4), inR = hole(nx - 8, ny / 2, 2.6), ringL = hole(8, ny / 2, 6.5), ringR = hole(nx - 8, ny / 2, 4.6);
    const fixed = new Set(), F = new Float64Array(ndof);
    for (let i = 0; i <= nx; i++) for (let j = 0; j <= ny; j++) {
      const d = Math.hypot(i - 8, j - ny / 2); if (d <= 4.3 && d >= 3.2) { fixed.add(2 * nid(i, j)); fixed.add(2 * nid(i, j) + 1); }
      const d2 = Math.hypot(i - (nx - 8), j - ny / 2); if (d2 <= 2.9 && d2 >= 1.8) F[2 * nid(i, j) + 1] += 1;
    }
    function lk() { const E = 1, nu = 0.3, k = [1 / 2 - nu / 6, 1 / 8 + nu / 8, -1 / 4 - nu / 12, -1 / 8 + 3 * nu / 8, -1 / 4 + nu / 12, -1 / 8 - nu / 8, nu / 6, 1 / 8 - 3 * nu / 8];
      const f = E / (1 - nu * nu), m = [[0, 1, 2, 3, 4, 5, 6, 7], [1, 0, 7, 6, 5, 4, 3, 2], [2, 7, 0, 5, 6, 3, 4, 1], [3, 6, 5, 0, 7, 2, 1, 4], [4, 5, 6, 7, 0, 1, 2, 3], [5, 4, 3, 2, 1, 0, 7, 6], [6, 3, 4, 1, 2, 7, 0, 5], [7, 2, 1, 4, 3, 6, 5, 0]];
      return m.map((r) => r.map((q) => f * k[q])); }
    function edof(i, j) { const n1 = nid(i, j), n2 = nid(i + 1, j); return [2 * n1 + 2, 2 * n1 + 3, 2 * n2 + 2, 2 * n2 + 3, 2 * n2, 2 * n2 + 1, 2 * n1, 2 * n1 + 1]; }
    function solve(xp) { // 带状 Cholesky（对称正定），固定自由度用大数罚
      const B = band, A2 = new Float64Array(ndof * B);
      for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
        const e = i * ny + j, Ee = 1e-9 + xp[e] ** 3, d = edof(i, j);
        for (let a = 0; a < 8; a++) for (let c2 = 0; c2 < 8; c2++) { const r = d[a], s = d[c2]; if (s >= r && s - r < B) A2[r * B + (s - r)] += Ee * KE[a][c2]; }
      }
      const f = Float64Array.from(F); for (const q of fixed) { A2[q * B] += 1e12; f[q] = 0; }
      for (let k = 0; k < ndof; k++) { let s = A2[k * B]; for (let m2 = Math.max(0, k - B + 1); m2 < k; m2++) { const v = A2[m2 * B + (k - m2)]; s -= v * v; } const dk = Math.sqrt(s); A2[k * B] = dk;
        for (let r = k + 1; r < Math.min(ndof, k + B); r++) { let s2 = A2[k * B + (r - k)]; for (let m2 = Math.max(0, r - B + 1); m2 < k; m2++) s2 -= A2[m2 * B + (k - m2)] * A2[m2 * B + (r - m2)]; A2[k * B + (r - k)] = s2 / dk; } }
      const y = new Float64Array(ndof); for (let k = 0; k < ndof; k++) { let s = f[k]; for (let m2 = Math.max(0, k - B + 1); m2 < k; m2++) s -= A2[m2 * B + (k - m2)] * y[m2]; y[k] = s / A2[k * B]; }
      const u = new Float64Array(ndof); for (let k = ndof - 1; k >= 0; k--) { let s = y[k]; for (let r = k + 1; r < Math.min(ndof, k + B); r++) s -= A2[k * B + (r - k)] * u[r]; u[k] = s / A2[k * B]; }
      return u;
    }
    function step() {
      const vf = +inp.value, xp = Float64Array.from(x);
      for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) { const e = i * ny + j; if (inL(i, j) || inR(i, j)) xp[e] = 0.001; else if (ringL(i, j) || ringR(i, j)) xp[e] = 1; }
      const u = solve(xp), dc = new Float64Array(nx * ny);
      for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) { const e = i * ny + j, d = edof(i, j); let ce = 0; for (let a = 0; a < 8; a++) for (let c2 = 0; c2 < 8; c2++) ce += u[d[a]] * KE[a][c2] * u[d[c2]]; dc[e] = -3 * xp[e] ** 2 * ce; }
      const dcf = new Float64Array(nx * ny), rmin = 1.5; // 灵敏度过滤
      for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) { let s = 0, w = 0; for (let k = Math.max(0, i - 2); k < Math.min(nx, i + 3); k++) for (let l = Math.max(0, j - 2); l < Math.min(ny, j + 3); l++) { const f2 = Math.max(0, rmin - Math.hypot(i - k, j - l)); s += f2 * x[k * ny + l] * dc[k * ny + l]; w += f2; } dcf[i * ny + j] = s / (Math.max(1e-3, x[i * ny + j]) * w); }
      let l1 = 0, l2 = 1e9; const xn = new Float64Array(nx * ny); // 最优准则法
      while ((l2 - l1) / (l1 + l2) > 1e-3) { const lm = (l1 + l2) / 2; let sum = 0; for (let e = 0; e < nx * ny; e++) { xn[e] = Math.max(0.001, Math.max(x[e] - 0.2, Math.min(1, Math.min(x[e] + 0.2, x[e] * Math.sqrt(-dcf[e] / lm))))); sum += xn[e]; } if (sum > vf * nx * ny) l1 = lm; else l2 = lm; }
      for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) { const e = i * ny + j; if (inL(i, j) || inR(i, j)) xn[e] = 0.001; else if (ringL(i, j) || ringR(i, j)) xn[e] = 1; }
      x = xn; it++; st.textContent = `第 ${it} 步`;
      if (it < 40) setTimeout(step, 0); else { busy = false; st.textContent = `算完（${it} 步）`; }
    }
    visible(el, () => {
      const c = C(), g = S.g; S.begin();
      const W = S.W(), cs = Math.min((W - 20) / nx, 230 / ny), ox = (W - cs * nx) / 2;
      for (let i = 0; i < nx; i++) for (let j = 0; j < ny; j++) {
        let v = x ? x[i * ny + j] : 1; if (inL(i, j) || inR(i, j)) v = 0; else if (ringL(i, j) || ringR(i, j)) v = 1;
        g.fillStyle = v > 0.5 ? c.accent : v > 0.2 ? c.soft : c.paper; g.globalAlpha = Math.max(0.15, v); g.fillRect(ox + i * cs, 10 + j * cs, cs + 0.5, cs + 0.5);
      }
      g.globalAlpha = 1; arrow(g, ox + (nx - 8) * cs, 10 + (ny / 2) * cs, ox + (nx - 8) * cs, 10 + (ny / 2) * cs + 50, c.bad, 2.5);
      if (!x) txt(g, "点“开始算”", W / 2, 140, c.ink, 15, "center", true);
    });
  };

  // ---------- 零件族：一张表 → 一族零件 ----------
  A.family = (el) => {
    const rows = [["CR-15.0", 15.0], ["CR-15.5", 15.5], ["CR-16.0", 16.0], ["CR-16.5", 16.5]], S = canvas(el, 230);
    cap(el, "Excel 模板里一行一个规格（这里是两孔曲柄，孔距 15.0–16.5 mm）。上传后逐行检查（缺字段、超范围、编号重复都标红），全部没问题才入库；有造型程序的类别每个规格自动生成三维（STEP），并且标好它能接进设计的哪个参数（孔距 → 曲柄半径）。");
    visible(el, (t) => {
      const c = C(), g = S.g; S.begin();
      const W = S.W(), k = Math.floor(t / 900) % (rows.length + 2);
      rbox(g, 10, 10, W * 0.36, 200, 8, c.paper, c.line, 1);
      txt(g, "编号　　　名称　　孔距 mm", 22, 34, c.muted, 12);
      rows.forEach((r, i) => { const on = i < k; rbox(g, 16, 46 + i * 38, W * 0.36 - 12, 30, 5, on ? c.soft : "transparent", on ? c.accent : c.line, on ? 1.5 : 0.5); txt(g, `${r[0]}　针杆曲柄　${r[1].toFixed(1)}`, 26, 66 + i * 38, c.ink, 12.5); if (on) txt(g, "✓", W * 0.36 - 6, 66 + i * 38, c.ok, 14, "right", true); });
      arrow(g, W * 0.39, 110, W * 0.45, 110, c.muted, 2);
      rows.forEach((r, i) => {
        if (i >= k) return;
        const cx = W * 0.5 + (i % 2) * W * 0.24, cy = 60 + Math.floor(i / 2) * 100, s = 2.6, L = r[1] * s;
        g.fillStyle = c.accent; g.globalAlpha = 0.85; g.beginPath(); g.arc(cx, cy, 11 * s * 0.55, Math.PI / 2, -Math.PI / 2); g.lineTo(cx + L, cy - 7 * s * 0.55); g.arc(cx + L, cy, 7 * s * 0.55, -Math.PI / 2, Math.PI / 2); g.closePath(); g.fill(); g.globalAlpha = 1;
        g.fillStyle = c.paper; g.beginPath(); g.arc(cx, cy, 7 * s * 0.5, 0, 7); g.fill(); g.beginPath(); g.arc(cx + L, cy, 3.5 * s * 0.5, 0, 7); g.fill();
        txt(g, r[0], cx + L / 2, cy + 34, c.ink, 12, "center");
      });
    });
  };

  // ---------- AI 整理样本：每个数都要找得到出处 ----------
  A.extract = (el) => {
    const S = canvas(el, 240);
    cap(el, "AI 从 PDF 的文字里抽表，每个值附一段原文出处；程序再把每个数拿回 PDF 文字里找：找到了打 ✓，找不到打 ？（常见于单位换算、看错行）。整批先进“待复核”，人逐行对照、改对后点“复核无误，设为可用”。待复核的零件不会出现在设计和选型里。");
    const doc = ["SV-400 交流伺服电机", "额定功率 400 W　额定转矩 1.27 N·m", "峰值转矩 4.46 N·m", "额定转速 3000 r/min　最高 6000 r/min", "转子惯量 0.42 ×10⁻⁴ kg·m²", "法兰 60 mm"];
    const cells = [["额定转矩", "1.27", true], ["峰值转矩", "4.46", true], ["额定转速", "3000", true], ["转子惯量", "0.42", true], ["机身长", "95", false]];
    visible(el, (t) => {
      const c = C(), g = S.g; S.begin();
      const W = S.W(), k = Math.floor(t / 800) % (cells.length + 3);
      rbox(g, 10, 10, W * 0.42, 210, 8, c.paper, c.line, 1); txt(g, "PDF 样本（文字）", 20, 30, c.muted, 12);
      doc.forEach((d, i) => txt(g, d, 20, 58 + i * 26, c.ink, 12.5));
      arrow(g, W * 0.44, 110, W * 0.5, 110, c.muted, 2); txt(g, "AI 抽取", W * 0.47, 98, c.muted, 11, "center");
      rbox(g, W * 0.52, 10, W * 0.46, 210, 8, c.paper, c.line, 1); txt(g, "待复核", W * 0.52 + 12, 30, c.warn, 12, "left", true);
      cells.forEach((x, i) => { if (i >= k) return; txt(g, x[0], W * 0.52 + 14, 58 + i * 30, c.ink, 12.5); txt(g, x[1], W * 0.52 + 120, 58 + i * 30, c.ink, 12.5, "left", true); txt(g, x[2] ? "✓ 在 PDF 里找到" : "？ PDF 里没有", W * 0.52 + 175, 58 + i * 30, x[2] ? c.ok : c.warn, 12); });
      if (k >= cells.length + 1) { rbox(g, W * 0.52 + 12, 196, 140, 20, 5, c.ok); txt(g, "人复核后 → 可用", W * 0.52 + 82, 211, "#fff", 12, "center", true); }
    });
  };

  // ---------- 小计算器：转速与红绿灯（直接调软件的计算接口，来宾也能用） ----------
  const CALC = {};
  CALC.speed = (el) => {
    const P = [["n", "最高转速", 2000, 7000, 100, "r/min"], ["mr", "针杆组件质量", 0.05, 0.25, 0.005, "kg"], ["fn", "机壳一阶固有频率", 100, 400, 5, "Hz"]];
    el.innerHTML = "<b>小计算器：转速与红绿灯</b><div class='cap'>拖滑块，下面 " + DATA.ai.checks_lockstitch + " 项校核当场重算——调的就是软件的计算接口，和软件里一模一样。</div>";
    const vals = { n: 5000, mr: 0.12, fn: 190 };
    P.forEach(([k, zh, lo, hi, st, u]) => {
      const r = document.createElement("div"); r.className = "row";
      r.innerHTML = `<span>${zh}</span><input type="range" min="${lo}" max="${hi}" step="${st}" value="${vals[k]}"><b>${vals[k]} ${u}</b>`;
      r.querySelector("input").oninput = (e) => { vals[k] = +e.target.value; r.querySelector("b").textContent = `${vals[k]} ${u}`; go(); };
      el.appendChild(r);
    });
    const sum = document.createElement("div"); sum.className = "sum"; el.appendChild(sum);
    const list = document.createElement("div"); list.className = "checks"; el.appendChild(list);
    let tm = null;
    function go() { clearTimeout(tm); tm = setTimeout(run, 200); }
    async function run() {
      if (location.protocol === "file:") { sum.className = "sum warn"; sum.innerHTML = "这是离线帮助：小计算器要联网，打开<a href='https://learn.wenquestrobotics.com/static/help/sewing-freecad/index.html'>在线版</a>就能用。"; return; }
      try {
        const r = await fetch((API || "") + "/api/v1/sewing/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ machine: "lockstitch", params: vals }) });
        const R = await r.json();
        const bad = R.checks.filter((c) => c.state === "bad").length, warn = R.checks.filter((c) => c.state === "warn").length;
        sum.className = "sum " + (bad ? "bad" : warn ? "warn" : "ok");
        sum.textContent = bad || warn ? `不合格 ${bad} 项，注意 ${warn} 项（共 ${R.checks.length} 项）` : `全部 ${R.checks.length} 项合格`;
        list.innerHTML = R.checks.map((c) => `<div><span class="lamp ${c.state}"></span>${c.name.zh}：${c.value.zh}</div>`).join("");
      } catch (e) { sum.className = "sum warn"; sum.textContent = "连不上计算接口（" + e.message + "）"; }
    }
    run();
  };

  document.querySelectorAll(".anim").forEach((el) => { const f = A[el.dataset.anim]; if (f) f(el); });
  document.querySelectorAll(".calc").forEach((el) => { const f = CALC[el.dataset.calc]; if (f) f(el); });
  // 动画、计算器插进页面后高度变了：带 #节 打开时再对准一次
  if (location.hash) { const t = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (t) setTimeout(() => t.scrollIntoView(), 60); }
})();
