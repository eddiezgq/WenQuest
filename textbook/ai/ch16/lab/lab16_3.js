// 实验 16.3 加噪与去噪（配 16.3 节）。
// 两个场景：
//   forward ：把加噪时刻 t 拖大，看三个峰怎样被抹平成一团标准正态；
//   reverse ：从纯噪声出发去噪，调采样步数与随机性，看质量与代价怎么换。
// 真分布是已知的混合高斯，所以像不像由柯尔莫哥洛夫—斯米尔诺夫距离说了算，不用猜。
// 最优的噪声预测器对这个分布有解析式，所以浏览器里不用训模型就能采样——
// 与 code/_ch16.py 的 eps_exact 是同一个式子。
WQ.lab({
  title: ["实验 16.3 把分布揉成噪声，再揉回来", "Lab 16.3 Noise it into a Gaussian, then bring it back"],
  goal: ["亲手拖加噪的时刻，看三个峰在第几步就认不出来了；再调采样步数，看少走几步要拿质量换多少。做完能回答三个问题：前向过程为什么不用学、反向每一步到底在估什么、步数砍到十分之一会坏成什么样。",
         "Drag the noising time and watch the three modes disappear; then change the number of sampling steps and see what fewer steps cost. You should be able to say why the forward process needs no training, what each reverse step estimates, and how bad ten steps really is."],
  scenes: [
    { id: "forward", name: ["正向：加噪", "Forward: add noise"],
      problem: { title: ["问题：加到第几步就认不出来了", "Problem: when do the modes vanish"],
                 text: ["前向过程每一步掺一点高斯噪声，而且第 t 步有闭式解：x_t = √ᾱ_t·x_0 + √(1−ᾱ_t)·ε。这一步没有任何参数，不用学。把 t 拖大，看三个峰什么时候被抹平、和标准正态（虚线）什么时候重合。",
                        "Each forward step mixes in Gaussian noise, and step t has a closed form: x_t = sqrt(abar_t) x_0 + sqrt(1 - abar_t) eps. It has no parameters at all. Drag t and watch the three modes flatten into the standard normal (dashed)."] } },
    { id: "reverse", name: ["反向：去噪采样", "Reverse: denoise and sample"],
      problem: { title: ["问题：少走几步，差多少", "Problem: what do fewer steps cost"],
                 text: ["反向过程从纯噪声起步，每一步估一次“这里掺了多少噪声”，减掉一点。走满一千步质量最好，但一千次前向太贵。把步数往下调，看分布从哪一档开始明显偏；再把随机性 η 调到 0（确定性采样），看是不是更扛得住少步数。",
                        "The reverse process starts from pure noise and at each step estimates how much noise is in the sample. A thousand steps is best but costs a thousand forward passes. Lower the step count and see where the distribution visibly drifts; then set eta to 0 for deterministic sampling."] } },
  ],
  params: [
    { id: "t", name: ["加噪到第几步 t", "noising step t"], min: 0, max: 999, step: 1, value: 0, digits: 0 },
    { id: "steps", name: ["采样步数", "sampling steps"], min: 5, max: 300, step: 5, value: 200, digits: 0 },
    { id: "eta", name: ["随机性 η（0 = 确定采样）", "randomness eta (0 = deterministic)"], min: 0, max: 1, step: 0.1, value: 1, digits: 1 },
    { id: "n", name: ["画多少个样本", "number of samples"], min: 500, max: 3000, step: 500, value: 2000, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["现在的分布", "current distribution"] },
           { color: "var(--ink)", name: ["真分布", "true density"] },
           { color: "var(--muted)", name: ["标准正态", "standard normal"] }],
  tasks: [
    { id: "flat", text: ["把 t 拖到最大：分布和标准正态（虚线）重合了吗？这时候还看得出原来有几个峰吗？",
                         "Drag t to the maximum: does the distribution match the dashed normal, and can you still tell how many modes there were?"],
      demo: { scene: "forward", set: { t: 999 }, press: [] } },
    { id: "vanish", text: ["把 t 从 0 慢慢拖到 400：右边那个又矮又窄的峰大约在第几步先不见了？左边那个最密的呢？",
                           "Drag t from 0 up to 400: at roughly which step does the low narrow right mode disappear, and when does the dense left one go?"],
      demo: { scene: "forward", set: { t: 300 }, press: [] } },
    { id: "full", text: ["切到反向场景，步数留在 200：KS 距离是多少？与“同样本量真样本的下限”差多少？",
                         "Switch to the reverse scene with 200 steps: what is the KS distance, and how far is it above the finite-sample floor?"],
      demo: { scene: "reverse", set: { steps: 200, eta: 1 }, press: [] } },
    { id: "few", text: ["把步数砍到 10：KS 距离涨了几倍？画面上哪个峰最先出问题？",
                        "Cut the steps to 10: how many times larger is the KS distance, and which mode suffers first?"],
      demo: { scene: "reverse", set: { steps: 10 }, press: [] } },
    { id: "eta0", text: ["步数仍是 10，把 η 调到 0（确定性采样）：好一点还是差一点？记下两个数。",
                         "Keep 10 steps and set eta to 0 for deterministic sampling: better or worse? Write down both numbers."],
      demo: { scene: "reverse", set: { steps: 10, eta: 0 }, press: [] } },
  ],
  think: ["把步数从 300 一档一档减到 5，把 KS 距离记成一条曲线。它在哪一段几乎不变、哪一段开始陡起来？如果每一步的代价相同，你会把步数定在哪里？",
          "Sweep the step count from 400 down to 5 and plot the KS distance. Where is it flat, and where does it take off? If every step costs the same, where would you set it?"],

  // ---- 与 code/_ch16.py 同一个三峰分布（标准化之后）
  W: [0.5, 0.35, 0.15],
  MU: [-2.0, 0.6, 3.2],
  SD: [0.45, 0.6, 0.25],
  TT: 1000,
  init() {
    if (this._ready) return;
    let m = 0, m2 = 0;
    for (let k = 0; k < 3; k++) { m += this.W[k] * this.MU[k]; m2 += this.W[k] * (this.SD[k] * this.SD[k] + this.MU[k] * this.MU[k]); }
    this.M = m; this.S = Math.sqrt(m2 - m * m);
    this.ZMU = this.MU.map((v) => (v - m) / this.S);
    this.ZSD = this.SD.map((v) => v / this.S);
    this.BETA = new Float64Array(this.TT);
    this.ABAR = new Float64Array(this.TT);
    let acc = 1;
    for (let t = 0; t < this.TT; t++) { this.BETA[t] = 1e-4 + (0.02 - 1e-4) * t / (this.TT - 1); acc *= 1 - this.BETA[t]; this.ABAR[t] = acc; }
    this._ready = true;
  },
  rng(seed) { let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; },
  normal(r) { const u = Math.max(r(), 1e-12), v = r(); return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v); },
  real(n, seed) {                                     // 真样本（标准化坐标）
    const r = this.rng(seed), out = new Float64Array(n);
    for (let i = 0; i < n; i++) {
      let u = r(), k = 0, c = 0;
      for (; k < 3; k++) { c += this.W[k]; if (u <= c) break; }
      k = Math.min(k, 2);
      out[i] = this.ZMU[k] + this.ZSD[k] * this.normal(r);
    }
    return out;
  },
  cdf(z) {                                            // 真分布的累积分布（标准化坐标）
    let s = 0;
    for (let k = 0; k < 3; k++) s += this.W[k] * 0.5 * (1 + this.erf((z - this.ZMU[k]) / (this.ZSD[k] * Math.SQRT2)));
    return s;
  },
  erf(x) {                                            // Abramowitz & Stegun 7.1.26
    const s = x < 0 ? -1 : 1; x = Math.abs(x);
    const t = 1 / (1 + 0.3275911 * x);
    const y = 1 - ((((1.061405429 * t - 1.453152027) * t + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * Math.exp(-x * x);
    return s * y;
  },
  pdf(z) {
    let s = 0;
    for (let k = 0; k < 3; k++) s += this.W[k] / (this.ZSD[k] * Math.sqrt(2 * Math.PI)) * Math.exp(-0.5 * Math.pow((z - this.ZMU[k]) / this.ZSD[k], 2));
    return s;
  },
  ksNormal(arr) {
    const s = Array.from(arr).sort((a, b) => a - b);
    let d = 0;
    for (let i = 0; i < s.length; i++) d = Math.max(d, Math.abs((i + 1) / s.length - 0.5 * (1 + this.erf(s[i] / Math.SQRT2))));
    return d;
  },
  ks(arr) {
    const s = Array.from(arr).sort((a, b) => a - b);
    let d = 0;
    for (let i = 0; i < s.length; i++) d = Math.max(d, Math.abs((i + 1) / s.length - this.cdf(s[i])));
    return d;
  },
  coverage(arr) {
    let c = 0;
    for (let k = 0; k < 3; k++) {
      let hit = 0;
      for (let i = 0; i < arr.length; i++) if (Math.abs(arr[i] - this.ZMU[k]) < 2 * this.ZSD[k]) hit++;
      if (hit / arr.length > 0.01) c++;
    }
    return c;
  },
  epsStar(z, t) {                                     // 最优噪声预测器（解析解）
    const ab = this.ABAR[t];
    let num = 0, den = 0;
    for (let k = 0; k < 3; k++) {
      const mu = Math.sqrt(ab) * this.ZMU[k], va = ab * this.ZSD[k] * this.ZSD[k] + (1 - ab);
      const d = z - mu, c = this.W[k] / Math.sqrt(2 * Math.PI * va) * Math.exp(-0.5 * d * d / va);
      num += c * (-d / va); den += c;
    }
    return -Math.sqrt(1 - ab) * (num / Math.max(den, 1e-300));
  },
  sample(n, steps, eta, seed) {
    const r = this.rng(seed), z = new Float64Array(n);
    for (let i = 0; i < n; i++) z[i] = this.normal(r);
    const ts = [];
    for (let i = 0; i < steps; i++) ts.push(Math.round((this.TT - 1) * (1 - i / Math.max(steps - 1, 1))));
    const uniq = ts.filter((v, i) => i === 0 || v !== ts[i - 1]);
    for (let i = 0; i < uniq.length; i++) {
      const t = uniq[i], ab = this.ABAR[t];
      const tp = i + 1 < uniq.length ? uniq[i + 1] : -1;
      const abp = tp >= 0 ? this.ABAR[tp] : 1;
      const sig = tp >= 0 ? eta * Math.sqrt(Math.max((1 - abp) / (1 - ab) * (1 - ab / abp), 0)) : 0;
      const keep = Math.sqrt(Math.max(1 - abp - sig * sig, 0));
      for (let j = 0; j < n; j++) {
        const e = this.epsStar(z[j], t);
        let zh = (z[j] - Math.sqrt(1 - ab) * e) / Math.sqrt(ab);
        zh = Math.max(-6, Math.min(6, zh));
        if (tp < 0) { z[j] = zh; continue; }
        z[j] = Math.sqrt(abp) * zh + keep * e + (sig > 0 ? sig * this.normal(r) : 0);
      }
    }
    return z;
  },
  calc(api) {
    this.init();
    const p = api.p, key = [api.scene, p.t, p.steps, p.eta, p.n].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    let cur, floor = 0;
    const n = Math.round(p.n);
    if (api.scene === "forward") {
      const z0 = this.real(n, 7), r = this.rng(31), t = Math.round(p.t);
      cur = new Float64Array(n);
      const a = Math.sqrt(this.ABAR[t]), b = Math.sqrt(1 - this.ABAR[t]);
      for (let i = 0; i < n; i++) cur[i] = a * z0[i] + b * this.normal(r);
    } else {
      cur = this.sample(n, Math.round(p.steps), p.eta, 17);
    }
    let f = 0;
    for (let s = 0; s < 4; s++) f += this.ks(this.real(n, 900 + s));
    floor = f / 4;
    const val = { cur, ks: this.ks(cur), ksn: this.ksNormal(cur), cov: this.coverage(cur), floor,
                  abar: this.ABAR[Math.round(p.t)], passes: api.scene === "forward" ? 0 : Math.round(p.steps) };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const p = api.p, c = this.calc(api);
    if (api.scene === "forward" && p.t >= 990) api.done("flat");
    if (api.scene === "forward" && p.t >= 250 && p.t <= 400) api.done("vanish");
    if (api.scene === "reverse" && p.steps >= 150 && p.eta > 0.5) api.done("full");
    if (api.scene === "reverse" && p.steps <= 15) api.done("few");
    if (api.scene === "reverse" && p.steps <= 15 && p.eta < 0.05) api.done("eta0");
    if (api.scene === "forward") {
      return [[["ᾱ_t（原始信号还剩多少）", "abar_t (signal left)"], c.abar.toFixed(4)],
              [["√ᾱ_t（原信号的系数）", "sqrt(abar_t)"], Math.sqrt(c.abar).toFixed(3)],
              [["√(1−ᾱ_t)（噪声的系数）", "sqrt(1-abar_t)"], Math.sqrt(1 - c.abar).toFixed(3)],
              [["与标准正态的 KS 距离", "KS distance to the standard normal"], c.ksn.toFixed(3)],
              [["与真分布的 KS 距离", "KS distance to the true density"], c.ks.toFixed(3)]];
    }
    return [[["与真分布的 KS 距离", "KS distance to the true density"], c.ks.toFixed(3)],
            [["同样本量真样本的下限", "finite-sample floor"], c.floor.toFixed(3)],
            [["比下限高几倍", "times the floor"], (c.ks / Math.max(c.floor, 1e-9)).toFixed(1)],
            [["覆盖了几个峰", "modes covered"], String(c.cov)],
            [["采一次要几次前向", "forward passes per sample"], String(c.passes)]];
  },
  draw(api, s) {
    this.init();
    const { w, h } = api, c = this.calc(api);
    const x0 = 56, y0 = 22, pw = w - x0 - 28, ph = h - y0 - 44;
    const LO = -4, HI = 4, NB = 64;
    const hist = new Float64Array(NB);
    for (let i = 0; i < c.cur.length; i++) {
      const b = Math.floor((Math.max(LO, Math.min(HI - 1e-9, c.cur[i])) - LO) / (HI - LO) * NB);
      hist[b]++;
    }
    const bw = (HI - LO) / NB;
    for (let b = 0; b < NB; b++) hist[b] /= c.cur.length * bw;
    let top = 0;
    for (let b = 0; b < NB; b++) top = Math.max(top, hist[b]);
    for (let z = LO; z <= HI; z += 0.02) top = Math.max(top, this.pdf(z));
    top *= 1.12;
    const X = (z) => x0 + (z - LO) / (HI - LO) * pw;
    const Y = (v) => y0 + ph - v / top * ph;
    api.rect(x0, y0, pw, ph, null, api.css("--grid"), 1);
    for (let z = LO; z <= HI; z += 1) { api.line(X(z), y0, X(z), y0 + ph, api.css("--grid"), 1);
      api.label(String(z), X(z) - 6, y0 + ph + 16, api.css("--muted"), 11); }
    for (let b = 0; b < NB; b++) {
      if (hist[b] <= 0) continue;
      const px = X(LO + b * bw), pwid = Math.max(X(LO + (b + 1) * bw) - px - 1, 1);
      api.rect(px, Y(hist[b]), pwid, y0 + ph - Y(hist[b]), api.scene === "forward" ? "rgba(31,119,180,0.55)" : "rgba(44,160,44,0.55)", null, 0);
    }
    let prev = null, prevN = null;
    for (let z = LO; z <= HI; z += 0.02) {
      const cur = [X(z), Y(this.pdf(z))];
      const curN = [X(z), Y(Math.exp(-0.5 * z * z) / Math.sqrt(2 * Math.PI))];
      if (prev) api.line(prev[0], prev[1], cur[0], cur[1], api.css("--ink"), 2.0);
      if (prevN) api.line(prevN[0], prevN[1], curN[0], curN[1], api.css("--muted"), 1.3, [5, 4]);
      prev = cur; prevN = curN;
    }
    api.label(api.T("密度", "density"), 10, y0 + 12, api.css("--muted"), 12);
    api.label(api.T("标准化之后的取值", "standardized value"), x0 + pw / 2 - 48, h - 12, api.css("--muted"), 12);
    const tag = api.scene === "forward"
      ? api.T(`t = ${Math.round(api.p.t)}，KS = ${c.ks.toFixed(3)}`, `t = ${Math.round(api.p.t)}, KS = ${c.ks.toFixed(3)}`)
      : api.T(`${Math.round(api.p.steps)} 步，KS = ${c.ks.toFixed(3)}`, `${Math.round(api.p.steps)} steps, KS = ${c.ks.toFixed(3)}`);
    api.label(tag, x0 + pw - 170, y0 + 18, api.css("--ink"), 13);
  },
});
