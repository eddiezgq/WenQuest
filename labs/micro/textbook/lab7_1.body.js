// 实验 7.1 存储阵列的划分（配 7.1 节）。4 KB（32768 位）、每次读 32 位的阵列排成 rows 行 × 32768/rows 列，
// 存取时间 = 译码 + 字线 + 位线 + 灵敏放大 + 列选与输出（M7_1.sramAccess，器件数字来自 params.json 的 sram_sim，
// 即 calib/calib_sram.py 的 SKY130 仿真；单元尺寸、译码器宽、列外围高为 problems.p71 的教学设定）。
const Q71 = M7_1.P.problems.p71, BITS71 = Q71.bits, WORD71 = Q71.word;
const ROWS71 = [64, 128, 256, 512, 1024];
const SEG71 = [["dec", "译码", "decode", "#1d6fb8"], ["wl", "字线", "word line", "#7fb3e0"], ["bl", "位线", "bit line", "#c0392b"],
               ["sa", "灵敏放大", "sense amp", "#e67e22"], ["out", "列选与输出", "mux & output", "#2e8b57"]];
const acc71 = (r, dv) => M7_1.sramAccess(r, BITS71 / r, WORD71, dv / 1000);
const argmin71 = (dv, key) => ROWS71.reduce((b, r) => (acc71(r, dv)[key] < acc71(b, dv)[key] ? r : b), ROWS71[0]);

WQ.lab({
  title: ["实验 7.1 存储阵列的划分", "Lab 7.1 Organising a memory array"],
  goal: ["关节控制芯片的 4 KB 故障录波缓冲：调行数和位线摆幅，看存取时间的各段怎样变，找出最快、面积最小的划分。",
         "The 4 KB fault-recording buffer of a joint controller: vary the number of rows and the bit-line swing, watch each part of the access time, and find the fastest and smallest organisation."],
  scenes: [
    { id: "buf", robot: true, name: ["故障录波缓冲", "Fault-recording buffer"], hide: [],
      problem: { title: ["机器人问题：4 KB 怎样排成阵列", "Robot problem: how to arrange 4 KB"],
                 text: ["32768 位排成一长条，位线太长；排成很宽，字线又长又重、列选级数多。中间哪一种最好？",
                        "As a tall strip the bit lines are too long; very wide, the word lines are long and heavy and the column mux is deep. Which in-between is best?"] } },
  ],
  params: [
    { id: "r", name: ["行数（2 的幂次：6 = 64 行 … 10 = 1024 行）", "Rows (power of 2: 6 = 64 … 10 = 1024)"], min: 6, max: 10, step: 1, value: 10, unit: "", digits: 0 },
    { id: "dv", name: ["位线摆幅 ΔV", "Bit-line swing ΔV"], min: 25, max: 200, step: 25, value: 100, unit: "mV", digits: 0 },
  ],
  tasks: [
    { id: "fast", robot: true, text: ["ΔV = 100 mV：找出存取时间最短的划分。", "ΔV = 100 mV: find the organisation with the shortest access time."],
      demo: { scene: "buf", set: { r: 8, dv: 100 }, press: [], wait: 1 } },
    { id: "dv200", text: ["ΔV 加到 200 mV，看 1024 行的阵列：位线一段变成多少？存取时间比 ΔV = 100 mV 时多了多少？", "Raise ΔV to 200 mV and look at 1024 rows: how long is the bit-line part now, and how much longer is the access than at 100 mV?"],
      demo: { scene: "buf", set: { r: 10, dv: 200 }, press: [], wait: 1 } },
    { id: "small", text: ["找出面积最小的划分。", "Find the organisation with the smallest area."],
      demo: { scene: "buf", set: { r: 8, dv: 100 }, press: [], wait: 1 } },
  ],
  think: ["ΔV 加大时，为什么行数多的阵列吃亏最多？ΔV 能不能一直减小？",
          "Why do arrays with many rows suffer most when ΔV grows? Can ΔV keep shrinking?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: SEG71.map((s) => ({ name: [s[1], s[2]], color: s[3] })),
  reset(api, s) { check71(api); },
  readouts(api, s) {
    const f = api.fmt, p = api.p, r = 1 << p.r, a = acc71(r, p.dv);
    return [[["行 × 列 / 列选比", "Rows × columns / mux"], r + " × " + BITS71 / r + " / " + a.mux],
            [["译码 / 字线 / 位线", "Decode / word line / bit line"], f(a.dec * 1e12, 0) + " / " + f(a.wl * 1e12, 0) + " / " + f(a.bl * 1e12, 0) + " ps"],
            [["灵敏放大 / 输出", "Sense amp / output"], f(a.sa * 1e12, 0) + " / " + f(a.out * 1e12, 0) + " ps"],
            [["存取时间", "Access time"], f(a.total * 1e12, 0) + " ps"],
            [["面积 / 长 × 宽", "Area / width × height"], f(a.area / 1e6, 3) + " mm² / " + f(a.w_um, 0) + " × " + f(a.h_um, 0) + " μm"]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, mu = css("--muted"), ink = css("--ink");
    const p = api.p, r = 1 << p.r;
    const all = ROWS71.map((rr) => acc71(rr, p.dv)), tmax = Math.max(...all.map((a) => a.total)) * 1.1;
    const x0 = w * 0.16, bw = w * 0.5, bh = Math.min(26, h * 0.1), y0 = h * 0.12;
    api.label(api.T("存取时间分段（ps）", "Access-time breakdown (ps)"), x0, y0 - 10, mu, 12, "left");
    ROWS71.forEach((rr, i) => {
      const a = all[i], y = y0 + i * (bh + 10);
      let x = x0;
      SEG71.forEach((sg) => { const ww = a[sg[0]] / tmax * bw; api.rect(x, y, ww, bh, sg[3]); x += ww; });
      api.label(rr + "×" + BITS71 / rr, x0 - 6, y + bh * 0.7, rr === r ? ink : mu, rr === r ? 13 : 11, "right");
      api.label(api.fmt(a.total * 1e12, 0), x + 4, y + bh * 0.7, rr === r ? ink : mu, 11, "left");
    });
    // 阵列的形状（按比例）
    const a = acc71(r, p.dv), box = Math.min(w * 0.24, h * 0.7), sc = box / Math.max(...all.map((q) => Math.max(q.w_um, q.h_um)));
    const ax = w * 0.74, ay = h * 0.12;
    api.label(api.T("阵列形状（按比例）", "Array shape (to scale)"), ax, ay - 10, mu, 12, "left");
    api.rect(ax, ay, Math.max(2, a.w_um * sc), Math.max(2, a.h_um * sc), "#9aa5ab");
    api.label(api.fmt(a.w_um, 0) + " × " + api.fmt(a.h_um, 0) + " μm", ax, ay + Math.max(2, a.h_um * sc) + 16, ink, 11, "left");
  },
});

function check71(api) {
  const p = api.p, r = 1 << p.r;
  if (p.dv === 100 && r === argmin71(100, "total")) api.done("fast");
  if (p.dv === 200 && r === 1024) api.done("dv200");
  if (r === argmin71(p.dv, "area")) api.done("small");
}
