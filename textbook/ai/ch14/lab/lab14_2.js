// 实验 14.2 一张图进了语言模型，要花多少（配 14.2、14.6 节）。
// 两个场景：
//   page  ：一页图纸按定分辨率还是按切片进模型——词元数、注意力代价、键值缓存，以及字还认不认得出；
//   mix   ：一天的工作量——多少页图纸、多少页文字，加起来多少词元、要多少显存。
// 全部是算术，在浏览器里现算；公式与 code/_ch14.py 的 tokens_of / tiled_tokens / attn_cost 一致。
WQ.lab({
  title: ["实验 14.2 视觉词元的账", "Lab 14.2 Counting visual tokens"],
  goal: ["把“一张图要多少词元”这件事算清楚：分辨率、块大小、2×2 合并、切片各起什么作用；再看注意力代价与键值缓存怎样随之涨，以及把整页缩进 336 像素之后，图纸上的字还剩几个像素。",
         "Work out what an image costs in tokens: resolution, patch size, 2x2 merging and tiling; then watch attention cost and KV cache follow, and see how many pixels a dimension label has left once a full page is squeezed into 336 pixels."],
  scenes: [
    { id: "page", name: ["一页图纸", "One drawing"],
      problem: { title: ["问题：整页缩小还是切片", "Problem: shrink the page or tile it"],
                 text: ["A4 图纸按 300 dpi 扫描是 2480×3508 像素。整页缩到 336×336 只要 576 个词元，但 3 毫米高的尺寸数字只剩三个多像素，认不出来；按 448×448 切片则认得出，代价是词元数涨几十倍。",
                        "An A4 drawing at 300 dpi is 2480x3508 px. Squeezed into 336x336 it costs only 576 tokens, but a 3 mm dimension label is left with about three pixels. Tiling at 448x448 keeps it readable at tens of times the tokens."] } },
    { id: "mix", name: ["一天的量", "A day's workload"],
      problem: { title: ["问题：一天的图纸与报告加起来要多少", "Problem: what does a day of pages cost"],
                 text: ["车间一天几十页图纸、几百页文字记录。词元数决定算力与显存：注意力那两项按词元数的平方涨，键值缓存按词元数线性涨。先把这笔账算出来，再谈上不上线。",
                        "A shop floor produces dozens of drawings and hundreds of text pages a day. Attention grows with the square of the token count and the KV cache grows linearly — do the arithmetic before promising a deployment."] } },
  ],
  params: [
    { id: "res", name: ["定分辨率（像素，方图）", "fixed resolution (px)"], min: 224, max: 1344, step: 112, value: 336, digits: 0 },
    { id: "patch", name: ["块大小", "patch size"], min: 14, max: 32, step: 2, value: 14, digits: 0 },
    { id: "merge", name: ["相邻几×几合成一个词元", "merge n x n tokens into one"], min: 1, max: 3, step: 1, value: 1, digits: 0 },
    { id: "tile", name: ["切片边长（像素，0 = 不切片）", "tile size (0 = no tiling)"], min: 0, max: 672, step: 112, value: 448, digits: 0 },
    { id: "pages", name: ["一天的图纸页数", "drawings per day"], min: 10, max: 200, step: 10, value: 40, digits: 0 },
    { id: "textPages", name: ["一天的文字页数", "text pages per day"], min: 0, max: 1000, step: 50, value: 300, digits: 0 },
  ],
  legend: [{ color: "var(--blue)", name: ["视觉词元", "visual tokens"] }, { color: "var(--red)", name: ["注意力代价", "attention cost"] }],
  tasks: [
    { id: "shrink", text: ["把切片关掉（切片边长 0）、定分辨率设 336：一页图纸多少词元？3 毫米高的字还剩几个像素？读得出吗？",
                           "Turn tiling off and set the resolution to 336: how many tokens is one page, and how many pixels tall is a 3 mm dimension label?"],
      demo: { scene: "page", set: { tile: 0, res: 336 }, press: [] } },
    { id: "tiles", text: ["把切片边长设回 448：词元数变成多少？是 336 整页的几倍？与 InternVL 1.5 报告给的测试上限 10496 对得上吗？",
                          "Set the tile size back to 448: how many tokens now, and how does that compare with InternVL 1.5's reported test cap of 10,496?"],
      demo: { scene: "page", set: { tile: 448, res: 336 }, press: [] } },
    { id: "merge2", text: ["把“相邻几×几合成一个”调到 2（Qwen2-VL 的做法）：词元数少了几倍？注意力代价少了几倍？两者为什么不一样？",
                           "Set the merge factor to 2 (what Qwen2-VL does): by how much do the tokens drop, and by how much does the attention cost drop? Why are the two different?"],
      demo: { scene: "page", set: { merge: 2 }, press: [] } },
    { id: "day", text: ["切到“一天的量”：40 页图纸、300 页文字，图纸占了全部词元的百分之几？再把图纸加到 200 页看一看。",
                        "Switch to the daily scene: with 40 drawings and 300 text pages, what share of all tokens is the drawings? Then raise the drawings to 200."],
      demo: { scene: "mix", set: { pages: 200 }, press: [] } },
  ],
  think: ["为什么把分辨率提高一倍，注意力的代价是十六倍而不是四倍？（提示：词元数先按平方涨，注意力再按词元数的平方涨。）",
          "Why does doubling the resolution cost sixteen times more attention rather than four? (Tokens grow as the square; attention grows as the square of the tokens.)"],

  D_MODEL: 4096, LAYERS: 32, DPI: 300, A4W: 2480, A4H: 3508, CHAR_MM: 3,
  tokensOf(res, patch, merge) { const n = Math.floor(res / patch); return Math.floor(n * n / (merge * merge)); },
  calc(api) {
    const p = api.p, key = [p.res, p.patch, p.merge, p.tile, p.pages, p.textPages].join(",");
    if (this._c && this._c.key === key) return this._c.val;
    const perTile = this.tokensOf(p.tile || 448, p.patch, p.merge);
    let tiles = 0, tok;
    if (p.tile > 0) {
      tiles = Math.min(40, Math.max(1, Math.round(this.A4W / p.tile)) * Math.max(1, Math.round(this.A4H / p.tile)));
      tok = (tiles + 1) * perTile;                       // 加一张缩略图
    } else {
      tok = this.tokensOf(p.res, p.patch, p.merge);
    }
    const charPx = this.CHAR_MM / 25.4 * this.DPI;        // 原图上一个尺寸数字有多高
    const shown = p.tile > 0 ? charPx : charPx * p.res / this.A4H;   // 切片保持原分辨率；整页缩小则按比例缩
    const attn = 2 * this.LAYERS * tok * tok * this.D_MODEL;
    const kvPerTok = 2 * 2 * this.D_MODEL * this.LAYERS / 8;   // 分组查询注意力按 8 组（9.4 节）
    const textTok = 800;
    const dayImg = tok * p.pages, dayTxt = textTok * p.textPages;
    const val = { tok, tiles, perTile, charPx, shown, attn, kvMB: tok * kvPerTok / 1e6,
                  dayImg, dayTxt, share: dayImg / Math.max(dayImg + dayTxt, 1) * 100,
                  dayKvGB: (dayImg + dayTxt) * kvPerTok / 1e9, textTok,
                  readable: shown >= 8 };
    this._c = { key, val };
    return val;
  },
  reset(api, s) { this._c = null; },
  readouts(api, s) {
    const p = api.p, c = this.calc(api);
    if (api.scene === "page" && p.tile === 0) api.done("shrink");
    if (api.scene === "page" && p.tile === 448) api.done("tiles");
    if (api.scene === "page" && p.merge >= 2) api.done("merge2");
    if (api.scene === "mix" && p.pages >= 200) api.done("day");
    if (api.scene === "page") {
      return [[["这一页的词元数", "tokens for this page"], String(c.tok)],
              [["切了几片（含缩略图）", "tiles (plus thumbnail)"], p.tile > 0 ? String(c.tiles + 1) : "—"],
              [["每片多少词元", "tokens per tile"], p.tile > 0 ? String(c.perTile) : "—"],
              [["尺寸数字在模型眼里有几个像素高", "pixels per dimension label"], c.shown.toFixed(1)],
              [["读得出吗", "readable?"], c.readable ? api.T("读得出", "yes") : api.T("读不出", "no")],
              [["注意力两项的乘加", "attention MACs"], (c.attn / 1e12).toFixed(2) + " T"],
              [["这一页的键值缓存", "KV cache for this page"], c.kvMB.toFixed(0) + " MB"]];
    }
    return [[["一页图纸的词元", "tokens per drawing"], String(c.tok)],
            [["一页文字的词元", "tokens per text page"], String(c.textTok)],
            [["一天的图纸词元", "drawing tokens per day"], (c.dayImg / 1e6).toFixed(2) + " M"],
            [["一天的文字词元", "text tokens per day"], (c.dayTxt / 1e6).toFixed(2) + " M"],
            [["图纸占全部词元的比例", "drawings' share"], c.share.toFixed(1) + "%"],
            [["一天全部词元的键值缓存", "KV cache if all kept"], c.dayKvGB.toFixed(1) + " GB"]];
  },
  draw(api, s) {
    const { w, h } = api, c = this.calc(api), p = api.p;
    const x0 = 70, y0 = 28, pw = w - x0 - 40, ph = h - y0 - 46;
    if (api.scene === "page") {
      // 画一页 A4 与它的切片
      const scale = Math.min(ph / this.A4H, pw / 2 / this.A4W) * 0.95;
      const W = this.A4W * scale, H = this.A4H * scale, ox = x0 + pw / 4 - W / 2, oy = y0 + (ph - H) / 2;
      api.rect(ox, oy, W, H, api.css("--panel"), api.css("--ink"), 1.5);
      api.label(api.T("A4 图纸 300 dpi", "A4 at 300 dpi"), ox, oy - 8, api.css("--muted"), 12);
      if (p.tile > 0) {
        const nx = Math.max(1, Math.round(this.A4W / p.tile)), ny = Math.max(1, Math.round(this.A4H / p.tile));
        for (let i = 1; i < nx; i++) api.line(ox + W * i / nx, oy, ox + W * i / nx, oy + H, api.css("--blue"), 1);
        for (let j = 1; j < ny; j++) api.line(ox, oy + H * j / ny, ox + W, oy + H * j / ny, api.css("--blue"), 1);
        api.label(api.T(`${nx}×${ny} 片，每片 ${c.perTile} 词元`, `${nx}x${ny} tiles, ${c.perTile} tokens each`),
                  ox, oy + H + 18, api.css("--blue"), 12);
      } else {
        api.label(api.T(`整页缩到 ${p.res}×${p.res}`, `whole page into ${p.res}x${p.res}`), ox, oy + H + 18, api.css("--red"), 12);
      }
      // 右边：一个尺寸数字在模型眼里有多大
      const bx = x0 + pw * 0.62, by = y0 + ph * 0.25, box = Math.max(3, Math.min(120, c.shown * 6));
      api.label(api.T("模型看到的尺寸数字（放大 6 倍画出）", "a dimension label as the model sees it (drawn 6x)"), bx - 30, by - 14, api.css("--muted"), 12);
      api.rect(bx, by, box * 2.2, box, null, c.readable ? api.css("--green") : api.css("--red"), 2);
      api.label("Ø30 ±0.02", bx + 4, by + box * 0.72, c.readable ? api.css("--green") : api.css("--red"), Math.max(7, Math.min(26, box * 0.7)));
      api.label(api.T(`${c.shown.toFixed(1)} 个像素高`, `${c.shown.toFixed(1)} px tall`), bx, by + box + 20, api.css("--ink"), 13);
      api.label(api.T(`这一页 ${c.tok} 个词元，注意力 ${(c.attn / 1e12).toFixed(1)} 万亿次乘加`,
                      `${c.tok} tokens, ${(c.attn / 1e12).toFixed(1)} T MACs`), bx, by + box + 44, api.css("--muted"), 12);
      return;
    }
    // 一天的量：两根柱子
    const total = c.dayImg + c.dayTxt, bw = pw / 4;
    const bars = [[api.T("图纸", "drawings"), c.dayImg, api.css("--blue")], [api.T("文字", "text"), c.dayTxt, api.css("--green")]];
    bars.forEach(([name, val, col], i) => {
      const hgt = ph * (val / Math.max(total, 1));
      const bxx = x0 + pw * (0.2 + 0.35 * i);
      api.rect(bxx, y0 + ph - hgt, bw, hgt, col, null, 0);
      api.label(name, bxx + bw / 4, y0 + ph + 16, api.css("--muted"), 12);
      api.label((val / 1e6).toFixed(2) + " M", bxx, y0 + ph - hgt - 8, col, 12);
    });
    api.line(x0, y0 + ph, x0 + pw, y0 + ph, api.css("--grid"), 1);
    api.label(api.T(`图纸占 ${c.share.toFixed(1)}%，一天的键值缓存 ${c.dayKvGB.toFixed(1)} GB`,
                    `drawings are ${c.share.toFixed(1)}%; a day of KV cache is ${c.dayKvGB.toFixed(1)} GB`),
              x0, h - 12, api.css("--ink"), 13);
  },
});
