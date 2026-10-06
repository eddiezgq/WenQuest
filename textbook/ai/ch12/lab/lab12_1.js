// 实验 12.1 从波形到梅尔频谱（配 12.1 节）。三个场景：
//   wave：看合成的语音波形与它的频谱，改元音（共振峰不同）、加噪声；
//   frame：改帧长与帧移，看时间分辨率与频率分辨率此消彼长（测不准：窗短则时间准、频率糊）；
//   mel ：改梅尔滤波器的个数，看一帧 201 个频点被归并成多少维、信息丢了多少（用重建误差衡量）。
// 信号由程序按公式合成（与书中 _ch12.py 的办法相同），不需要麦克风，也不传任何录音。
WQ.lab({
  title: ["实验 12.1 从波形到梅尔频谱", "Lab 12.1 From waveform to mel spectrogram"],
  goal: ["改元音、噪声、帧长、帧移与梅尔滤波器个数，看同一段语音在波形、频谱、梅尔频谱三种表示下各是什么样，数据量差多少，什么信息被丢掉了。",
         "Change the vowel, the noise, the frame length and hop, and the number of mel filters; see the same speech as a waveform, a spectrum and a mel spectrogram, how much data each needs and what gets discarded."],
  scenes: [
    { id: "wave", name: ["波形与频谱", "Waveform and spectrum"],
      problem: { title: ["问题：一段声音里有什么", "Problem: what is in a sound"],
                 text: ["元音由基频的谐波按共振峰加权而成：改一个元音，谐波还在，包络（共振峰的位置）变了。识别要认的正是这个包络，而不是绝对音高。",
                        "A vowel is the harmonics of the pitch shaped by formants: change the vowel and the harmonics stay, the envelope moves. Recognition reads that envelope, not the absolute pitch."] } },
    { id: "frame", name: ["分帧", "Framing"],
      problem: { title: ["问题：窗开多大", "Problem: how long a window"],
                 text: ["窗短了，时间上分得清，频率上糊成一片；窗长了反过来。语音常用 25 毫秒：既能看清共振峰，又跟得上音素的变化。",
                        "A short window resolves time but blurs frequency; a long one does the opposite. Speech uses about 25 ms: fine enough in frequency, fast enough for phonemes."] } },
    { id: "mel", name: ["梅尔频带", "Mel bands"],
      problem: { title: ["问题：频点能并多少", "Problem: how far can we pool"],
                 text: ["201 个频点并成 80 个梅尔频带，数据少一半多；并成 20 个呢？并得越狠，越省，丢的也越多——丢到什么程度就认不出音素了？",
                        "201 bins pool into 80 mel bands, less than half the data. What about 20? The more you pool the cheaper it gets — and the more you lose."] } },
  ],
  params: [
    { id: "vowel", name: ["元音（0 a · 1 i · 2 u · 3 e）", "Vowel (0 a · 1 i · 2 u · 3 e)"], min: 0, max: 3, step: 1, value: 0, digits: 0 },
    { id: "f0", name: ["基频 F0（Hz）", "Pitch F0 (Hz)"], min: 80, max: 260, step: 5, value: 120, digits: 0 },
    { id: "snr", name: ["信噪比（dB）", "SNR (dB)"], min: -10, max: 40, step: 1, value: 40, digits: 0 },
    { id: "frame", name: ["帧长（ms）", "Frame length (ms)"], min: 5, max: 80, step: 5, value: 25, digits: 0 },
    { id: "hop", name: ["帧移（ms）", "Hop (ms)"], min: 2, max: 40, step: 1, value: 10, digits: 0 },
    { id: "nmel", name: ["梅尔滤波器个数", "Mel filters"], min: 8, max: 128, step: 4, value: 80, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["波形", "waveform"] }, { color: "var(--red)", name: ["频谱", "spectrum"] },
           { color: "var(--green)", name: ["梅尔频带", "mel bands"] }],
  tasks: [
    { id: "formant", text: ["把元音从 a 换成 i：频谱的包络怎么变？基频从 120 改到 220 Hz 时，包络变不变？",
                            "Switch the vowel from a to i: how does the spectral envelope move? Now raise the pitch from 120 to 220 Hz — does the envelope follow?"],
      demo: { scene: "wave", set: { vowel: 1, f0: 220 }, press: [] } },
    { id: "window", text: ["帧长从 25 ms 减到 5 ms：频率分辨率变成多少赫兹？还分得清相邻的谐波吗？",
                           "Shorten the frame from 25 ms to 5 ms: what is the frequency resolution? Can you still separate neighbouring harmonics?"],
      demo: { scene: "frame", set: { frame: 5 }, press: [] } },
    { id: "pool", text: ["梅尔滤波器从 80 个减到 16 个：每秒的数据量变成多少？重建误差涨了多少？",
                         "Cut the mel filters from 80 to 16: how much data per second, and how much does the reconstruction error grow?"],
      demo: { scene: "mel", set: { nmel: 16 }, press: [] } },
    { id: "noise", text: ["把信噪比降到 0 dB：频谱里还看得见共振峰吗？梅尔频谱呢？（这解释了为什么增强要在特征之前做。）",
                          "Drop the SNR to 0 dB: can you still see the formants in the spectrum? In the mel spectrogram? (This is why enhancement comes before features.)"],
      demo: { scene: "wave", set: { snr: 0 }, press: [] } },
  ],
  think: ["为什么识别用的是频谱的包络而不是基频？同一句话男声女声说出来，什么变了、什么没变？",
          "Why do recognizers read the spectral envelope rather than the pitch? Said by a man and a woman, what changes and what does not?"],

  SR: 16000,
  VOW: [[730, 1090, 2440], [270, 2290, 3010], [300, 870, 2240], [530, 1840, 2480]],
  rand(i) { const x = Math.sin(i * 12.9898 + 78.233) * 43758.5453; return 2 * (x - Math.floor(x)) - 1; },
  signal(api) {
    const p = api.p, n = 2048, sr = this.SR, F = this.VOW[p.vowel];
    const x = new Float64Array(n);
    for (let k = 1; k <= 40; k++) {
      const f = p.f0 * k;
      if (f > sr / 2) break;
      let g = 0;
      for (const fc of F) g += 1 / (1 + ((f - fc) / 90) ** 2);
      for (let i = 0; i < n; i++) x[i] += (g / k) * Math.sin(2 * Math.PI * f * i / sr);
    }
    let mx = 0;
    for (let i = 0; i < n; i++) mx = Math.max(mx, Math.abs(x[i]));
    for (let i = 0; i < n; i++) x[i] /= mx || 1;
    if (p.snr < 40) {                                   // 叠加噪声（1/f 一类，低频更强）
      let ps = 0;
      for (let i = 0; i < n; i++) ps += x[i] * x[i];
      ps /= n;
      const nz = new Float64Array(n);
      let pn = 0;
      for (let i = 0; i < n; i++) { nz[i] = 0.6 * this.rand(i) + 0.4 * this.rand(Math.floor(i / 8)); pn += nz[i] * nz[i]; }
      pn /= n;
      const k = Math.sqrt(ps / (pn * Math.pow(10, p.snr / 10)));
      for (let i = 0; i < n; i++) x[i] += k * nz[i];
    }
    return x;
  },
  // 朴素的离散傅里叶变换（点数不多，够用；真实实现用快速傅里叶变换）
  spectrum(x, n) {
    const out = new Float64Array(Math.floor(n / 2) + 1);
    const win = new Float64Array(n);                       // 汉明窗预先算好，不在内层循环里重复算
    for (let i = 0; i < n; i++) win[i] = 0.54 - 0.46 * Math.cos(2 * Math.PI * i / (n - 1));
    for (let f = 0; f < out.length; f++) {
      let re = 0, im = 0;
      for (let i = 0; i < n; i++) {
        const a = 2 * Math.PI * f * i / n;
        re += x[i] * win[i] * Math.cos(a);
        im -= x[i] * win[i] * Math.sin(a);
      }
      out[f] = (re * re + im * im) / n;
    }
    return out;
  },
  // 三角窗按频点的实际频率算权重（不把顶点取整到频点，否则低频的窄窗会塌成全零），每行归一化成单位面积
  melBank(nMel, nBins, sr) {
    const hz2mel = (f) => 2595 * Math.log10(1 + f / 700), mel2hz = (m) => 700 * (Math.pow(10, m / 2595) - 1);
    const lo = hz2mel(20), hi = hz2mel(sr / 2), pts = [];
    for (let i = 0; i < nMel + 2; i++) pts.push(mel2hz(lo + (hi - lo) * i / (nMel + 1)));
    const df = sr / (2 * (nBins - 1)), bank = [];
    for (let i = 0; i < nMel; i++) {
      const row = new Float64Array(nBins);
      let area = 0;
      for (let j = 0; j < nBins; j++) {
        const f = j * df;
        const v = Math.max(0, Math.min((f - pts[i]) / Math.max(pts[i + 1] - pts[i], 1e-9),
                                       (pts[i + 2] - f) / Math.max(pts[i + 2] - pts[i + 1], 1e-9)));
        row[j] = v; area += v;
      }
      if (area > 0) for (let j = 0; j < nBins; j++) row[j] /= area;
      bank.push(row);
    }
    return bank;
  },
  calc(api) {
    const p = api.p, sr = this.SR;
    const key = [p.vowel, p.f0, p.snr, p.frame, p.hop, p.nmel].join(",");
    if (this._cache && this._cache.key === key) return this._cache.val;           // 一次重画只算一遍
    const n = Math.max(32, Math.round(sr * p.frame / 1000));                      // 帧长就是帧长，不圆整
    const x = this.signal(api);
    const spec = this.spectrum(x.subarray(0, n), n);
    const bank = this.melBank(p.nmel, spec.length, sr);
    const mel = bank.map((row) => { let s = 0; for (let j = 0; j < row.length; j++) s += row[j] * spec[j]; return Math.log(s + 1e-10); });
    // 重建误差：把梅尔频带按滤波器摊回频点，与原频谱比（衡量归并丢了多少）。只在被滤波器覆盖的频点上算，
    // 误差按频谱的动态范围归一——这样它随滤波器个数单调下降，才能用来比较。
    const rec = new Float64Array(spec.length), wsum = new Float64Array(spec.length);
    bank.forEach((row, i) => { for (let j = 0; j < row.length; j++) { rec[j] += row[j] * Math.exp(mel[i]); wsum[j] += row[j]; } });
    let num = 0, cnt = 0, lmin = Infinity, lmax = -Infinity;
    for (let j = 0; j < spec.length; j++) {
      const ls = Math.log(spec[j] + 1e-10);
      if (wsum[j] > 1e-9) { lmin = Math.min(lmin, ls); lmax = Math.max(lmax, ls); }
    }
    for (let j = 0; j < spec.length; j++) {
      if (wsum[j] <= 1e-9) continue;                                   // 没被任何滤波器覆盖的频点不计
      const ls = Math.log(spec[j] + 1e-10), lr = Math.log(rec[j] / wsum[j] + 1e-10);
      num += (ls - lr) ** 2; cnt++;
    }
    const val = { n, x, spec, mel, df: sr / n, fps: 1000 / p.hop, bins: spec.length,
                  err: Math.sqrt(num / Math.max(cnt, 1)) / Math.max(lmax - lmin, 1e-9) * 100 };
    this._cache = { key, val };
    return val;
  },
  reset(api, s) {},
  readouts(api, s) {
    const p = api.p, r = this.calc(api);
    if (p.vowel === 1 && p.f0 >= 200) api.done("formant");
    if (p.frame <= 5) api.done("window");
    if (p.nmel <= 16) api.done("pool");
    if (p.snr <= 0) api.done("noise");
    const wave = this.SR, melN = r.fps * p.nmel, specN = r.fps * r.bins;
    return [[["每帧的采样点数 / 频点数", "samples per frame / bins"], r.n + " / " + r.bins],
            [["频率分辨率", "frequency resolution"], api.fmt(r.df, 1) + " Hz"],
            [["帧率 / 相邻帧重叠", "frames per second / overlap"], api.fmt(r.fps, 0) + api.T(" 帧/秒", " fps") + " / " + api.fmt(Math.max(0, (p.frame - p.hop) / p.frame * 100), 0) + "%"],
            [["每秒的数：波形 / 频谱 / 梅尔", "numbers per second: wave / spec / mel"], wave + " / " + api.fmt(specN, 0) + " / " + api.fmt(melN, 0)],
            [["梅尔比波形省", "mel vs waveform"], api.fmt(wave / Math.max(melN, 1), 1) + api.T(" 倍", "×")],
            [["归并的重建误差", "pooling error"], api.fmt(r.err, 1) + "%"]];
  },
  draw(api, s) {
    const { w, h } = api, m = 30, r = this.calc(api);
    const third = (h - 60) / 3;
    // 波形
    api.label(api.T("波形", "waveform"), m, 20, api.css("--blue"), 12);
    const N = Math.min(r.n, 600);
    for (let i = 1; i < N; i++) {
      api.line(m + (i - 1) / N * (w - 2 * m), 20 + third / 2 - r.x[i - 1] * third / 2.5,
               m + i / N * (w - 2 * m), 20 + third / 2 - r.x[i] * third / 2.5, api.css("--blue"), 1);
    }
    // 频谱
    api.label(api.T("频谱（对数）", "spectrum (log)"), m, 30 + third, api.css("--red"), 12);
    const sp = r.spec, lo = Math.log(1e-8);
    let top = lo;
    for (const v of sp) top = Math.max(top, Math.log(v + 1e-10));
    for (let j = 0; j < sp.length; j++) {
      const v = (Math.log(sp[j] + 1e-10) - lo) / (top - lo + 1e-9);
      const x0 = m + j / sp.length * (w - 2 * m);
      api.rect(x0, 36 + third + third * (1 - Math.max(0, v)), Math.max(1, (w - 2 * m) / sp.length - 1),
               third * Math.max(0.01, v), api.css("--red"));
    }
    // 梅尔
    api.label(api.T("梅尔频带（对数）", "mel bands (log)"), m, 46 + 2 * third, api.css("--green"), 12);
    const mel = r.mel;
    let mlo = Infinity, mhi = -Infinity;
    for (const v of mel) { mlo = Math.min(mlo, v); mhi = Math.max(mhi, v); }
    for (let j = 0; j < mel.length; j++) {
      const v = (mel[j] - mlo) / (mhi - mlo + 1e-9);
      const x0 = m + j / mel.length * (w - 2 * m);
      api.rect(x0, 52 + 2 * third + third * (1 - v), Math.max(2, (w - 2 * m) / mel.length - 2),
               third * Math.max(0.01, v), api.css("--green"));
    }
  },
});
