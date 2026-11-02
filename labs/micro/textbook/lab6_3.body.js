// 实验 6.3 Booth 编码（配 6.3 节）。8 位无符号乘法：乘数 b 补一位 b(−1) = 0 和高位的 0，每三位 b(2i+1) b(2i) b(2i−1) 编成一个
// 数字 d = −2·b(2i+1) + b(2i) + b(2i−1) ∈ {−2, −1, 0, 1, 2}，共 5 个；第 i 行部分积 = d·a·4^i。与普通的 8 行与门部分积对照。
const BOOTH63 = (b) => {
  const bit = (k) => (k < 0 ? 0 : (b >> k) & 1), d = [];
  for (let i = 0; i < 5; i++) d.push(-2 * bit(2 * i + 1) + bit(2 * i) + bit(2 * i - 1));
  return d;
};
const NZ63 = (b) => BOOTH63(b).filter((x) => x !== 0).length;
const PLAIN63 = (b) => { let n = 0; for (let i = 0; i < 8; i++) n += (b >> i) & 1; return n; };
let minAll63 = null;
for (let b = 0; b < 256 && minAll63 === null; b++) if (NZ63(b) === 5) minAll63 = b;

WQ.lab({
  title: ["实验 6.3 Booth 编码", "Lab 6.3 Booth recoding"],
  goal: ["PI 控制器里的乘法：输入被乘数和乘数，看基 4 Booth 编码把乘数变成哪 5 个数字、每行部分积是多少、加起来是不是乘积；比较普通部分积与 Booth 部分积中不为 0 的行数。",
         "The multiplication in a PI controller: enter the multiplicand and multiplier, see the five radix-4 Booth digits, each partial product and their sum; compare the non-zero rows of ordinary and Booth partial products."],
  scenes: [
    { id: "pi", robot: true, name: ["Kp·e 的乘法", "The Kp·e product"], hide: [],
      problem: { title: ["机器人问题：乘法器能不能小一半", "Robot problem: can the multiplier be halved"],
                 text: ["8 位乘 8 位有 8 行部分积。Booth 编码后只有 5 行，每行是被乘数的 0、±1、±2 倍。", "An 8 × 8 multiply has 8 partial-product rows; after Booth recoding only 5, each 0, ±1 or ±2 times the multiplicand."] } },
  ],
  params: [
    { id: "a", name: ["被乘数 a", "Multiplicand a"], min: 0, max: 255, step: 1, value: 200, unit: "", digits: 0 },
    { id: "b", name: ["乘数 b", "Multiplier b"], min: 0, max: 255, step: 1, value: 100, unit: "", digits: 0 },
  ],
  tasks: [
    { id: "b123", robot: true, text: ["把乘数设为 123，读出 5 个 Booth 数字，验证 Σ d·4^i = 123。", "Set the multiplier to 123, read the five Booth digits and check Σ d·4^i = 123."],
      demo: { scene: "pi", set: { b: 123 }, press: [], wait: 1 } },
    { id: "b255", text: ["乘数 255：普通部分积 8 行都不为 0，Booth 部分积有几行不为 0？", "Multiplier 255: all eight ordinary rows are non-zero. How many Booth rows are?"],
      demo: { scene: "pi", set: { b: 255 }, press: [], wait: 1 } },
    { id: "all5", text: ["找出让 5 个 Booth 数字都不为 0 的最小乘数。", "Find the smallest multiplier whose five Booth digits are all non-zero."],
      demo: { scene: "pi", set: { b: 137 }, press: [], wait: 1 } },
  ],
  think: ["为什么 Booth 编码的乘数要和相邻一组重叠一位？取相反数为什么要“各位取反再加 1”，这个“1”放在哪一列？",
          "Why do adjacent Booth groups overlap by one bit? Why is negation “invert and add 1”, and in which column does that 1 go?"],
  buttons: [{ id: "reset", name: ["重置", "Reset"] }],
  legend: [{ name: ["正的部分积", "positive row"], color: "#1d6fb8" }, { name: ["负的部分积", "negative row"], color: "#c0392b" }],
  reset(api, s) { check63(api); },
  readouts(api, s) {
    const p = api.p, d = BOOTH63(p.b), sum = d.reduce((acc, x, i) => acc + x * p.a * Math.pow(4, i), 0);
    return [[["Booth 数字（低位在前）", "Booth digits (low first)"], d.map((x) => (x > 0 ? "+" : "") + x).join(" ")],
            [["Σ d·4^i", "Σ d·4^i"], String(d.reduce((acc, x, i) => acc + x * Math.pow(4, i), 0))],
            [["部分积之和 / a·b", "Sum of rows / a·b"], sum + " / " + p.a * p.b],
            [["不为 0 的行：普通 / Booth", "Non-zero rows: ordinary / Booth"], PLAIN63(p.b) + " / " + NZ63(p.b)]];
  },
  draw(api, s) {
    const { w, h } = api, css = api.css, mu = css("--muted"), ink = css("--ink"), blue = "#1d6fb8", red = "#c0392b";
    const p = api.p, d = BOOTH63(p.b), x0 = w * 0.06, y0 = h * 0.1, lh = Math.min(30, h * 0.12);
    api.label(api.T("乘数的二进制（补 b(−1) = 0）", "multiplier bits (with b(−1) = 0)"), x0, y0, mu, 12, "left");
    let bits = ""; for (let k = 9; k >= 0; k--) bits += ((p.b >> k) & 1) + (k % 2 === 0 ? "  " : " ");
    api.label(bits + "| 0", x0, y0 + 20, ink, 14, "left");
    d.forEach((x, i) => {
      const y = y0 + 50 + i * lh, v = x * p.a * Math.pow(4, i), col = x < 0 ? red : x > 0 ? blue : mu;
      api.label(api.T("第 " + i + " 行：", "row " + i + ": ") + (x > 0 ? "+" : "") + x + " × a × 4^" + i + " = " + v, x0, y, col, 13, "left");
      const bw = Math.min(w * 0.4, Math.abs(v) / (255 * 2 * 256) * w * 0.4);
      api.rect(w * 0.55, y - 10, bw, 12, col);
    });
    const tot = d.reduce((acc, x, i) => acc + x * p.a * Math.pow(4, i), 0);
    api.label(api.T("合计 ", "sum ") + tot + (tot === p.a * p.b ? " = a·b ✓" : ""), x0, y0 + 50 + 5 * lh + 6, ink, 14, "left");
  },
});

function check63(api) {
  const p = api.p;
  if (p.b === 123) api.done("b123");
  if (p.b === 255) api.done("b255");
  if (p.b === minAll63) api.done("all5");
}
