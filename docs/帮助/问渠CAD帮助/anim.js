// 问渠 CAD 课程的互动块（样课：第 1、3、4 课）。零件尺寸、网格都在 DATA.parts（build.py 从 WQ-LS 真零件量出来）。
(function () {
  const css = (k) => getComputedStyle(document.documentElement).getPropertyValue(k).trim();
  const C = () => ({ ink: css("--ink"), muted: css("--muted"), line: css("--line"), soft: css("--soft"), paper: css("--paper"),
    accent: css("--accent"), accent2: css("--accent2"), ok: css("--ok"), bad: css("--bad"), gold: css("--gold") });
  const FONT = '"PingFang SC","Microsoft YaHei","Noto Sans CJK SC",system-ui,sans-serif';
  function canvas(el, h) {
    const cv = document.createElement("canvas");
    el.appendChild(cv);
    const fit = () => { const w = el.clientWidth - 28; cv.width = w * devicePixelRatio; cv.height = h * devicePixelRatio; cv.style.height = h + "px"; cv.style.width = w + "px"; };
    fit();
    addEventListener("resize", fit);
    const g = cv.getContext("2d");
    return { cv, g, W: () => cv.width / devicePixelRatio, H: h, begin() { g.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0); g.clearRect(0, 0, cv.width, cv.height); } };
  }
  function bar(el, html) { const b = document.createElement("div"); b.className = "bar"; b.innerHTML = html; el.appendChild(b); return b; }
  function cap(el, text) { const c = document.createElement("div"); c.className = "cap"; c.innerHTML = text; el.appendChild(c); return c; }
  function visible(el, fn) {
    let on = false;
    new IntersectionObserver((es) => { on = es[0].isIntersecting; }).observe(el);
    (function loop(t) { if (on && !document.hidden) fn(t); requestAnimationFrame(loop); })(0);
  }
  function txt(g, s, x, y, col, size, align, bold) { g.fillStyle = col; g.font = `${bold ? "600 " : ""}${size || 13}px ${FONT}`; g.textAlign = align || "left"; g.fillText(s, x, y); }
  function rbox(g, x, y, w, h, r, fill, stroke, lw) { g.beginPath(); g.roundRect(x, y, w, h, r); if (fill) { g.fillStyle = fill; g.fill(); } if (stroke) { g.strokeStyle = stroke; g.lineWidth = lw || 1.5; g.stroke(); } }

  const A = {};

  // ---------------------------------------------------------------- 第 1 课：界面地图（网页画的示意，点一块看说明）
  A.uimap = function (el) {
    const R = [
      ["menu", "菜单", 0, 0, 1, 0.045, "所有命令都在这里：文件、编辑、视图、工具、宏，以及当前工作台自己的菜单。"],
      ["tool", "工具栏", 0, 0.045, 0.62, 0.11, "常用命令的按钮。鼠标停在按钮上会显示名字和说明；换工作台，这里跟着换。"],
      ["wb", "工作台", 0.62, 0.045, 0.2, 0.055, "工作台下拉框：零件设计、草图、装配、工程图、有限元、AI Parts……换一个，工具就换一套。"],
      ["tree", "模型树", 0, 0.155, 0.17, 0.42, "文件里的每个对象，按建模的先后排。选中、隐藏（空格）、改名、拖动换组都在这里。"],
      ["prop", "属性", 0, 0.575, 0.17, 0.36, "选中对象的数据：位置、尺寸、颜色……能直接改数。"],
      ["view", "三维视图", 0.17, 0.155, 0.6, 0.78, "看模型、点选的地方。CAD 导航：中键拖平移，中键 + 左键拖旋转，滚轮缩放。"],
      ["cube", "导航立方体", 0.67, 0.165, 0.09, 0.16, "点面 = 正对那一面看；点角 = 轴测；箭头 = 转 45°。"],
      ["task", "任务面板", 0.77, 0.155, 0.23, 0.78, "命令的参数在这里填：画草图时显示约束和自由度，凸台时填长度……做完点“确定”。"],
      ["report", "报告视图", 0.17, 0.79, 0.6, 0.145, "提示、警告、出错写在这里（视图 → 面板 → 报告视图）。出了问题先看它。"],
      ["status", "状态栏", 0, 0.935, 1, 0.065, "鼠标指着什么、坐标、当前导航方式（CAD）和单位。"],
    ];
    const cv = canvas(el, 360);
    let cur = "view", hover = null;
    const info = cap(el, "");
    function rect(r) { const W = cv.W(), H = cv.H; return [r[2] * W, r[3] * H, r[4] * W, r[5] * H]; }
    function draw() {
      const c = C(), g = cv.g;
      cv.begin();
      for (const r of R) {
        const [x, y, w, h] = rect(r), on = r[0] === cur, hv = r[0] === hover;
        rbox(g, x + 2, y + 2, w - 4, h - 4, 6, on ? c.accent : hv ? c.soft : c.paper, on ? c.accent : c.line, on ? 2 : 1);
        txt(g, r[1], x + w / 2, y + h / 2 + 5, on ? "#fff" : c.ink, 13.5, "center", on);
      }
      const r = R.find((x) => x[0] === cur);
      info.innerHTML = `<b>${r[1]}</b>：${r[6]}`;
    }
    function hit(e) {
      const b = cv.cv.getBoundingClientRect(), x = e.clientX - b.left, y = e.clientY - b.top;
      for (const r of R.slice().reverse()) { const [rx, ry, rw, rh] = rect(r); if (x >= rx && x <= rx + rw && y >= ry && y <= ry + rh) return r[0]; }
      return null;
    }
    cv.cv.addEventListener("click", (e) => { const h = hit(e); if (h) { cur = h; draw(); } });
    cv.cv.addEventListener("mousemove", (e) => { const h = hit(e); if (h !== hover) { hover = h; cv.cv.style.cursor = h ? "pointer" : ""; draw(); } });
    addEventListener("resize", draw);
    document.addEventListener("themechange", draw);
    draw();
  };

  // ---------------------------------------------------------------- 第 3 课：画圆的两下（模拟草图里的圆工具）
  A.circle = function (el) {
    const cv = canvas(el, 300);
    const b = bar(el, '<button data-a="reset">重来</button> <label>键入直径 <input type="number" step="0.5" min="1" max="30" style="width:70px" placeholder="16"></label> <button data-a="enter">回车</button>');
    const info = cap(el, "");
    let st = { phase: 0, c: null, r: 0, cons: [] };
    const S = 9; // 像素 / mm
    const O = () => [cv.W() / 2, cv.H / 2];
    const toMM = (x, y) => { const [ox, oy] = O(); return [(x - ox) / S, (oy - y) / S]; };
    const toPx = (x, y) => { const [ox, oy] = O(); return [ox + x * S, oy - y * S]; };
    function dof() { if (!st.c) return null; let n = 3; for (const k of st.cons) n -= k === "重合（圆心在原点）" ? 2 : 1; return n; }
    function draw(mouse) {
      const c = C(), g = cv.g;
      cv.begin();
      const [ox, oy] = O();
      g.strokeStyle = c.bad; g.lineWidth = 1; g.beginPath(); g.moveTo(0, oy); g.lineTo(cv.W(), oy); g.stroke();
      g.strokeStyle = c.ok; g.beginPath(); g.moveTo(ox, 0); g.lineTo(ox, cv.H); g.stroke();
      if (st.c) {
        const [cx, cy] = toPx(...st.c);
        let r = st.r;
        if (st.phase === 1 && mouse) r = Math.hypot(mouse[0] - st.c[0], mouse[1] - st.c[1]);
        const full = dof() === 0;
        g.strokeStyle = full ? c.ok : c.ink; g.lineWidth = 2; g.beginPath(); g.arc(cx, cy, r * S, 0, 7); g.stroke();
        g.fillStyle = c.accent2; g.beginPath(); g.arc(cx, cy, 3.5, 0, 7); g.fill();
        if (r > 0) txt(g, `⌀${(2 * r).toFixed(st.phase === 2 ? 2 : 1)}`, cx + r * S * 0.72 + 6, cy - r * S * 0.72, c.bad, 13);
      }
      const d = dof();
      const state = d === null ? "空草图" : d === 0 ? "<b style=\"color:var(--ok)\">完全约束</b>" : `约束不足：${d} 个自由度`;
      info.innerHTML = (st.phase === 0 ? "第一下：在画布上点圆心（点在红绿两轴的交点 = 原点，软件会加“重合”）。" :
        st.phase === 1 ? "第二下：点一下定半径（拖出来的不准），或者在上面键入直径再回车。" : "画好了。") +
        `　右边会显示：${state}　约束：${st.cons.length ? st.cons.join("、") : "无"}`;
    }
    let mouse = null;
    cv.cv.addEventListener("mousemove", (e) => { const r = cv.cv.getBoundingClientRect(); mouse = toMM(e.clientX - r.left, e.clientY - r.top); if (st.phase === 1) draw(mouse); });
    cv.cv.addEventListener("click", (e) => {
      const rr = cv.cv.getBoundingClientRect(), p = toMM(e.clientX - rr.left, e.clientY - rr.top);
      if (st.phase === 0) {
        st.c = p; st.phase = 1;
        if (Math.hypot(p[0], p[1]) < 0.9) { st.c = [0, 0]; st.cons.push("重合（圆心在原点）"); }
      } else if (st.phase === 1) { st.r = Math.hypot(p[0] - st.c[0], p[1] - st.c[1]); st.phase = 2; }
      draw(mouse);
    });
    b.onclick = (e) => {
      const a = e.target.dataset.a;
      if (a === "reset") st = { phase: 0, c: null, r: 0, cons: [] };
      if (a === "enter" && st.phase === 1) {
        const v = parseFloat(b.querySelector("input").value || "16");
        if (v > 0) { st.r = v / 2; st.phase = 2; st.cons.push(`直径 ${v}`); }
      }
      draw(mouse);
    };
    document.addEventListener("themechange", () => draw(mouse));
    draw();
  };

  // ---------------------------------------------------------------- 三维小窗（three.js）：真零件，可转；“回放”按钮：草图 → 凸台
  let threeP = null;
  function three() {
    if (window.THREE) return Promise.resolve(window.THREE);
    if (!threeP) threeP = new Promise((ok, no) => { const s = document.createElement("script"); s.src = DATA.three; s.onload = () => ok(window.THREE); s.onerror = no; document.head.appendChild(s); });
    return threeP;
  }
  function viewer(el, part, profile, depth, note) {
    const box = document.createElement("div");
    box.style.cssText = "height:320px;border-radius:10px;overflow:hidden;background:var(--soft);touch-action:none";
    el.appendChild(box);
    const b = bar(el, '<button data-a="real" class="on">WQ-LS 真零件</button><button data-a="replay">回放：草图 → 凸台</button>');
    const info = cap(el, note);
    three().then((T) => {
      const W = () => box.clientWidth, H = 320;
      const ren = new T.WebGLRenderer({ antialias: true, alpha: true });
      ren.setPixelRatio(devicePixelRatio); ren.setSize(W(), H); box.appendChild(ren.domElement);
      const sc = new T.Scene();
      const cam = new T.PerspectiveCamera(32, W() / H, 0.1, 500);
      sc.add(new T.HemisphereLight(0xffffff, 0x445566, 0.9));
      const dl = new T.DirectionalLight(0xffffff, 0.8); dl.position.set(20, 30, 40); sc.add(dl);
      const mat = new T.MeshStandardMaterial({ color: 0x9aa4ad, metalness: 0.45, roughness: 0.42 });
      const gi = new T.BufferGeometry();
      gi.setAttribute("position", new T.Float32BufferAttribute(part.mesh.v, 3));
      gi.setIndex(part.mesh.f);
      const geo = gi.toNonIndexed(); geo.computeVertexNormals();      // 不共用顶点：棱是硬的，不会糊成一团
      const real = new T.Mesh(geo, mat); sc.add(real);
      const edges = new T.LineSegments(new T.EdgesGeometry(geo, 25), new T.LineBasicMaterial({ color: 0x1d2329 })); real.add(edges);
      // 回放：草图轮廓（线）→ 拉伸（ExtrudeGeometry 逐帧加深）
      const shape = profile(T);
      const grp = new T.Group(); sc.add(grp);
      const pts = shape.getPoints(64), lineG = new T.BufferGeometry().setFromPoints(pts.map((p) => new T.Vector3(p.x, p.y, 0)));
      const holes = shape.holes.map((h) => new T.Line(new T.BufferGeometry().setFromPoints(h.getPoints(64).map((p) => new T.Vector3(p.x, p.y, 0))), new T.LineBasicMaterial({ color: 0xc2410c })));
      const sk = new T.Group(); sk.add(new T.LineLoop(lineG, new T.LineBasicMaterial({ color: 0xc2410c }))); holes.forEach((h) => sk.add(h));
      grp.add(sk);
      const pad = new T.Mesh(new T.BufferGeometry(), new T.MeshStandardMaterial({ color: 0x6fb3e6, metalness: 0.2, roughness: 0.5 }));
      grp.add(pad);
      const bb = new T.Box3().setFromObject(real), size = bb.getSize(new T.Vector3()).length();
      grp.position.set(0, 0, -depth / 2);
      let az = 0.7, el2 = 0.55, dist = size * 2.1, drag = null, mode = "real", t0 = 0;
      function place() { cam.position.set(dist * Math.cos(el2) * Math.sin(az), -dist * Math.cos(el2) * Math.cos(az), dist * Math.sin(el2)); cam.up.set(0, 0, 1); cam.lookAt(0, 0, 0); }
      box.addEventListener("pointerdown", (e) => { drag = [e.clientX, e.clientY]; box.setPointerCapture(e.pointerId); });
      box.addEventListener("pointermove", (e) => { if (!drag) return; az -= (e.clientX - drag[0]) * 0.01; el2 = Math.max(-1.4, Math.min(1.4, el2 + (e.clientY - drag[1]) * 0.01)); drag = [e.clientX, e.clientY]; });
      box.addEventListener("pointerup", () => { drag = null; });
      box.addEventListener("wheel", (e) => { e.preventDefault(); dist *= e.deltaY > 0 ? 1.1 : 0.9; }, { passive: false });
      b.onclick = (e) => {
        const a = e.target.dataset.a; if (!a) return;
        mode = a; t0 = performance.now();
        b.querySelectorAll("button").forEach((x) => x.classList.toggle("on", x.dataset.a === a));
      };
      addEventListener("resize", () => { ren.setSize(W(), H); cam.aspect = W() / H; cam.updateProjectionMatrix(); });
      visible(box, (t) => {
        if (!drag) az += 0.004;
        real.visible = mode === "real"; grp.visible = mode === "replay";
        if (mode === "replay") {
          const s = Math.min(1, Math.max(0, ((t - t0) / 1000 - 1.2) / 2.2));
          pad.visible = s > 0;
          if (s > 0) { pad.geometry.dispose(); pad.geometry = new T.ExtrudeGeometry(shape, { depth: depth * s, bevelEnabled: false, curveSegments: 48 }); }
          info.innerHTML = s <= 0 ? "草图：轮廓（红线）在 XY 平面上" : s < 1 ? `凸台：拉出 ${(depth * s).toFixed(1)} mm` : `凸台 ${depth} mm 完成。${note}`;
          if ((t - t0) / 1000 > 6) t0 = t;
        } else info.innerHTML = note;
        place(); ren.render(sc, cam);
      });
    });
  }
  A.collar = function (el) {
    const p = DATA.parts.presser_collar;
    viewer(el, p, (T) => { const s = new T.Shape(); s.absarc(0, 0, p.od / 2, 0, Math.PI * 2, false); const h = new T.Path(); h.absarc(0, 0, p.id / 2, 0, Math.PI * 2, true); s.holes.push(h); return s; },
      p.t, `压脚杆套环：外径 ${p.od}、内孔 ${p.id}、厚 ${p.t} mm，体积 ${p.volume} mm³（拖动转，滚轮缩放）`);
  };
  A.clamp = function (el) {
    const p = DATA.parts.needle_clamp, R = p.R, w = p.tab_w / 2, d = p.tab_d, y0 = -Math.sqrt(R * R - w * w);
    viewer(el, p, (T) => {
      const s = new T.Shape(); s.moveTo(w, y0); s.lineTo(w, -d); s.lineTo(-w, -d); s.lineTo(-w, y0);
      s.absarc(0, 0, R, Math.atan2(y0, -w), Math.atan2(y0, w) + 2 * Math.PI, true);
      const h = new T.Path(); h.absarc(0, 0, p.bore / 2, 0, Math.PI * 2, true); s.holes.push(h); return s;
    }, p.t, `针夹：圆弧 R${R}、耳朵宽 ${p.tab_w}、伸到中心下 ${d}、厚 ${p.t}；真零件还有两个小孔（穿线孔、夹紧螺钉孔），体积 ${p.volume} mm³`);
  };

  // ---------------------------------------------------------------- 第 4 课：自由度实验（针夹轮廓，勾约束看还剩几个自由度、哪里还在动）
  A.dof = function (el) {
    const P = DATA.parts.needle_clamp;
    const L = [ // [名字, 吃掉几个自由度, 作用于哪个量]
      ["中心线下端点在下边线上", 1, "cl1"], ["中心线上端点在圆弧上", 1, "cl2"],
      ["左右下角关于 Y 轴对称", 1, "sym"], [`圆弧半径 ${P.R}`, 1, "R"], [`下边线水平距离 ${P.tab_w}`, 1, "w"], [`原点到下边线距离 ${P.tab_d}`, 1, "d"],
    ];
    const on = {};
    const cv = canvas(el, 300);
    const b = bar(el, L.map((x, i) => `<label style="margin-right:12px;white-space:nowrap"><input type="checkbox" data-i="${i}"> ${x[0]}</label>`).join("") +
      ' <button data-a="all">全勾上</button> <button data-a="none">全不勾</button>');
    const info = cap(el, "");
    b.addEventListener("change", (e) => { const i = e.target.dataset.i; if (i !== undefined) on[L[i][2]] = e.target.checked; });
    b.addEventListener("click", (e) => {
      const a = e.target.dataset.a; if (!a) return;
      b.querySelectorAll("input").forEach((x, i) => { x.checked = a === "all"; on[L[i][2]] = a === "all"; });
    });
    visible(cv.cv, (t) => {
      const c = C(), g = cv.g, s = t / 1000;
      cv.begin();
      const wob = (k, amp, ph) => (on[k] ? 0 : amp * Math.sin(s * 1.6 + ph));
      const R = P.R + wob("R", 0.9, 0), w = P.tab_w / 2 + wob("w", 0.8, 1.1), d = P.tab_d + wob("d", 1.0, 2.0), sh = wob("sym", 0.9, 0.5);
      const cl1 = wob("cl1", 1.2, 0.3), cl2 = wob("cl2", 1.0, 1.7);
      const S = Math.min(cv.W(), 520) / 26, ox = cv.W() / 2, oy = 125;
      const X = (x) => ox + x * S, Y = (y) => oy - y * S;
      const xr = w + sh, xl = -w + sh;
      const yr = -Math.sqrt(Math.max(R * R - xr * xr, 0.01)), yl = -Math.sqrt(Math.max(R * R - xl * xl, 0.01));
      const free = L.filter((x) => !on[x[2]]).length;
      const col = free === 0 ? c.ok : c.ink;
      g.strokeStyle = c.line; g.lineWidth = 1; g.beginPath(); g.moveTo(0, oy); g.lineTo(cv.W(), oy); g.moveTo(ox, 0); g.lineTo(ox, cv.H); g.stroke();
      g.strokeStyle = col; g.lineWidth = 2.2; g.beginPath();
      g.moveTo(X(xr), Y(yr)); g.lineTo(X(xr), Y(-d)); g.lineTo(X(xl), Y(-d)); g.lineTo(X(xl), Y(yl));
      g.arc(X(0), Y(0), R * S, Math.atan2(-yl, xl), Math.atan2(-yr, xr) + 2 * Math.PI, false);
      g.stroke();
      g.beginPath(); g.arc(X(0), Y(0), (P.bore / 2) * S, 0, 7); g.stroke();
      g.setLineDash([6, 4]); g.strokeStyle = free === 0 ? c.ok : c.accent; g.beginPath(); g.moveTo(X(0), Y(-d - 1.5 + cl1 * 1.5)); g.lineTo(X(0), Y(R + 1.5 + cl2)); g.stroke(); g.setLineDash([]);
      txt(g, free === 0 ? "完全约束" : `约束不足：${free} 个自由度`, 14, 22, free === 0 ? c.ok : c.ink, 15, "left", true);
      txt(g, "（几何上的竖直、重合、直径 8、圆心在原点已经有了）", 14, 42, c.muted, 12);
      info.innerHTML = free === 0 ? "全绿：轮廓每一处都定了，拖不动。凸台 8 mm 就是针夹。" :
        "还在动的部分 = 还没定住的量：" + L.filter((x) => !on[x[2]]).map((x) => x[0].replace(/ [\d.]+$/, "")).join("、") + "。";
    });
  };

  document.querySelectorAll(".anim[data-anim]").forEach((el) => { const f = A[el.dataset.anim]; if (f) f(el); });
})();
