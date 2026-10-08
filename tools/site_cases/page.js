// ---- language (shared with the home page: localStorage "wq-site-lang") ----
const root = document.documentElement, langBtn = document.getElementById("langBtn");
let lang;
try { lang = localStorage.getItem("wq-site-lang"); } catch (e) {}
lang = lang || ((navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en");
const onLang = [];
function setLang(l) {
  lang = l; root.lang = l === "en" ? "en" : "zh-CN";
  langBtn.textContent = l === "en" ? "中文" : "EN";
  try { localStorage.setItem("wq-site-lang", l); } catch (e) {}
  onLang.forEach(f => f());
}
langBtn.addEventListener("click", () => setLang(lang === "en" ? "zh" : "en"));
setLang(lang);
/*LANG-END*/
const L = () => (lang === "en" ? 1 : 0);
const STATUS = { ok: ["通过", "Passed"], hold: ["待确认", "To confirm"], na: ["不适用", "N/A"] };

// ---- process strip ----
let current = 1;
function drawChips() {
  [0, 1].forEach(lane => {
    const box = document.getElementById("lane" + lane);
    box.innerHTML = "";
    CASE.steps.filter(s => s.lane === lane).forEach(st => {
      const b = document.createElement("button");
      b.type = "button"; b.className = "step"; b.setAttribute("role", "tab");
      b.setAttribute("aria-selected", st.n === current ? "true" : "false");
      b.innerHTML = `<span class="n">${String(st.n).padStart(2, "0")}</span><span class="t">${st.t[L()]}</span><span class="pill ${st.s}">${STATUS[st.s][L()]}</span>`;
      b.addEventListener("click", () => { current = st.n; drawChips(); drawDetail(); });
      box.appendChild(b);
    });
  });
}
function drawDetail() {
  const st = CASE.steps.find(s => s.n === current);
  document.getElementById("detail").innerHTML =
    `<div><h3>${String(st.n).padStart(2, "0")} · ${st.t[L()]}</h3><p class="who">${st.who[L()]}</p>${st.body[L()]}</div><div>${st.side[L()]}</div>`;
}
drawChips(); drawDetail();
onLang.push(drawChips, drawDetail);

// ---- 3D viewer ----
(function () {
  const cv = document.getElementById("cv"), cap = document.getElementById("cap");
  let partId = CASE.parts[0].id;
  const setCap = () => { cap.innerHTML = CASE.parts.find(p => p.id === partId).cap[L()]; };
  setCap(); onLang.push(setCap);
  if (!window.THREE) { cap.textContent = lang === "en" ? "The 3D model did not load. Reload the page." : "三维模型加载失败，请刷新页面。"; return; }
  const renderer = new THREE.WebGLRenderer({ canvas: cv, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(2, window.devicePixelRatio || 1));
  const scene = new THREE.Scene();
  const cam = new THREE.PerspectiveCamera(32, 1, 1, 8000);
  scene.add(new THREE.HemisphereLight(0xdfe9ee, 0x1a252a, 0.85));
  const key = new THREE.DirectionalLight(0xffffff, 0.9); key.position.set(1, 1.4, 1.2); scene.add(key);
  const rim = new THREE.DirectionalLight(0xf2b705, 0.35); rim.position.set(-1.2, -0.4, -1); scene.add(rim);
  const holder = new THREE.Group(); scene.add(holder);
  const cache = {};
  function build(id) {
    const m = CASE.mesh[id];
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.Float32BufferAttribute(m.v, 3));
    g.setIndex(m.i); g.computeVertexNormals(); g.computeBoundingBox();
    const c = new THREE.Vector3(); g.boundingBox.getCenter(c); g.translate(-c.x, -c.y, -c.z);
    g.computeBoundingSphere();
    const grp = new THREE.Group();
    grp.add(new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: 0xbfc8cc, metalness: 0.55, roughness: 0.38, side: THREE.DoubleSide })));
    grp.add(new THREE.LineSegments(new THREE.EdgesGeometry(g, 28), new THREE.LineBasicMaterial({ color: 0x0a1216, transparent: true, opacity: 0.55 })));
    const s = m.size;  // put the longest dimension horizontal, the thinnest facing the viewer at an angle
    if (s[2] >= s[0] && s[2] >= s[1]) grp.rotation.x = -Math.PI / 2;
    if (s[2] >= s[0] && s[2] >= s[1] && s[2] > 2 * s[0]) { grp.rotation.set(0, Math.PI / 2, 0); }
    if (s[2] < 0.3 * Math.min(s[0], s[1])) grp.rotation.x = -Math.PI / 2.6;
    return { grp, r: g.boundingSphere.radius };
  }
  let obj = null;
  function select(id) {
    partId = id;
    if (obj) holder.remove(obj);
    cache[id] = cache[id] || build(id);
    obj = cache[id].grp; holder.add(obj);
    const r = cache[id].r;
    cam.position.set(0, r * 0.9, r * 3.3); cam.lookAt(0, 0, 0);
    setCap();
  }
  document.querySelectorAll(".viewer .tabs button").forEach(b => b.addEventListener("click", () => {
    document.querySelectorAll(".viewer .tabs button").forEach(x => x.setAttribute("aria-pressed", x === b ? "true" : "false"));
    select(b.dataset.part);
  }));
  select(partId);
  let rx = 0.35, ry = 0.6, drag = null, idle = true;
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  cv.addEventListener("pointerdown", e => { drag = { x: e.clientX, y: e.clientY, rx, ry }; idle = false; cv.setPointerCapture(e.pointerId); });
  cv.addEventListener("pointermove", e => { if (!drag) return; ry = drag.ry + (e.clientX - drag.x) * 0.01; rx = Math.max(-1.3, Math.min(1.3, drag.rx + (e.clientY - drag.y) * 0.01)); });
  cv.addEventListener("pointerup", () => { drag = null; });
  function resize() { const w = cv.clientWidth, h = cv.clientHeight; if (!w || !h) return; renderer.setSize(w, h, false); cam.aspect = w / h; cam.updateProjectionMatrix(); }
  window.addEventListener("resize", resize); resize();
  (function tick() { if (idle && !reduce) ry += 0.004; holder.rotation.set(rx, ry, 0); renderer.render(scene, cam); requestAnimationFrame(tick); })();
})();
