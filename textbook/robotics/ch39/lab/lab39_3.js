// 实验 39.3 采样与混叠（配 39.3 节）。正弦信号 sin(2πft)，以 f_s 采样；画出原信号、采样点，以及采样点“看到”的
// 表观频率 f_a = |f − k f_s|（式 (39.3.5)）的正弦。按“开始”让时间轴滚动。
WQ.lab({
  title: ["实验 39.3 采样与混叠", "Lab 39.3 Sampling and aliasing"],
  goal: ["改变信号频率和采样频率，看采样点描出的波形什么时候与原信号一致，什么时候变成另一个频率。",
         "Change the signal and sampling frequencies: when do the samples trace the true signal, and when another frequency?"],
  scenes: [
    { id: "motor", robot: true, name: ["电机振动进入力信号", "Motor vibration in the force signal"],
      problem: { title: ["机器人问题：读数里莫名其妙的 50 Hz", "Robot problem: a mysterious 50 Hz in the readings"],
                 text: ["关节电机在 950 Hz 振动，力传感器以 1 kHz 采样，读数中出现 50 Hz 的波动。是工频干扰吗？",
                        "The joint motor vibrates at 950 Hz; the force sensor samples at 1 kHz and shows a 50 Hz ripple. Is it mains hum?"] } },
    { id: "mains", name: ["视频里的风扇", "A fan on video"],
      problem: { title: ["生活中的例子：视频里的风扇为什么转得慢", "Everyday example: why a fan on video turns slowly"],
                 text: ["风扇的叶片每秒有 50 次转到同一位置，手机每秒拍 60 帧，视频里的风扇看起来每秒只转 10 次，还像是倒着转。",
                        "The blades return to the same position 50 times a second; a phone films 60 frames a second, so on video the fan seems to turn 10 times a second, even backwards."] } },
  ],
  params: [
    { id: "f", name: ["信号频率 f", "Signal frequency f"], min: 10, max: 2000, step: 10, value: 950, unit: "Hz", digits: 0 },
    { id: "fs", name: ["采样频率 f_s", "Sampling frequency f_s"], min: 50, max: 5000, step: 10, value: 1000, unit: "Hz", digits: 0 },
  ],
  buttons: [{ id: "start", name: ["开始", "Start"], primary: true }, { id: "reset", name: ["重置", "Reset"] }],
  tasks: [
    { id: "a50", robot: true, text: ["f_s = 1000 Hz、f = 950 Hz：读出表观频率。", "f_s = 1000 Hz, f = 950 Hz: read the apparent frequency."],
      demo: { scene: "motor", set: { f: 950, fs: 1000 }, press: [] } },
    { id: "fix", robot: true, text: ["保持 f = 950 Hz，找一个采样频率使它不再混叠。", "Keep f = 950 Hz and find a sampling rate with no aliasing."],
      demo: { scene: "motor", set: { f: 950, fs: 2000 }, press: [] } },
    { id: "slow", text: ["f = 50 Hz、f_s = 60 Hz（视频里的风扇）：观察 10 Hz 的伪波动。", "f = 50 Hz, f_s = 60 Hz (the fan on video): watch the false 10 Hz wave."],
      demo: { scene: "mains", set: { f: 50, fs: 60 }, press: [] } },
  ],
  think: ["改变采样频率时，如果读数中某个波动的频率跟着变，说明了什么？", "If a ripple's frequency moves when you change the sampling rate, what does that tell you?"],

  alias(f, fs) { const r = f % fs; return Math.min(r, fs - r); },
  reset(api, s) { s.t0 = 0; },
  update(dt, api, s) { s.t0 += dt * 0.004; },              // 时间轴每秒滚动 4 ms，便于观察
  readouts(api, s) {
    const f = api.p.f, fs = api.p.fs, fa = this.alias(f, fs), ok = f < fs / 2;
    if (api.scene === "motor" && f === 950 && fs === 1000) api.done("a50");
    if (api.scene === "motor" && f === 950 && fs > 1900) api.done("fix");
    if (api.scene === "mains" && f === 50 && fs === 60) api.done("slow");
    return [[["奈奎斯特频率 f_s/2", "Nyquist frequency f_s/2"], api.fmt(fs / 2, 0) + " Hz"],
            [["表观频率 f_a", "apparent frequency f_a"], api.fmt(fa, 0) + " Hz"],
            [["是否混叠", "aliased?"], ok ? (api.lang() === "en" ? "no (f < f_s/2)" : "否（f < f_s/2）") : (api.lang() === "en" ? "yes" : "是")]];
  },
  draw(api, s) {
    const { w, h } = api, f = api.p.f, fs = api.p.fs, fa = this.alias(f, fs);
    const span = Math.max(4 / Math.max(fa, 1), 6 / f, 20 / fs);      // 显示的时间长度：至少几个表观周期
    const T = Math.min(span, 0.25), x0 = 40, x1 = w - 20, y0 = h * 0.5, A = h * 0.32;
    const X = (t) => x0 + (x1 - x0) * (t - s.t0) / T, Y = (v) => y0 - A * v;
    api.line(x0, y0, x1, y0, api.css("--line"), 1);
    // 原信号（细线）：点数随频率增加
    const n = Math.min(4000, Math.max(400, Math.ceil(f * T * 30)));
    const c = api.ctx; c.beginPath();
    for (let i = 0; i <= n; i++) { const t = s.t0 + T * i / n; const p = [X(t), Y(Math.sin(2 * Math.PI * f * t))]; i ? c.lineTo(...p) : c.moveTo(...p); }
    c.strokeStyle = api.css("--muted"); c.lineWidth = 0.8; c.stroke();
    // 采样点与它们连成的折线
    const k0 = Math.ceil(s.t0 * fs), k1 = Math.floor((s.t0 + T) * fs), pts = [];
    for (let k = k0; k <= k1 && pts.length < 2000; k++) pts.push([X(k / fs), Y(Math.sin(2 * Math.PI * f * k / fs))]);
    if (pts.length > 1) { c.beginPath(); pts.forEach((p, i) => (i ? c.lineTo(...p) : c.moveTo(...p))); c.strokeStyle = api.css("--red"); c.lineWidth = 2.5; c.stroke(); }
    if (pts.length < 300) pts.forEach((p) => api.circle(p[0], p[1], 3.5, api.css("--ink")));
    api.label((api.lang() === "en" ? "time window " : "时间窗 ") + api.fmt(T * 1000, 1) + " ms", x0, h - 14, api.css("--muted"), 12);
    api.label("f = " + f + " Hz   f_s = " + fs + " Hz   f_a = " + api.fmt(fa, 0) + " Hz", x0, 16, api.css("--ink"), 14);
  },
});
