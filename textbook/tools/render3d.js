// 书中三维图与三维动画的渲染页（第 13 轮 8.3 R2）：render3d.py 把场景（零件网格、相机、标注）交给这一页，
// 用 three.js 着色并画轮廓线，再在上面叠一层 SVG（零件序号、文字、尺寸、箭头）。整页截图就是书里的图；
// 三维动画逐帧调用 window.frame(state)。
import * as THREE from "./three.module.js";

const S = window.SCENE;
const W = S.width, H = S.height;
const box = document.getElementById("box");
box.style.width = W + "px"; box.style.height = H + "px";
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, alpha: false });
renderer.setPixelRatio(S.scale || 2);
renderer.setSize(W, H);
renderer.setClearColor(new THREE.Color(S.background || "#ffffff"), 1);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.localClippingEnabled = true;
box.appendChild(renderer.domElement);
const svgNS = "http://www.w3.org/2000/svg";
const ov = document.createElementNS(svgNS, "svg");
ov.setAttribute("width", W); ov.setAttribute("height", H);
ov.style.position = "absolute"; ov.style.left = "0"; ov.style.top = "0";
box.appendChild(ov);

const scene = new THREE.Scene();
scene.add(new THREE.AmbientLight(0xffffff, S.ambient ?? 1.15));
const key = new THREE.DirectionalLight(0xffffff, S.key ?? 1.6);
const fill = new THREE.DirectionalLight(0xffffff, 0.55);
scene.add(key); scene.add(fill); scene.add(key.target); scene.add(fill.target);

const groups = {};          // 零件名 → THREE.Group
const allBox = new THREE.Box3();
const EDGE = new THREE.LineBasicMaterial({ color: S.edgeColor || 0x1d2327 });
const SECTION = new THREE.MeshStandardMaterial({ color: new THREE.Color(S.sectionColor || "#f4e1d2"), roughness: 0.9, metalness: 0,
  polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1, side: THREE.DoubleSide });

// 剖面：零件本色调浅，加 45° 剖面线（屏幕坐标，线距固定），像工程图的剖面一样能分清各个零件
function sectionMat(color) {
  const c = new THREE.Color(color).lerp(new THREE.Color("#ffffff"), 0.45);
  const d = new THREE.Color(color).multiplyScalar(0.55);
  return new THREE.ShaderMaterial({
    uniforms: { c: { value: c }, d: { value: d }, gap: { value: (S.hatchPx ?? 9.0) * (S.scale || 1) } },
    vertexShader: `void main(){ gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `uniform vec3 c; uniform vec3 d; uniform float gap;
      void main(){ float t = mod(gl_FragCoord.x + gl_FragCoord.y, gap); vec3 col = t < 1.3 ? d : c; gl_FragColor = vec4(col, 1.0); }`,
    side: THREE.DoubleSide, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
}

function material(color, opacity) {
  return new THREE.MeshStandardMaterial({ color: new THREE.Color(color), roughness: 0.62, metalness: 0.12,
    transparent: opacity < 1, opacity, depthWrite: opacity >= 1, polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
    side: THREE.DoubleSide });
}

for (const p of S.parts) {
  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(p.v, 3));
  g.setIndex(p.t);
  g.computeVertexNormals();
  const mats = [material(p.color, p.opacity ?? 1)];
  // 按面着色的组与剖面三角形：重新排列索引，每组一个材料
  const ntri = p.t.length / 3;
  const matOf = new Int32Array(ntri);          // 0 = 零件本色
  const colorIdx = {};
  for (const [start, count, color] of p.g || []) {
    if (!(color in colorIdx)) { colorIdx[color] = mats.length; mats.push(material(color, p.opacity ?? 1)); }
    for (let k = start; k < start + count; k++) matOf[k] = colorIdx[color];
  }
  if ((p.s || []).length) { const si = mats.length; mats.push(sectionMat(p.color)); for (const k of p.s) matOf[k] = si; }
  if (mats.length > 1) {
    const idx = [];
    for (let m = 0; m < mats.length; m++) {
      const start = idx.length;
      for (let k = 0; k < ntri; k++) if (matOf[k] === m) idx.push(p.t[3 * k], p.t[3 * k + 1], p.t[3 * k + 2]);
      if (idx.length > start) g.addGroup(start, idx.length - start, m);
    }
    g.setIndex(idx);
  }
  const mesh = new THREE.Mesh(g, mats.length > 1 ? mats : mats[0]);
  const grp = new THREE.Group();
  grp.add(mesh);
  if (S.edges !== false && (p.opacity ?? 1) > 0.35) {
    const e = new THREE.LineSegments(new THREE.EdgesGeometry(g, S.edgeAngle ?? 28), EDGE);
    grp.add(e);
  }
  if (S.outline !== false && (p.opacity ?? 1) > 0.35) grp.add(outlineMesh(g));
  grp.userData.base = new THREE.Vector3(0, 0, 0);
  grp.userData.explode = new THREE.Vector3(...(p.explode || [0, 0, 0]));
  scene.add(grp);
  groups[p.name] = grp;
  g.computeBoundingBox();
  allBox.union(g.boundingBox);
}

// 轮廓（剪影）：背面向外推出一点、画成深色，正面挡住中间，只露出外缘——曲面的轮廓线
function outlineMesh(g) {
  const m = new THREE.ShaderMaterial({
    uniforms: { w: { value: (S.outlinePx ?? 1.1) }, pix: { value: 1 } },
    vertexShader: `uniform float w; uniform float pix;
      void main(){ vec4 p = modelViewMatrix * vec4(position, 1.0); vec3 n = normalize(normalMatrix * normal);
        p.xyz += n * w * pix; gl_Position = projectionMatrix * p; }`,
    fragmentShader: `void main(){ gl_FragColor = vec4(0.114, 0.137, 0.153, 1.0); }`,
    side: THREE.BackSide });
  const o = new THREE.Mesh(g, m);
  o.userData.outline = true;
  return o;
}

// 相机：正交投影，方向由“从目标看向相机”的向量给出
const cam = new THREE.OrthographicCamera(-1, 1, 1, -1, -1e5, 1e5);
function setCamera(c) {
  const dir = new THREE.Vector3(...(c.dir || [1, -1.4, 0.9])).normalize();
  const up = new THREE.Vector3(...(c.up || [0, 0, 1]));
  const fitBox = c.fit ? new THREE.Box3(new THREE.Vector3(...c.fit[0]), new THREE.Vector3(...c.fit[1])) : currentBox();
  const center = c.target ? new THREE.Vector3(...c.target) : fitBox.getCenter(new THREE.Vector3());
  cam.up.copy(up);
  cam.position.copy(center).addScaledVector(dir, 5000);
  cam.lookAt(center);
  cam.updateMatrixWorld();
  // 包围盒 8 个角点投影到相机平面，求宽高
  const inv = cam.matrixWorldInverse;
  let x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
  for (const x of [fitBox.min.x, fitBox.max.x]) for (const y of [fitBox.min.y, fitBox.max.y]) for (const z of [fitBox.min.z, fitBox.max.z]) {
    const q = new THREE.Vector3(x, y, z).applyMatrix4(inv);
    x0 = Math.min(x0, q.x); x1 = Math.max(x1, q.x); y0 = Math.min(y0, q.y); y1 = Math.max(y1, q.y);
  }
  const m = c.margin ?? 0.08, aspect = W / H;
  let w = (x1 - x0) * (1 + 2 * m), h = (y1 - y0) * (1 + 2 * m);
  if (w / h > aspect) h = w / aspect; else w = h * aspect;
  w /= (c.zoom || 1); h /= (c.zoom || 1);
  const cx = (x0 + x1) / 2 + (c.pan ? c.pan[0] * w : 0), cy = (y0 + y1) / 2 + (c.pan ? c.pan[1] * h : 0);
  cam.left = cx - w / 2; cam.right = cx + w / 2; cam.top = cy + h / 2; cam.bottom = cy - h / 2;
  cam.updateProjectionMatrix();
  const pix = w / W;                       // 每像素多少 mm：轮廓线宽按像素给
  scene.traverse((o) => { if (o.userData.outline) o.material.uniforms.pix.value = pix; });
  // 灯光跟着相机：主光在相机左上方
  const right = new THREE.Vector3().crossVectors(dir, up).normalize();
  key.position.copy(center).addScaledVector(dir, 1000).addScaledVector(up, 900).addScaledVector(right, -700);
  key.target.position.copy(center);
  fill.position.copy(center).addScaledVector(dir, 600).addScaledVector(right, 900).addScaledVector(up, -300);
  fill.target.position.copy(center);
}

function currentBox() {
  const b = new THREE.Box3();
  for (const g of Object.values(groups)) if (g.visible) b.expandByObject(g);
  return b.isEmpty() ? allBox : b;
}

// 状态：爆炸系数、各零件的位移与转动、显示与隐藏
function applyState(st) {
  const f = st.explode ?? S.explode ?? 0;
  for (const [name, g] of Object.entries(groups)) {
    const ps = (st.parts || {})[name] || {};
    g.position.copy(g.userData.explode).multiplyScalar(f);
    if (ps.move) g.position.add(new THREE.Vector3(...ps.move));
    g.rotation.set(0, 0, 0);
    if (ps.rot) {                          // [轴 x,y,z, 角度°, 绕的点 x,y,z]
      const [ax, ay, az, deg, px = 0, py = 0, pz = 0] = ps.rot;
      const q = new THREE.Quaternion().setFromAxisAngle(new THREE.Vector3(ax, ay, az).normalize(), deg * Math.PI / 180);
      const pivot = new THREE.Vector3(px, py, pz);
      g.quaternion.copy(q);
      const off = pivot.clone().sub(pivot.clone().applyQuaternion(q));
      g.position.add(off);
    }
    g.visible = ps.visible ?? true;
    if (ps.opacity !== undefined) g.children[0].material.forEach?.((m) => { m.transparent = ps.opacity < 1; m.opacity = ps.opacity; });
  }
}

function project(p) {
  const v = new THREE.Vector3(...p).project(cam);
  return [(v.x + 1) / 2 * W, (1 - v.y) / 2 * H];
}

function el(tag, attrs, text) {
  const e = document.createElementNS(svgNS, tag);
  for (const [k, v] of Object.entries(attrs)) e.setAttribute(k, v);
  if (text !== undefined) e.textContent = text;
  ov.appendChild(e);
  return e;
}

const FONT = "Noto Sans CJK SC, Noto Sans SC, sans-serif";
function arrowHead(x, y, ang, color, size = 9) {
  const a1 = ang + Math.PI * 0.88, a2 = ang - Math.PI * 0.88;
  el("path", { d: `M${x},${y} L${x + size * Math.cos(a1)},${y + size * Math.sin(a1)} L${x + size * Math.cos(a2)},${y + size * Math.sin(a2)} Z`, fill: color });
}

function overlay(st) {
  while (ov.firstChild) ov.removeChild(ov.firstChild);
  const fs = st.fontSize ?? S.fontSize ?? 15;
  // 尺寸：a、b 两点，off 是尺寸线相对 a、b 的偏移（三维，mm）
  for (const d of st.dims || []) {
    const off = d.off || [0, 0, 0];
    const a = project(d.a), b = project(d.b);
    const a2 = project(d.a.map((v, i) => v + off[i])), b2 = project(d.b.map((v, i) => v + off[i]));
    const col = d.color || "#1d2327";
    el("line", { x1: a[0], y1: a[1], x2: a2[0], y2: a2[1], stroke: col, "stroke-width": 0.9 });
    el("line", { x1: b[0], y1: b[1], x2: b2[0], y2: b2[1], stroke: col, "stroke-width": 0.9 });
    el("line", { x1: a2[0], y1: a2[1], x2: b2[0], y2: b2[1], stroke: col, "stroke-width": 1.1 });
    const ang = Math.atan2(b2[1] - a2[1], b2[0] - a2[0]);
    arrowHead(b2[0], b2[1], ang, col); arrowHead(a2[0], a2[1], ang + Math.PI, col);
    const mx = (a2[0] + b2[0]) / 2, my = (a2[1] + b2[1]) / 2;
    let rot = ang * 180 / Math.PI; if (rot > 90) rot -= 180; if (rot < -90) rot += 180;
    const t = el("text", { x: mx, y: my - 5, "font-size": d.fontSize || fs, "font-family": FONT, fill: col, "text-anchor": "middle",
      transform: `rotate(${rot} ${mx} ${my})`, "paint-order": "stroke", stroke: "#fff", "stroke-width": 3.5 }, d.text);
  }
  // 箭头（力、运动方向）：from → to（三维点），或 at + dir + len
  for (const ar of st.arrows || []) {
    const p0 = project(ar.from), p1 = project(ar.to);
    const col = ar.color || "#c0504d";
    el("line", { x1: p0[0], y1: p0[1], x2: p1[0], y2: p1[1], stroke: col, "stroke-width": ar.width || 3 });
    arrowHead(p1[0], p1[1], Math.atan2(p1[1] - p0[1], p1[0] - p0[0]), col, ar.head || 14);
    if (ar.text) {
      const at = ar.textAt === "end" ? p1 : p0;
      el("text", { x: at[0] + (ar.dx ?? 6), y: at[1] + (ar.dy ?? -6), "font-size": ar.fontSize || fs, "font-family": FONT, fill: col,
        "text-anchor": ar.anchor || "start", "paint-order": "stroke", stroke: "#fff", "stroke-width": 3.5 }, ar.text);
    }
  }
  // 点（定位支承点等）
  for (const pt of st.points || []) {
    const p = project(pt.at);
    el("circle", { cx: p[0], cy: p[1], r: pt.r || 5, fill: pt.color || "#4f7fb8", stroke: "#fff", "stroke-width": 1.5 });
    if (pt.text) el("text", { x: p[0] + (pt.dx ?? 8), y: p[1] + (pt.dy ?? -8), "font-size": pt.fontSize || fs, "font-family": FONT,
      fill: pt.color || "#4f7fb8", "paint-order": "stroke", stroke: "#fff", "stroke-width": 3.5, "text-anchor": pt.anchor || "start" }, pt.text);
  }
  // 零件序号与文字标注：at 是三维点；pos 是标注位置（相对图宽高的比例 [0–1, 0–1]），不给时自动放在左右两侧
  const labels = (st.labels || []).map((l) => ({ ...l, p: project(l.at) }));
  // 遮挡检查：标注点被别的零件挡住（射线先碰到别的零件）就记下来，程序会报出来
  window.MISSES = [];
  const meshes = [];
  for (const [name, g] of Object.entries(groups)) if (g.visible) for (const c of g.children) if (c.isMesh && !c.userData.outline) meshes.push([c, name]);
  const ray = new THREE.Raycaster();
  for (const l of labels) {
    const P = new THREE.Vector3(...l.at);
    const dirv = new THREE.Vector3().subVectors(P, cam.position).normalize();
    ray.set(cam.position.clone(), dirv);
    const hits = ray.intersectObjects(meshes.map((m) => m[0]), false);
    if (!hits.length) continue;
    const first = hits[0];
    const dist = cam.position.distanceTo(P);
    const owner = meshes.find((m) => m[0] === first.object)[1];
    if (l.part && !owner.startsWith(l.part)) {
      // 被挡住：在这个零件上找离指示点最近、看得见的一点（三角形重心），把引线指到那里
      const cand = [];
      for (const [m, name] of meshes) {
        if (!name.startsWith(l.part)) continue;
        const pos = m.geometry.attributes.position, idx = m.geometry.index;
        const n = idx ? idx.count : pos.count;
        for (let k = 0; k < n; k += 3) {
          const ia = idx ? idx.getX(k) : k, ib = idx ? idx.getX(k + 1) : k + 1, ic = idx ? idx.getX(k + 2) : k + 2;
          const c = new THREE.Vector3((pos.getX(ia) + pos.getX(ib) + pos.getX(ic)) / 3, (pos.getY(ia) + pos.getY(ib) + pos.getY(ic)) / 3,
            (pos.getZ(ia) + pos.getZ(ib) + pos.getZ(ic)) / 3).applyMatrix4(m.matrixWorld);
          cand.push([c.distanceTo(P), c]);
        }
      }
      cand.sort((u, v) => u[0] - v[0]);
      let found = null;
      for (const [, c] of cand.slice(0, 1500)) {
        const dv = new THREE.Vector3().subVectors(c, cam.position).normalize();
        ray.set(cam.position.clone(), dv);
        const h = ray.intersectObjects(meshes.map((m) => m[0]), false);
        if (h.length && meshes.find((m) => m[0] === h[0].object)[1].startsWith(l.part) && Math.abs(h[0].distance - cam.position.distanceTo(c)) < 0.5) { found = c; break; }
      }
      if (found) { l.at = [found.x, found.y, found.z]; l.p = project(l.at); }
      else window.MISSES.push([l.text, owner]);
    }
  }
  const auto = labels.filter((l) => !l.pos);
  const left = auto.filter((l) => (l.side || (l.p[0] < W / 2 ? "left" : "right")) === "left").sort((a, b) => a.p[1] - b.p[1]);
  const right = auto.filter((l) => !left.includes(l)).sort((a, b) => a.p[1] - b.p[1]);
  const place = (arr, x) => {
    const gap = (st.labelGap ?? 34);
    let y = -Infinity;
    for (const l of arr) { y = Math.max(l.p[1], y + gap); l.q = [x, y]; }
    const over = y - (H - 20);             // 太靠下时整体上移
    if (over > 0) for (const l of arr) l.q[1] -= over;
  };
  place(left, (st.labelX ?? 0.06) * W); place(right, (1 - (st.labelX ?? 0.06)) * W);
  for (const l of labels) {
    const q = l.pos ? [l.pos[0] * W, l.pos[1] * H] : l.q;
    const col = l.color || "#1d2327";
    const balloon = l.style !== "text";
    const r = balloon ? (l.r || 13) : 0;
    const dx = l.p[0] - q[0], dy = l.p[1] - q[1], dl = Math.hypot(dx, dy) || 1;
    el("line", { x1: q[0] + dx / dl * r, y1: q[1] + dy / dl * r, x2: l.p[0], y2: l.p[1], stroke: col, "stroke-width": 0.9 });
    el("circle", { cx: l.p[0], cy: l.p[1], r: 2.3, fill: col });
    if (balloon) {
      el("circle", { cx: q[0], cy: q[1], r, fill: "#fff", stroke: col, "stroke-width": 1.2 });
      el("text", { x: q[0], y: q[1] + fs * 0.36, "font-size": fs, "font-family": FONT, fill: col, "text-anchor": "middle" }, l.text);
    } else {
      const anchor = l.anchor || (q[0] < l.p[0] ? "end" : "start");
      el("text", { x: q[0] + (anchor === "end" ? -4 : 4), y: q[1] + fs * 0.36, "font-size": l.fontSize || fs, "font-family": FONT, fill: col,
        "text-anchor": anchor, "paint-order": "stroke", stroke: "#fff", "stroke-width": 3.5 }, l.text);
    }
  }
  for (const t of st.texts || []) {                    // 固定位置的文字（标题、说明），pos 为比例
    el("text", { x: t.pos[0] * W, y: t.pos[1] * H, "font-size": t.fontSize || fs, "font-family": FONT, fill: t.color || "#1d2327",
      "text-anchor": t.anchor || "start", "font-weight": t.bold ? 700 : 400, "paint-order": "stroke", stroke: "#fff", "stroke-width": 3 }, t.text);
  }
}

function frame(st) {
  applyState(st);
  setCamera(st.camera || S.camera || {});
  renderer.render(scene, cam);
  overlay(st);
}

window.frame = (st) => { frame(st); return true; };
frame(S.state || {});
window.READY = true;
