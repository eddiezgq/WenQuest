// WenQuest virtual machines for PLC labs (第 18 轮 〔VP〕): the machine model (I/O, physics, faults) and its 3D view.
//
// Each machine is a factory WQPLANTS.<name>(options) returning a plant for WQ.lab({view: "plc", plant}):
//   io        the machine's I/O table (as on the real machine's wiring diagram): use it as plc.io
//   panel     the operator panel (push buttons, NC buttons, switches)
//   faults    faults the student (or a test) can inject
//   reset(s, {faults, seed}), inputs(s) -> {name: value}, step(dt_ms, outputs, s), read(s, name)
//   build3d(st, THREE) -> view; draw3d(view, s, io): the 3D picture (three.js primitives, no network)
// The physics is deliberately simple (kinematics, first-order lags) but it has the things a commissioning engineer
// meets: sensor bounce, travel times, limit switches, analogue noise, stuck sensors, jammed cylinders, broken wires.
// A machine also reports hazards (read(s, "hazard")): a test can demand { never: { hazard: true } }.
(function (root) {
"use strict";

// ---------------------------------------------------------------- helpers
function rng(seed) {   // mulberry32, the same in every browser
  let a = (seed >>> 0) || 1;
  return () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));
const approach = (x, target, rate, dt) => (x < target ? Math.min(target, x + rate * dt) : Math.max(target, x - rate * dt));
// a bouncing contact: after a change the reading chatters for `ms` (the reason for input filters, Ch. 3 and 6)
function bounce(s, key, v, now, ms) {
  const b = s._b || (s._b = {});
  const c = b[key] || (b[key] = { v, t: -1e9 });
  if (c.v !== v) { c.v = v; c.t = now; }
  if (ms > 0 && now - c.t < ms) return Math.floor((now - c.t) / 2) % 2 === 0 ? v : !v;
  return v;
}

// 3D building blocks
function kit3d(st, THREE) {
  const mats = {};
  const mat = (color, opts = {}) => {
    const k = color + JSON.stringify(opts);
    return mats[k] || (mats[k] = new THREE.MeshStandardMaterial(Object.assign({ color, roughness: 0.6, metalness: 0.1 }, opts)));
  };
  const add = (obj, parent) => { obj.castShadow = true; obj.receiveShadow = true; (parent || st.scene).add(obj); return obj; };
  const box = (w, h, d, color, x, y, z, parent) => { const m = add(new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat(color)), parent); m.position.set(x, y, z); return m; };
  const cyl = (r, h, color, x, y, z, parent, axis) => {
    const m = add(new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, 24), mat(color)), parent);
    if (axis === "x") m.rotation.z = Math.PI / 2; if (axis === "z") m.rotation.x = Math.PI / 2;
    m.position.set(x, y, z); return m;
  };
  const lamp = (r, color, x, y, z, parent) => {
    const m = add(new THREE.Mesh(new THREE.SphereGeometry(r, 20, 14), new THREE.MeshStandardMaterial({ color: 0x333333, emissive: color, emissiveIntensity: 0, roughness: 0.3 })), parent);
    m.position.set(x, y, z); m.userData.on = (v) => { m.material.emissiveIntensity = v ? 1.6 : 0; m.material.color.setHex(v ? color : 0x333333); };
    return m;
  };
  const label = (text, x, y, z, size = 0.12, parent) => {
    const c = document.createElement("canvas"); c.width = 256; c.height = 64;
    const g = c.getContext("2d"); g.font = "bold 34px system-ui, sans-serif"; g.textAlign = "center"; g.textBaseline = "middle";
    g.fillStyle = "rgba(255,255,255,0.85)"; g.fillRect(0, 8, 256, 48); g.fillStyle = "#1f2a33"; g.fillText(text, 128, 33);
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map: new THREE.CanvasTexture(c), depthTest: false }));
    sp.scale.set(size * 4, size, 1); sp.position.set(x, y, z); sp.renderOrder = 10;
    (parent || st.scene).add(sp); return sp;
  };
  const beam = (from, to, color) => {
    const g = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(...from), new THREE.Vector3(...to)]);
    const l = new THREE.Line(g, new THREE.LineDashedMaterial({ color, dashSize: 0.03, gapSize: 0.02 }));
    l.computeLineDistances(); st.scene.add(l);
    l.userData.on = (v) => { l.material.color.setHex(v ? 0xd1242f : 0x9aa7b0); };
    return l;
  };
  const camera = (pos, target) => { st.camera.position.set(...pos); st.camera.lookAt(new THREE.Vector3(...target)); st.target = target; };
  return { mat, box, cyl, lamp, label, beam, camera };
}

// ---------------------------------------------------------------- 1. traffic light (crossroads)
// Outputs: NS_R/Y/G, EW_R/Y/G (north–south, east–west lamps), P_Wait (pedestrian "wait" lamp); inputs: S_Ped (request),
// S_Night (night mode switch). Hazard: both directions show green or yellow at the same time.
function traffic(o = {}) {
  const io = [
    { name: "S_Ped", addr: "%IX0.0", dir: "in", comment: ["行人过街请求按钮", "Pedestrian request button"] },
    { name: "S_Night", addr: "%IX0.1", dir: "in", comment: ["夜间模式开关", "Night mode switch"] },
    { name: "NS_R", addr: "%QX0.0", dir: "out", comment: ["南北红灯", "North–south red"] },
    { name: "NS_Y", addr: "%QX0.1", dir: "out", comment: ["南北黄灯", "North–south yellow"] },
    { name: "NS_G", addr: "%QX0.2", dir: "out", comment: ["南北绿灯", "North–south green"] },
    { name: "EW_R", addr: "%QX0.3", dir: "out", comment: ["东西红灯", "East–west red"] },
    { name: "EW_Y", addr: "%QX0.4", dir: "out", comment: ["东西黄灯", "East–west yellow"] },
    { name: "EW_G", addr: "%QX0.5", dir: "out", comment: ["东西绿灯", "East–west green"] },
    { name: "P_Wait", addr: "%QX0.6", dir: "out", comment: ["行人“请等待”指示灯", "Pedestrian 'wait' lamp"] },
  ];
  const go = (out, d) => out[d + "_G"] || out[d + "_Y"];
  return {
    io,
    panel: [{ name: "S_Ped", kind: "push", label: ["行人请求", "Pedestrian"] }, { name: "S_Night", kind: "switch", label: ["夜间模式", "Night mode"] }],
    faults: [{ id: "lampNS", name: ["南北绿灯烧坏", "NS green lamp burnt out"] }],
    reset(s, opt) {
      s.f = (opt && opt.faults) || {}; s.t = 0; s.hazard = false; s.out = {};
      s.cars = [{ d: "NS", x: -6 }, { d: "NS", x: -12 }, { d: "EW", x: -5 }, { d: "EW", x: -10.5 }];
      s.lightNS = "off"; s.lightEW = "off"; s.yellowTime = 0;
    },
    inputs() { return {}; },
    step(dt, out, s) {
      s.t += dt; s.out = out;
      if (go(out, "NS") && go(out, "EW")) s.hazard = true;
      const ns = out.NS_G && !s.f.lampNS ? "G" : out.NS_Y ? "Y" : out.NS_R ? "R" : "off";
      const ew = out.EW_G ? "G" : out.EW_Y ? "Y" : out.EW_R ? "R" : "off";
      s.lightNS = ns; s.lightEW = ew;
      // cars: drive at 6 m/s, stop before the stop line (x = -2.5) unless green; leave and come back
      for (const c of s.cars) {
        const light = c.d === "NS" ? ns : ew;
        const ahead = s.cars.filter((k) => k.d === c.d && k.x > c.x).reduce((m, k) => Math.min(m, k.x), 1e9);
        let v = 6;
        if (c.x < -2.5 && c.x > -4.5 && light !== "G") v = 0;
        if (ahead - c.x < 4) v = 0;
        c.x += v * dt / 1000;
        if (c.x > 12) c.x -= 24;
      }
    },
    read(s, n) { if (n === "hazard") return s.hazard; return undefined; },
    build3d(st, THREE) {
      const K = kit3d(st, THREE);
      K.box(30, 0.02, 4, 0x55606a, 0, 0.01, 0); K.box(4, 0.021, 30, 0x55606a, 0, 0.011, 0);
      for (let k = -14; k < 14; k += 2) { K.box(1, 0.025, 0.1, 0xffffff, k + 0.5, 0.012, 0); K.box(0.1, 0.026, 1, 0xffffff, 0, 0.013, k + 0.5); }
      const head = (x, z, rot, name) => {
        const g = new THREE.Group(); g.position.set(x, 0, z); g.rotation.y = rot; st.scene.add(g);
        K.cyl(0.06, 3, 0x30363d, 0, 1.5, 0, g); K.box(0.35, 1.0, 0.3, 0x24292f, 0, 3.0, 0, g);
        const r = K.lamp(0.11, 0xff3b30, 0, 3.32, 0.16, g), y = K.lamp(0.11, 0xffb000, 0, 3.0, 0.16, g), gr = K.lamp(0.11, 0x2ecc71, 0, 2.68, 0.16, g);
        K.label(name, 0, 3.8, 0, 0.6, g);
        return { r, y, g: gr };
      };
      const v = { ns: head(2.4, 2.4, 0, "NS"), ew: head(-2.4, 2.4, Math.PI / 2, "EW"), cars: [], K };
      v.wait = K.lamp(0.12, 0xffb000, 2.6, 1.2, -2.6);
      K.label("P", 2.6, 1.6, -2.6, 0.45);
      for (let k = 0; k < 4; k++) v.cars.push(K.box(1.8, 0.8, 0.9, [0x1f6feb, 0xc2570c, 0x8250df, 0x1a7f37][k], 0, 0.5, 0));
      K.camera([11, 10, 13], [0, 0.5, 0]);
      return v;
    },
    draw3d(v, s) {
      const o = s.out || {};
      v.ns.r.userData.on(o.NS_R); v.ns.y.userData.on(o.NS_Y); v.ns.g.userData.on(o.NS_G && !(s.f || {}).lampNS);
      v.ew.r.userData.on(o.EW_R); v.ew.y.userData.on(o.EW_Y); v.ew.g.userData.on(o.EW_G);
      v.wait.userData.on(o.P_Wait);
      (s.cars || []).forEach((c, k) => {
        const m = v.cars[k];
        if (c.d === "NS") { m.position.set(1, 0.5, -c.x); m.rotation.y = Math.PI / 2; } else { m.position.set(c.x, 0.5, -1); m.rotation.y = 0; }
      });
    },
  };
}

// ---------------------------------------------------------------- 2. three-floor elevator
// Inputs: floor sensors B_F1..B_F3 (flags at each floor), limit switches S_LowLim / S_TopLim (NC: FALSE = hit), call
// buttons S_C1..S_C3, door sensors B_DoorOpen / B_DoorClosed. Outputs: K_Up, K_Down (hoist contactors), Y_DoorOpen,
// Y_DoorClose, H_C1..H_C3 (call lamps). Hazards: both contactors on; moving with the door open; overtravel.
function elevator(o = {}) {
  const io = [
    { name: "B_F1", addr: "%IX0.0", dir: "in", comment: ["1 楼平层传感器", "Floor 1 level sensor"] },
    { name: "B_F2", addr: "%IX0.1", dir: "in", comment: ["2 楼平层传感器", "Floor 2 level sensor"] },
    { name: "B_F3", addr: "%IX0.2", dir: "in", comment: ["3 楼平层传感器", "Floor 3 level sensor"] },
    { name: "S_LowLim", addr: "%IX0.3", dir: "in", comment: ["下极限开关（常闭）", "Bottom limit (NC)"] },
    { name: "S_TopLim", addr: "%IX0.4", dir: "in", comment: ["上极限开关（常闭）", "Top limit (NC)"] },
    { name: "S_C1", addr: "%IX0.5", dir: "in", comment: ["1 楼呼梯按钮", "Call button floor 1"] },
    { name: "S_C2", addr: "%IX0.6", dir: "in", comment: ["2 楼呼梯按钮", "Call button floor 2"] },
    { name: "S_C3", addr: "%IX0.7", dir: "in", comment: ["3 楼呼梯按钮", "Call button floor 3"] },
    { name: "B_DoorOpen", addr: "%IX1.0", dir: "in", comment: ["门开到位", "Door fully open"] },
    { name: "B_DoorClosed", addr: "%IX1.1", dir: "in", comment: ["门关到位", "Door fully closed"] },
    { name: "K_Up", addr: "%QX0.0", dir: "out", comment: ["上行接触器", "Hoist up contactor"] },
    { name: "K_Down", addr: "%QX0.1", dir: "out", comment: ["下行接触器", "Hoist down contactor"] },
    { name: "Y_DoorOpen", addr: "%QX0.2", dir: "out", comment: ["开门", "Open door"] },
    { name: "Y_DoorClose", addr: "%QX0.3", dir: "out", comment: ["关门", "Close door"] },
    { name: "H_C1", addr: "%QX0.4", dir: "out", comment: ["1 楼呼梯指示", "Call lamp floor 1"] },
    { name: "H_C2", addr: "%QX0.5", dir: "out", comment: ["2 楼呼梯指示", "Call lamp floor 2"] },
    { name: "H_C3", addr: "%QX0.6", dir: "out", comment: ["3 楼呼梯指示", "Call lamp floor 3"] },
  ];
  const H = 3.0, SPEED = 1.0, FLAG = 0.04;   // floor height m, car speed m/s, half-length of a level flag m
  return {
    io,
    panel: [1, 2, 3].map((k) => ({ name: "S_C" + k, kind: "push", label: [`${k} 楼呼梯`, `Call ${k}`] })),
    faults: [{ id: "f2dead", name: ["2 楼平层传感器坏（常为 0）", "Floor-2 sensor dead (always 0)"] },
             { id: "doorJam", name: ["门卡住（关不上）", "Door jammed (will not close)"] }],
    reset(s, opt) {
      s.f = (opt && opt.faults) || {}; s.t = 0; s.z = (o.startFloor || 1) * H - H; s.v = 0; s.door = 1; s.hazard = false; s.why = ""; s.out = {};
      s.trips = 0; s.lastFloor = Math.round(s.z / H) + 1;
    },
    inputs(s) {
      const at = (k) => Math.abs(s.z - (k - 1) * H) <= FLAG;
      return {
        B_F1: at(1), B_F2: at(2) && !s.f.f2dead, B_F3: at(3),
        S_LowLim: s.z > -0.15, S_TopLim: s.z < 2 * H + 0.15,
        B_DoorOpen: s.door >= 0.99, B_DoorClosed: s.door <= 0.01,
      };
    },
    step(dt, out, s) {
      s.t += dt; s.out = out;
      const sec = dt / 1000;
      if (out.K_Up && out.K_Down) { s.hazard = true; s.why = "both"; }
      const target = out.K_Up && !out.K_Down ? SPEED : out.K_Down && !out.K_Up ? -SPEED : 0;
      // motoring: 2.5 m/s² up to speed; contactor off: the brake drops and stops the car within about 1 cm
      s.v = approach(s.v, target, target === 0 || Math.sign(target) !== Math.sign(s.v) ? 60 : 2.5, sec);
      s.z += s.v * sec;
      if (Math.abs(s.v) > 0.02 && s.door > 0.05) { s.hazard = true; s.why = "door"; }
      if (s.z < -0.3 || s.z > 2 * H + 0.3) { s.hazard = true; s.why = "overtravel"; s.z = clamp(s.z, -0.3, 2 * H + 0.3); s.v = 0; }
      const dTarget = out.Y_DoorOpen && !out.Y_DoorClose ? 1 : out.Y_DoorClose && !out.Y_DoorOpen && !s.f.doorJam ? 0 : s.door;
      s.door = approach(s.door, dTarget, 1 / 1.5, sec);   // 1.5 s to open or close
      if (s.f.doorJam && out.Y_DoorClose) s.door = Math.max(s.door, 0.3);
      const fl = Math.round(s.z / H) + 1;
      if (Math.abs(s.z - (fl - 1) * H) <= FLAG && Math.abs(s.v) < 0.05 && fl !== s.lastFloor) { s.trips++; s.lastFloor = fl; }
    },
    read(s, n) {
      if (n === "hazard") return s.hazard;
      if (n === "floor") { const fl = Math.round(s.z / H) + 1; return Math.abs(s.z - (fl - 1) * H) <= FLAG ? fl : 0; }
      if (n === "z") return s.z;
      if (n === "door") return s.door;
      if (n === "trips") return s.trips;
      return undefined;
    },
    build3d(st, THREE) {
      const K = kit3d(st, THREE);
      const v = { K };
      K.box(2.4, 0.1, 2.4, 0x8c959f, 0, 0.05, 0);
      for (const x of [-1.15, 1.15]) for (const z of [-1.15, 1.15]) K.box(0.08, 3 * H + 0.6, 0.08, 0x57606a, x, (3 * H + 0.6) / 2, z);
      for (let k = 0; k < 3; k++) {
        K.box(2.4, 0.06, 0.5, 0xd0d7de, 0, k * H, 1.45);
        K.label(`${k + 1}F`, -1.7, k * H + 0.6, 1.2, 0.5);
        v["lamp" + (k + 1)] = K.lamp(0.07, 0xffb000, 1.45, k * H + 1.1, 1.25);
        v["flag" + (k + 1)] = K.box(0.05, 0.08, 0.05, 0x1a7f37, 1.05, k * H + 0.2, -1.0);
      }
      v.car = new THREE.Group(); st.scene.add(v.car);
      K.box(1.8, 0.08, 1.8, 0x6e7781, 0, 0, 0, v.car); K.box(1.8, 0.08, 1.8, 0x6e7781, 0, 2.2, 0, v.car);
      K.box(0.06, 2.2, 1.8, 0xafb8c1, -0.9, 1.1, 0, v.car); K.box(0.06, 2.2, 1.8, 0xafb8c1, 0.9, 1.1, 0, v.car); K.box(1.8, 2.2, 0.06, 0xafb8c1, 0, 1.1, -0.9, v.car);
      v.doorL = K.box(0.9, 2.1, 0.05, 0x8ea8c3, -0.45, 1.1, 0.92, v.car); v.doorR = K.box(0.9, 2.1, 0.05, 0x8ea8c3, 0.45, 1.1, 0.92, v.car);
      v.sensor = K.box(0.1, 0.1, 0.1, 0x24292f, 1.0, 0.2, -0.95, v.car);
      v.rope = K.cyl(0.015, 1, 0x24292f, 0, 0, 0);
      v.motor = K.cyl(0.35, 0.5, 0x6e7781, 0, 3 * H + 0.75, 0, null, "x");
      K.camera([12, 8, 15], [0, 4.2, 0]);
      return v;
    },
    draw3d(v, s) {
      const z = s.z || 0, o = s.out || {};
      v.car.position.set(0, z + 0.04, 0);
      const open = (s.door || 0) * 0.85;
      v.doorL.position.x = -0.45 - open; v.doorR.position.x = 0.45 + open;
      const top = 3 * H + 0.5, len = top - (z + 2.25);
      v.rope.scale.y = Math.max(0.01, len); v.rope.position.set(0, z + 2.25 + len / 2, 0);
      v.motor.material = v.K.mat(o.K_Up || o.K_Down ? 0x2da44e : 0x6e7781);
      for (let k = 1; k <= 3; k++) v["lamp" + k].userData.on(o["H_C" + k]);
    },
  };
}

// ---------------------------------------------------------------- 3. sorting conveyor (the digital factory's finished-part sorter)
// Parts arrive at the entry; a color sensor (red/blue), an inductive sensor (metal) and a height sensor (tall) look at
// them on the way; three pushers put metal parts into bin 1, red plastic into bin 2, blue plastic into bin 3; anything
// else runs off the end into the reject box. Inputs: B_Entry, B_Red, B_Metal, B_Tall, B_Y1Out/B_Y2Out/B_Y3Out (pusher
// extended), B_Y1In.. (retracted), B_End; outputs: M_Belt, Y1..Y3 (pushers, spring return), H_Full (bin full lamp).
function sorter(o = {}) {
  const io = [
    { name: "B_Entry", addr: "%IX0.0", dir: "in", comment: ["入口光电", "Entry photo sensor"] },
    { name: "B_Insp", addr: "%IX0.1", dir: "in", comment: ["检测工位到位光电", "Part at the inspection station"] },
    { name: "B_Red", addr: "%IX0.2", dir: "in", comment: ["颜色传感器（红）", "Colour sensor (red)"] },
    { name: "B_Metal", addr: "%IX0.3", dir: "in", comment: ["电感式传感器（金属）", "Inductive sensor (metal)"] },
    { name: "B_Tall", addr: "%IX1.6", dir: "in", comment: ["高度检测（高件）", "Height sensor (tall part)"] },
    { name: "B_P1", addr: "%IX0.4", dir: "in", comment: ["推杆 1 前光电", "Photo sensor at pusher 1"] },
    { name: "B_P2", addr: "%IX0.5", dir: "in", comment: ["推杆 2 前光电", "Photo sensor at pusher 2"] },
    { name: "B_P3", addr: "%IX0.6", dir: "in", comment: ["推杆 3 前光电", "Photo sensor at pusher 3"] },
    { name: "B_Y1Out", addr: "%IX1.0", dir: "in", comment: ["推杆 1 伸出到位", "Pusher 1 extended"] },
    { name: "B_Y2Out", addr: "%IX1.1", dir: "in", comment: ["推杆 2 伸出到位", "Pusher 2 extended"] },
    { name: "B_Y3Out", addr: "%IX1.2", dir: "in", comment: ["推杆 3 伸出到位", "Pusher 3 extended"] },
    { name: "B_End", addr: "%IX1.3", dir: "in", comment: ["末端光电（废品）", "End sensor (reject)"] },
    { name: "S_Start", addr: "%IX1.4", dir: "in", comment: ["启动按钮", "Start button"] },
    { name: "S_Stop", addr: "%IX1.5", dir: "in", comment: ["停止按钮（常闭）", "Stop button (NC)"] },
    { name: "M_Belt", addr: "%QX0.0", dir: "out", comment: ["输送带电机", "Belt motor"] },
    { name: "Y1", addr: "%QX0.1", dir: "out", comment: ["推杆 1 电磁阀", "Pusher 1 valve"] },
    { name: "Y2", addr: "%QX0.2", dir: "out", comment: ["推杆 2 电磁阀", "Pusher 2 valve"] },
    { name: "Y3", addr: "%QX0.3", dir: "out", comment: ["推杆 3 电磁阀", "Pusher 3 valve"] },
    { name: "H_Run", addr: "%QX0.4", dir: "out", comment: ["运行指示灯", "Running lamp"] },
  ];
  const L = 3.0, V = 0.2;                           // belt length m, speed m/s
  const POS = { entry: 0.15, insp: 0.7, p1: 1.4, p2: 1.9, p3: 2.4, end: 2.9 };   // the inspection sensors all look at x = 0.7 m
  const KINDS = { metal: { color: 0x8c959f, h: 0.06 }, red: { color: 0xd1242f, h: 0.06 }, blue: { color: 0x1f6feb, h: 0.06 }, tallred: { color: 0xd1242f, h: 0.11 } };
  const bin = { metal: 1, red: 2, blue: 3 };
  return {
    io,
    panel: [{ name: "S_Start", kind: "push", label: ["启动", "Start"] }, { name: "S_Stop", kind: "nc-push", label: ["停止", "Stop"] }],
    faults: [{ id: "y2stuck", name: ["推杆 2 卡住", "Pusher 2 stuck"] }, { id: "colorDirty", name: ["颜色传感器脏（漏检）", "Colour sensor dirty (misses)"] },
             { id: "bounce", name: ["入口光电抖动", "Entry sensor bounce"] }],
    reset(s, opt) {
      s.f = (opt && opt.faults) || {}; s.t = 0; s.out = {};
      s.rand = rng((opt && opt.seed) || o.seed || 7);
      s.seq = (o.sequence || ["metal", "red", "blue", "red", "tallred", "metal", "blue", "red"]).slice();
      s.parts = []; s.next = 1500; s.y = [0, 0, 0];
      s.bins = { 1: [], 2: [], 3: [], reject: [] }; s.wrong = 0; s.sorted = 0; s.hazard = false; s.spawned = 0;
    },
    inputs(s) {
      const near = (x, w = 0.04, pred = () => true) => s.parts.some((p) => !p.gone && Math.abs(p.x - x) < w && pred(p));
      const dirty = s.f.colorDirty && Math.floor(s.t / 1700) % 2 === 0;
      return {
        B_Entry: bounce(s, "entry", near(POS.entry, 0.05), s.t, s.f.bounce ? 40 : 0),
        B_Insp: near(POS.insp, 0.03),
        B_Red: !dirty && near(POS.insp, 0.05, (p) => p.kind === "red" || p.kind === "tallred"),
        B_Metal: near(POS.insp, 0.05, (p) => p.kind === "metal"),
        B_Tall: near(POS.insp, 0.05, (p) => KINDS[p.kind].h > 0.08),
        B_P1: near(POS.p1, 0.03), B_P2: near(POS.p2, 0.03), B_P3: near(POS.p3, 0.03),
        B_Y1Out: s.y[0] > 0.97, B_Y2Out: s.y[1] > 0.97, B_Y3Out: s.y[2] > 0.97,
        B_End: near(POS.end, 0.04),
      };
    },
    step(dt, out, s) {
      s.t += dt; s.out = out;
      const sec = dt / 1000;
      // parts arrive every 3 s while the belt runs and the entry is clear
      if (out.M_Belt) s.next -= dt;
      if (s.next <= 0 && s.seq.length && !s.parts.some((p) => !p.gone && p.x < 0.35)) {
        s.parts.push({ kind: s.seq.shift(), x: 0.0, z: 0, gone: false, id: ++s.spawned }); s.next = o.interval || 3000;
      }
      ["Y1", "Y2", "Y3"].forEach((k, i) => {
        const stuck = i === 1 && s.f.y2stuck;
        s.y[i] = approach(s.y[i], out[k] && !stuck ? 1 : 0, 1 / 0.25, sec);   // 0.25 s stroke, spring return
      });
      for (const p of s.parts) {
        if (p.gone) continue;
        // a pusher at its station moves the part sideways off the belt
        const st = [POS.p1, POS.p2, POS.p3].findIndex((x) => Math.abs(p.x - x) < 0.06);
        if (st >= 0 && s.y[st] > 0.2) { p.z = Math.max(p.z, s.y[st] * 0.45); }
        if (p.z >= 0.4) { p.gone = true; s.bins[st + 1].push(p.kind); s.sorted++; if (bin[p.kind.replace("tall", "")] !== st + 1 || p.kind === "tallred") s.wrong++; continue; }
        if (out.M_Belt && p.z < 0.05) p.x += V * sec;
        if (p.x >= L) { p.gone = true; s.bins.reject.push(p.kind); if (p.kind !== "tallred") s.wrong++; }
      }
      s.parts = s.parts.filter((p) => !p.gone);
    },
    read(s, n) {
      if (n === "hazard") return s.hazard;
      if (n === "wrong") return s.wrong;
      if (n === "sorted") return s.sorted;
      if (n === "bin1") return s.bins[1].length;
      if (n === "bin2") return s.bins[2].length;
      if (n === "bin3") return s.bins[3].length;
      if (n === "rejects") return s.bins.reject.length;
      if (n === "done") return !s.seq.length && !s.parts.some((p) => !p.gone);
      return undefined;
    },
    build3d(st, THREE) {
      const K = kit3d(st, THREE);
      const v = { K, parts: {} };
      K.box(L + 0.2, 0.06, 0.32, 0x2d333b, L / 2, 0.75, 0);
      for (const x of [0.1, L - 0.1]) K.cyl(0.04, 0.34, 0x8c959f, x, 0.78, 0, null, "z");
      for (const x of [0.2, L / 2, L - 0.2]) for (const z of [-0.14, 0.14]) K.box(0.05, 0.72, 0.05, 0x57606a, x, 0.36, z);
      const sensor = (x, name, color) => { K.box(0.06, 0.18, 0.06, 0x24292f, x, 0.9, -0.22); K.label(name, x, 1.15, -0.22, 0.11); return K.beam([x, 0.82, -0.2], [x, 0.82, 0.2], color); };
      K.box(0.3, 0.05, 0.4, 0x24292f, POS.insp, 1.25, 0); K.cyl(0.04, 0.1, 0xd1242f, POS.insp - 0.08, 1.18, 0); K.cyl(0.04, 0.1, 0x8c959f, POS.insp + 0.08, 1.18, 0);
      v.beams = { entry: sensor(POS.entry, "B_Entry"), insp: sensor(POS.insp, "B_Insp"),
        p1: sensor(POS.p1 - 0.12, "B_P1"), p2: sensor(POS.p2 - 0.12, "B_P2"), p3: sensor(POS.p3 - 0.12, "B_P3"), end: sensor(POS.end, "B_End") };
      v.push = [POS.p1, POS.p2, POS.p3].map((x, i) => {
        K.box(0.14, 0.1, 0.3, 0x6e7781, x, 0.85, -0.42);
        const rod = K.box(0.12, 0.08, 0.04, 0xe1e4e8, x, 0.83, -0.2);
        K.box(0.4, 0.3, 0.3, [0x8c959f, 0xd1242f, 0x1f6feb][i], x, 0.15, 0.45);
        K.label(`Y${i + 1} → ${i + 1}`, x, 0.45, 0.62, 0.12);
        return rod;
      });
      K.box(0.4, 0.3, 0.4, 0x24292f, L + 0.2, 0.15, 0); K.label("reject", L + 0.2, 0.45, 0.2, 0.12);
      v.run = K.lamp(0.05, 0x2ecc71, 0.1, 1.1, 0.3);
      K.camera([1.6, 2.6, 3.4], [1.5, 0.75, 0]);
      return v;
    },
    draw3d(v, s) {
      const ins = this.inputs(s);
      v.beams.entry.userData.on(ins.B_Entry); v.beams.insp.userData.on(ins.B_Insp); v.beams.p1.userData.on(ins.B_P1); v.beams.p2.userData.on(ins.B_P2); v.beams.p3.userData.on(ins.B_P3); v.beams.end.userData.on(ins.B_End);
      v.push.forEach((rod, i) => { rod.position.z = -0.2 + (s.y[i] || 0) * 0.35; });
      v.run.userData.on((s.out || {}).H_Run);
      const live = new Set();
      for (const p of s.parts || []) {
        if (p.gone) continue;
        live.add(p.id);
        let m = v.parts[p.id];
        if (!m) { const k = KINDS[p.kind]; m = v.parts[p.id] = v.K.cyl(0.07, k.h, k.color, 0, 0, 0); m.userData.h = k.h; }
        m.position.set(p.x, 0.78 + m.userData.h / 2, p.z);
      }
      for (const [id, m] of Object.entries(v.parts)) if (!live.has(+id)) { m.parent.remove(m); delete v.parts[id]; }
    },
  };
}

// ---------------------------------------------------------------- 4. press-fit station (bearing into the gearbox cover)
// The operator puts a part in the fixture (panel switch), presses both two-hand buttons; the PLC clamps, presses the
// bearing down while watching the force (analogue, %IW64, 0–27648 = 0–10 kN), then checks the end force window and
// shows OK or NOK. A light curtain (NC, safety) must stop the press. Inputs: B_Part, B_Clamped, B_Unclamped, B_PressUp,
// B_PressDown, S_Hand1, S_Hand2, S_LC (light curtain, NC), AI_Force; outputs: Y_Clamp, Y_PressDown, Y_PressUp, H_OK, H_NOK.
// Force at the bottom: about 5.6 kN for a good part (window 4–7 kN), 9.1 kN too tight, 2.1 kN too loose.
// Operating elements (Chapter 15): e-stop (NC), mode switch, reset/home, single step, manual clamp and ram jog; lamps
// Ready and Fault. The ram valve is a 5/3 closed-centre valve: with neither coil on, the ram stops where it is.
function press(o = {}) {
  const io = [
    { name: "B_Part", addr: "%IX0.0", dir: "in", comment: ["工件在位", "Part present"] },
    { name: "B_Clamped", addr: "%IX0.1", dir: "in", comment: ["夹紧到位", "Clamped"] },
    { name: "B_Unclamped", addr: "%IX0.2", dir: "in", comment: ["松开到位", "Unclamped"] },
    { name: "B_PressUp", addr: "%IX0.3", dir: "in", comment: ["压头上位", "Ram at top"] },
    { name: "B_PressDown", addr: "%IX0.4", dir: "in", comment: ["压头下位（压装到底）", "Ram at bottom (seated)"] },
    { name: "S_Hand1", addr: "%IX0.5", dir: "in", comment: ["双手按钮左", "Two-hand button left"] },
    { name: "S_Hand2", addr: "%IX0.6", dir: "in", comment: ["双手按钮右", "Two-hand button right"] },
    { name: "S_LC", addr: "%IX0.7", dir: "in", comment: ["安全光幕（常闭，挡光为 0）", "Light curtain (NC, 0 when broken)"] },
    { name: "AI_Force", addr: "%IW64", dir: "in", type: "INT", comment: ["压装力 0–27648 ↔ 0–10 kN", "Press force 0–27648 ↔ 0–10 kN"] },
    { name: "S_EStop", addr: "%IX1.0", dir: "in", comment: ["急停（常闭，按下为 0）", "Emergency stop (NC, 0 when pressed)"] },
    { name: "S_Auto", addr: "%IX1.1", dir: "in", comment: ["方式选择：1 自动 / 0 手动", "Mode switch: 1 auto / 0 manual"] },
    { name: "S_Reset", addr: "%IX1.2", dir: "in", comment: ["复位（回原点）按钮", "Reset (home) button"] },
    { name: "S_Step", addr: "%IX1.3", dir: "in", comment: ["单步按钮", "Single-step button"] },
    { name: "S_JogClamp", addr: "%IX1.4", dir: "in", comment: ["手动：夹紧／松开", "Manual: clamp / unclamp"] },
    { name: "S_JogDown", addr: "%IX1.5", dir: "in", comment: ["手动：压头下行（点动）", "Manual: ram down (jog)"] },
    { name: "S_JogUp", addr: "%IX1.6", dir: "in", comment: ["手动：压头上行（点动）", "Manual: ram up (jog)"] },
    { name: "Y_Clamp", addr: "%QX0.0", dir: "out", comment: ["夹紧气缸", "Clamp cylinder"] },
    { name: "Y_PressDown", addr: "%QX0.1", dir: "out", comment: ["压头下行", "Ram down"] },
    { name: "Y_PressUp", addr: "%QX0.2", dir: "out", comment: ["压头上行", "Ram up"] },
    { name: "H_OK", addr: "%QX0.3", dir: "out", comment: ["合格灯（绿）", "OK lamp (green)"] },
    { name: "H_NOK", addr: "%QX0.4", dir: "out", comment: ["不合格灯（红）", "NOK lamp (red)"] },
    { name: "H_Ready", addr: "%QX0.5", dir: "out", comment: ["就绪灯（白）：在原点、可以启动", "Ready lamp (white): at home, may start"] },
    { name: "H_Fault", addr: "%QX0.6", dir: "out", comment: ["故障灯（黄）", "Fault lamp (amber)"] },
  ];
  const STROKE = 0.12, CONTACT = 0.085, SPEED = 0.06;   // ram stroke m, where the bearing meets the bore, ram speed m/s
  return {
    io,
    panel: [{ name: "B_Part", kind: "switch", label: ["放上工件", "Load part"] }, { name: "S_Hand1", kind: "push", label: ["双手左", "Hand L"] },
            { name: "S_Hand2", kind: "push", label: ["双手右", "Hand R"] },
            { names: ["S_Hand1", "S_Hand2"], kind: "push", label: ["双手同时按住", "Both hands"] }, { name: "S_LC", kind: "nc-push", label: ["手伸进光幕", "Hand in curtain"] },
            { name: "S_EStop", kind: "estop", label: ["急停（再按一次释放）", "E-stop (press again to release)"] }, { name: "S_Auto", kind: "switch", label: ["自动", "Auto"] },
            { name: "S_Reset", kind: "push", label: ["复位", "Reset"] }, { name: "S_Step", kind: "push", label: ["单步", "Step"] },
            { name: "S_JogClamp", kind: "switch", label: ["手动夹紧", "Jog clamp"] }, { name: "S_JogDown", kind: "push", label: ["手动下", "Jog down"] },
            { name: "S_JogUp", kind: "push", label: ["手动上", "Jog up"] }],
    faults: [{ id: "tight", name: ["过盈太大（力超上限）", "Interference too large (force high)"] },
             { id: "loose", name: ["过盈太小（力不足）", "Interference too small (force low)"] },
             { id: "clampWire", name: ["夹紧到位传感器断线", "Clamp sensor wire broken"] },
             { id: "upStuck", name: ["压头上位开关粘连（常为 1）", "Ram-top switch stuck closed (always 1)"] }],
    reset(s, opt) {
      s.f = (opt && opt.faults) || {}; s.t = 0; s.out = {}; s.clamp = o.clamp0 || 0; s.ram = o.ram0 || 0; s.force = 0; s.hazard = false; s.seated = false;
      s.rand = rng((opt && opt.seed) || 11); s.part = false; s.panelLC = true; s.peak = 0;
    },
    inputs(s) {
      const kN = s.force + (s.rand() - 0.5) * 0.05;   // ±0.025 kN noise
      return {
        B_Clamped: s.clamp > 0.97 && !s.f.clampWire, B_Unclamped: s.clamp < 0.03,
        B_PressUp: s.ram < 0.002 || !!s.f.upStuck, B_PressDown: s.ram > STROKE - 0.002,
        AI_Force: Math.round(clamp(kN, 0, 10) / 10 * 27648),
        S_EStop: true, S_LC: true,      // NC safety contacts: closed (TRUE) unless the panel or a test opens them
      };
    },
    step(dt, out, s, ins) {
      s.t += dt; s.out = out;
      if (ins) { s.part = !!ins.B_Part; s.panelLC = ins.S_LC !== false; }
      const sec = dt / 1000;
      s.clamp = approach(s.clamp, out.Y_Clamp ? 1 : 0, 1 / 0.3, sec);
      const dir = out.Y_PressDown && !out.Y_PressUp ? 1 : out.Y_PressUp && !out.Y_PressDown ? -1 : 0;
      // the part must be clamped before the ram touches it; the light curtain (read from the panel) is a hazard check
      const lcOk = s.panelLC;
      if (ins && ins.S_EStop === false && dir !== 0) s.hazard = true;   // e-stop pressed but the ram still moves
      if (dir > 0 && !lcOk) { s.hazard = true; }
      if (dir > 0 && s.ram > 0.02 && s.clamp < 0.9) s.hazard = true;
      s.ram = clamp(s.ram + dir * SPEED * sec, 0, STROKE);
      // force: zero until contact, then the press-fit force grows with depth; a hard stop at the bottom
      const k = s.f.tight ? 260 : s.f.loose ? 60 : 160;   // kN per m of engagement
      if (s.ram > CONTACT && dir >= 0 && s.part) s.force = k * (s.ram - CONTACT);
      else if (dir < 0 || s.ram <= CONTACT) s.force = approach(s.force, 0, 40, sec);
      s.peak = Math.max(s.peak, s.force);
      if (s.ram >= STROKE - 0.002 && s.part) s.seated = true;
    },
    read(s, n) {
      if (n === "hazard") return s.hazard;
      if (n === "force") return s.force;
      if (n === "peak") return s.peak;
      if (n === "seated") return s.seated;
      return undefined;
    },
    build3d(st, THREE) {
      const K = kit3d(st, THREE);
      const v = { K };
      K.box(1.0, 0.8, 0.7, 0x57606a, 0, 0.4, 0);
      K.box(0.1, 1.2, 0.1, 0x6e7781, -0.35, 1.4, -0.2); K.box(0.1, 1.2, 0.1, 0x6e7781, 0.35, 1.4, -0.2);
      K.box(0.9, 0.15, 0.3, 0x6e7781, 0, 2.05, -0.1);
      K.cyl(0.08, 0.35, 0x8c959f, 0, 1.8, 0);
      v.ram = K.cyl(0.03, 0.4, 0xe1e4e8, 0, 1.45, 0);
      v.bearing = K.cyl(0.07, 0.03, 0xafb8c1, 0, 1.0, 0);
      v.part = K.box(0.36, 0.14, 0.36, 0x7d8590, 0, 0.87, 0);
      v.clampL = K.box(0.06, 0.1, 0.2, 0xc2570c, -0.35, 0.87, 0); v.clampR = K.box(0.06, 0.1, 0.2, 0xc2570c, 0.35, 0.87, 0);
      v.ok = K.lamp(0.05, 0x2ecc71, 0.45, 2.1, 0.1); v.nok = K.lamp(0.05, 0xff3b30, 0.6, 2.1, 0.1);
      v.curtain = [-0.45, 0.45].map((x) => K.box(0.04, 1.0, 0.04, 0xffb000, x, 1.3, 0.38));
      K.label("OK", 0.45, 1.95, 0.12, 0.09); K.label("NOK", 0.62, 1.85, 0.12, 0.09);
      K.camera([2.4, 2.3, 3.4], [0, 1.1, 0]);
      return v;
    },
    draw3d(v, s) {
      const o = s.out || {};
      const y = 1.45 - (s.ram || 0) * 3.2;
      v.ram.position.y = y;
      v.bearing.visible = !!s.part; v.part.visible = !!s.part;
      v.bearing.position.y = Math.max(0.95, Math.min(1.0, y - 0.21));
      const c = (s.clamp || 0) * 0.12;
      v.clampL.position.x = -0.35 + c; v.clampR.position.x = 0.35 - c;
      v.ok.userData.on(o.H_OK); v.nok.userData.on(o.H_NOK);
      v.curtain.forEach((b) => { b.material = v.K.mat(s.panelLC ? 0xffb000 : 0xd1242f); });
    },
  };
}

const API = { traffic, elevator, sorter, press, kit3d, rng };
if (typeof module !== "undefined" && module.exports) module.exports = API;
else root.WQPLANTS = API;
})(typeof window !== "undefined" ? window : globalThis);
