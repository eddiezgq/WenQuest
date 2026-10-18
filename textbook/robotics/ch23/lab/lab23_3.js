// 实验 23.3 陀螺力矩与进动（配 23.3 节，物理仿真）。浏览器里运行 MuJoCo 3.14.0，与书中程序 ex23_3.py 同一版本。
// 场景 1（机器人）：UR5e 手腕上的打磨电主轴（示意值）：砂轮看作 Ø100 mm、厚 20 mm、0.6 kg 的均匀圆盘，绕水平轴 y 自转；
//   支架（手腕）绕竖直轴 z 以 Ω 转动，扳动主轴的轴线。两根铰链都无摩擦、不加驱动，给定初速度后各自保持不变；
//   支架铰链上的 torque 传感器读出支架对转子的约束力矩，预测 |M| = I₃ ω Ω（式 (23.3.17)），方向沿支架的 x 轴（垂直于两根轴）。
// 场景 2（生活）：课堂演示用的陀螺仪（示意值）：均匀圆盘 1.0 kg、半径 0.15 m，盘心离支点 0.20 m，轴水平，用球铰支在支点上；
//   以 Ω = m𝔤l/(I₃ω)（式 (23.3.18)）开始进动。进动角速度由轴的方位角随时间的变化求得。
// 阈值由 ex23_3.py 用 Python 版 MuJoCo 核算：12000 r/min、Ω = 1 rad/s 时 0.9425 N·m，与公式相差 < 10⁻⁹；
// 陀螺仪自转 60、30 rad/s 时测得的进动 2.9067、5.8133 rad/s，与公式相差 < 10⁻⁴；不自转时 0.23 s 内倒到水平线下 60°。
WQ.lab({
  title: ["实验 23.3 陀螺力矩与进动", "Lab 23.3 Gyroscopic torque and precession"],
  goal: ["测量扳动高速转子所需的力矩，以及重力作用下陀螺仪的进动角速度，与 M = Ω × L 的预测比较。",
         "Measure the torque needed to turn a fast rotor and the precession rate of a gyroscope under gravity, and compare them with M = Ω × L."],
  view: "physics",
  scenes: [
    { id: "spindle", robot: true, name: ["手腕上的电主轴", "Spindle on the wrist"], hide: ["spin"],
      problem: { title: ["机器人问题：扳动高速旋转的电主轴", "Robot problem: turning a fast spindle"],
                 text: ["UR5e 手持打磨电主轴，砂轮高速旋转。手腕扳动主轴的轴线时，要承受多大的力矩？方向朝哪里？",
                        "The UR5e holds a grinding spindle whose wheel spins fast. When the wrist turns the spindle's axis, how large is the torque it must carry, and in which direction?"] } },
    { id: "top", name: ["演示陀螺仪", "Demonstration gyroscope"], hide: ["rpm", "Om", "dir"],
      problem: { title: ["生活中的例子：陀螺仪为什么不倒", "Everyday example: why the gyroscope does not fall"],
                 text: ["陀螺仪的轴一端支在支点上，另一端悬空。圆盘转着时它不倒，而是绕着支点慢慢转圈。转得越快，转圈越快还是越慢？",
                        "A gyroscope rests one end of its axle on a pivot. While the disc spins it does not fall but slowly circles the pivot. Does it circle faster or slower when the disc spins faster?"] } },
  ],
  params: [
    { id: "rpm", name: ["砂轮转速", "Wheel speed"], min: 2000, max: 15000, step: 500, value: 12000, unit: "r/min", digits: 0 },
    { id: "Om", name: ["手腕扳动的角速度 Ω", "Wrist turning rate Ω"], min: 0.2, max: 3, step: 0.1, value: 1, unit: "rad/s", digits: 1 },
    { id: "dir", name: ["砂轮转向：0 正转 / 1 反转", "Wheel direction: 0 forward / 1 reverse"], min: 0, max: 1, step: 1, value: 0, unit: "", digits: 0 },
    { id: "spin", name: ["陀螺仪的自转角速度 ω", "Gyroscope spin ω"], min: 0, max: 80, step: 1, value: 60, unit: "rad/s", digits: 0 },
  ],
  legend: [{ color: "#b8860b", name: ["主轴：陀螺力矩 |M| / 陀螺仪：进动角速度", "spindle: |M| / gyroscope: precession rate"] }, { color: "#9aa4ab", name: ["预测", "prediction"] }],
  physics: {
    camera: [35, 25, 0.5],
    xml(api) {
      if (api.scene === "spindle") {
        return `<mujoco><option timestep="0.0002" integrator="RK4"/><worldbody>
<geom type="cylinder" size="0.05 0.15" pos="0 0 0.3" rgba="0.72 0.80 0.86 1" contype="0" conaffinity="0"/>
<body name="wrist" pos="0 0 0.5"><joint name="turn" type="hinge" axis="0 0 1"/><site name="s"/>
<geom type="box" size="0.03 0.03 0.03" mass="0.5" rgba="0.36 0.42 0.45 1" contype="0" conaffinity="0"/>
<geom type="cylinder" size="0.02 0.06" pos="0 -0.06 0" quat="0.7071068 0.7071068 0 0" mass="0.000001" rgba="0.2 0.2 0.22 1" contype="0" conaffinity="0"/>
<body name="rotor"><joint name="spin" type="hinge" axis="0 1 0"/>
<geom type="cylinder" size="0.05 0.01" quat="0.7071068 0.7071068 0 0" mass="0.6" rgba="0.62 0.64 0.66 1" contype="0" conaffinity="0"/>
<geom type="box" size="0.045 0.0105 0.004" mass="0.000001" rgba="0.85 0.55 0.15 1" contype="0" conaffinity="0"/>
</body></body></worldbody><sensor><torque site="s"/></sensor></mujoco>`;
      }
      return `<mujoco><option timestep="0.0005" integrator="RK4"/><worldbody>
<geom type="cylinder" size="0.01 0.15" pos="0 0 0.85" rgba="0.36 0.42 0.45 1" contype="0" conaffinity="0"/>
<geom type="cylinder" size="0.12 0.01" pos="0 0 0.7" rgba="0.36 0.42 0.45 1" contype="0" conaffinity="0"/>
<body name="axle" pos="0 0 1"><joint name="pivot" type="ball"/>
<geom type="capsule" fromto="0 0 0 0.26 0 0" size="0.006" mass="0.000001" rgba="0.8 0.8 0.82 1" contype="0" conaffinity="0"/>
<body name="wheel" pos="0.2 0 0"><joint name="spin" type="hinge" axis="1 0 0"/>
<geom type="cylinder" size="0.15 0.01" quat="0.7071068 0 0.7071068 0" mass="1" rgba="0.35 0.6 0.85 0.85" contype="0" conaffinity="0"/>
<geom type="box" size="0.0105 0.14 0.006" mass="0.000001" rgba="0.85 0.55 0.15 1" contype="0" conaffinity="0"/>
</body></body></worldbody></mujoco>`;
    },
  },
  consts: { I3r: 0.5 * 0.6 * 0.05 * 0.05, m: 1.0, l: 0.2, I3w: 0.5 * 1.0 * 0.15 * 0.15, g: 9.81 },
  reset(api, s) {
    const c = this.consts, d = api.sim.d;
    s.hist = []; s.az0 = null; s.az = 0; s.rate = null; s.low = 0;
    if (api.scene === "spindle") {
      s.w = api.p.rpm * 2 * Math.PI / 60 * (api.p.dir ? -1 : 1);
      d.qvel[0] = api.p.Om; d.qvel[1] = s.w;
      s.pred = c.I3r * Math.abs(s.w) * api.p.Om;
    } else {
      const sp = api.p.spin;
      s.pred = sp > 0 ? c.m * c.g * c.l / (c.I3w * sp) : 0;
      d.qvel[2] = s.pred; d.qvel[3] = sp;                         // 球铰的角速度在轴的坐标系中，开始时轴沿 x、水平
    }
  },
  update(dt, api, s) {
    const d = api.sim.d;
    if (api.scene === "spindle") {
      const q = d.sensordata;
      s.M = Math.hypot(q[0], q[1], q[2]); s.Mx = q[0];
      s.hist.push([d.time, s.M]);
      if (d.time > 0.2 && Math.abs(s.M / s.pred - 1) < 0.01) {
        if (!api.p.dir) api.done("gyro");
        else if (s.Mx > 0) api.done("reverse");
      }
      if (d.time >= 1.0) api.stop();
    } else {
      const R = d.xmat, ax = [R[9], R[12], R[15]];                // axle 的 x 轴在世界坐标系中的方向
      let az = Math.atan2(ax[1], ax[0]);
      if (s.az0 === null) { s.az0 = az; s.azp = az; s.az = 0; s.t0 = d.time; }
      let da = az - s.azp; if (da > Math.PI) da -= 2 * Math.PI; if (da < -Math.PI) da += 2 * Math.PI;
      s.az += da; s.azp = az;
      s.elev = Math.asin(Math.max(-1, Math.min(1, ax[2]))) * 180 / Math.PI;
      s.low = Math.min(s.low, s.elev);
      if (d.time - s.t0 > 0.2) s.rate = s.az / (d.time - s.t0);
      s.hist.push([d.time, s.rate || 0]);
      if (d.time >= 1.0 && api.p.spin >= 20 && Math.abs(s.rate / s.pred - 1) < 0.01) api.done("prec");
      if (d.time >= 1.0 && api.p.spin >= 29 && api.p.spin <= 31 && Math.abs(s.rate / s.pred - 1) < 0.01) api.done("double");
      if (api.p.spin === 0 && s.elev < -60 && d.time < 1.0) api.done("fall");
      if (d.time >= 8) api.stop();
    }
    if (s.hist.length > 3000) s.hist.shift();
  },
  chart(api, s, ctx, w, h) {
    const H = s.hist || [];
    const top = Math.max(1, 1.4 * (s.pred || 0), ...H.map((r) => r[1]));
    const t1 = H.length ? Math.max(api.scene === "spindle" ? 1 : 8, H[H.length - 1][0]) : 1;
    api.cplot(56, 10, w - 70, h - 34, [{ pts: H.filter((_, n) => n % 5 === 0).map((r) => [r[0], r[1]]), color: "#b8860b" },
      { pts: [[0, s.pred || 0], [t1, s.pred || 0]], color: "#9aa4ab" }],
      { xmin: 0, xmax: t1, ymin: 0, ymax: top, xlabel: "t / s", ylabel: api.scene === "spindle" ? "|M| / (N·m)" : "Ω / (rad/s)" });
  },
  readouts(api, s) {
    if (!api.sim) return [];
    if (api.scene === "spindle") {
      return [
        [["砂轮的角动量 L = I₃ω", "Wheel angular momentum L = I₃ω"], api.fmt(this.consts.I3r * Math.abs(s.w || 0), 4) + " kg·m²/s"],
        [["测得的陀螺力矩 |M|", "Measured gyroscopic torque |M|"], s.M == null ? "—" : api.fmt(s.M, 4) + " N·m"],
        [["预测 I₃ωΩ", "Prediction I₃ωΩ"], api.fmt(s.pred || 0, 4) + " N·m"],
        [["力矩沿支架 x 轴的分量", "Component along the wrist's x axis"], s.Mx == null ? "—" : api.fmt(s.Mx, 4) + " N·m"],
      ];
    }
    return [
      [["预测的进动角速度 m𝔤l/(I₃ω)", "Predicted precession m𝔤l/(I₃ω)"], api.p.spin > 0 ? api.fmt(s.pred, 4) + " rad/s" : "—"],
      [["测得的进动角速度", "Measured precession rate"], s.rate == null ? "—" : api.fmt(s.rate, 4) + " rad/s"],
      [["轴的仰角（最低）", "Axle elevation (lowest)"], s.elev == null ? "—" : `${api.fmt(s.elev, 2)}°（${api.fmt(s.low, 2)}°）`],
    ];
  },
  tasks: [
    { id: "gyro", robot: true, text: ["电主轴：测得的陀螺力矩与 I₃ωΩ 相差不到 1%。", "Spindle: the measured gyroscopic torque agrees with I₃ωΩ within 1 %."],
      demo: { scene: "spindle", set: { rpm: 12000, Om: 1, dir: 0 }, wait: 3 } },
    { id: "reverse", robot: true, text: ["让砂轮反转：力矩的大小不变，方向反过来（沿支架 x 轴的分量变号）。", "Reverse the wheel: the torque keeps its size and flips direction (its x component changes sign)."],
      demo: { scene: "spindle", set: { rpm: 12000, Om: 1, dir: 1 }, wait: 3 } },
    { id: "prec", text: ["陀螺仪：自转 20 rad/s 以上，测得的进动角速度与 m𝔤l/(I₃ω) 相差不到 1%。", "Gyroscope: with a spin of at least 20 rad/s the measured precession agrees with m𝔤l/(I₃ω) within 1 %."],
      demo: { scene: "top", set: { spin: 60 }, wait: 4 } },
    { id: "double", text: ["把自转减到 30 rad/s：进动加快到约两倍，仍与预测相差不到 1%。", "Reduce the spin to 30 rad/s: the precession roughly doubles and still agrees with the prediction within 1 %."],
      demo: { scene: "top", set: { spin: 30 }, wait: 4 } },
    { id: "fall", text: ["不让圆盘自转：轴在 1 s 内倒到水平线下 60°。", "Without spin the axle drops 60° below the horizontal within 1 s."],
      demo: { scene: "top", set: { spin: 0 }, wait: 3 } },
  ],
  think: ["电主轴的陀螺力矩方向既垂直于转轴，又垂直于扳动的方向。若手腕绕主轴自己的轴线转动，陀螺力矩是多少？为什么？", "The spindle torque is normal to both the spin axis and the turning axis. If the wrist turns about the spindle's own axis, what is the torque, and why?"],
});
