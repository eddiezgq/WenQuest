// 由表格的两列作图（第 122 轮实验报告首用；第 126 轮老师的网页文档共用）。只在 H5 上画（离屏 canvas，返回 PNG 的 base64）。

export interface ChartOpts { x: number; y: number; line: boolean; fit: boolean }
export interface ChartResult { ok: boolean; png: string; byRow: boolean; xLabel: string; yLabel: string; fit: { k: number; b: number } | null }

export const num = (c: string) => { const v = parseFloat(String(c).replace(/,/g, "").replace(/[−–]/g, "-")); return Number.isFinite(v) ? v : null; };

/** A table is read by columns; a one-row table like 表 1 (位置 1…10) is read along its row. */
export function drawChart(head: string[], rows: string[][], o: ChartOpts): ChartResult {
  const res: ChartResult = { ok: false, png: "", byRow: false, xLabel: "", yLabel: "", fit: null };
  // #ifdef H5
  let pts: [number, number][] = rows.map((r) => [num(r[o.x]), num(r[o.y])]).filter((p) => p[0] !== null && p[1] !== null) as [number, number][];
  let xLabel = head[o.x] || "", yLabel = head[o.y] || "";
  if (pts.length < 2 && rows.length === 1) {
    pts = head.map((h, j) => [num(h), num(rows[0][j])]).filter((p) => p[0] !== null && p[1] !== null) as [number, number][];
    xLabel = head[0] || ""; yLabel = rows[0][0] || "";
    res.byRow = true;
  }
  res.xLabel = xLabel; res.yLabel = yLabel;
  if (pts.length < 2) return res;
  res.ok = true;
  const cv = document.createElement("canvas");      // off-screen: uni-app's <canvas> resizes and clears itself
  cv.width = 640; cv.height = 420;
  const g = cv.getContext("2d")!;
  const W = cv.width, H = cv.height, L = 70, R = 20, T = 20, B = 50;
  g.fillStyle = "#fff"; g.fillRect(0, 0, W, H);
  const xs = pts.map((p) => p[0]), ys = pts.map((p) => p[1]);
  const pad = (a: number, b: number) => { const d = (b - a) || Math.abs(a) || 1; return [a - d * 0.08, b + d * 0.08]; };
  const [x0, x1] = pad(Math.min(...xs), Math.max(...xs)), [y0, y1] = pad(Math.min(...ys), Math.max(...ys));
  const X = (x: number) => L + (x - x0) / (x1 - x0) * (W - L - R), Y = (y: number) => H - B - (y - y0) / (y1 - y0) * (H - T - B);
  g.strokeStyle = "#333"; g.lineWidth = 1; g.beginPath(); g.moveTo(L, T); g.lineTo(L, H - B); g.lineTo(W - R, H - B); g.stroke();
  g.fillStyle = "#333"; g.font = "13px sans-serif"; g.textAlign = "center";
  // tick labels with enough decimals for the step (62.94 … 63.00 needs two)
  const dec = (a: number, b: number) => Math.min(6, Math.max(0, Math.ceil(-Math.log10((b - a) / 5)) + 1));
  const dx = dec(x0, x1), dy = dec(y0, y1);
  for (let i = 0; i <= 5; i++) {
    const xv = x0 + (x1 - x0) * i / 5, yv = y0 + (y1 - y0) * i / 5;
    g.fillText(xv.toFixed(dx), X(xv), H - B + 18);
    g.textAlign = "right"; g.fillText(yv.toFixed(dy), L - 6, Y(yv) + 4); g.textAlign = "center";
    g.strokeStyle = "#e5e5e5"; g.beginPath(); g.moveTo(L, Y(yv)); g.lineTo(W - R, Y(yv)); g.stroke();
  }
  g.fillText(xLabel, (L + W - R) / 2, H - 10);
  g.save(); g.translate(16, (T + H - B) / 2); g.rotate(-Math.PI / 2); g.fillText(yLabel, 0, 0); g.restore();
  const sorted = pts.slice().sort((a, b) => a[0] - b[0]);
  if (o.line) { g.strokeStyle = "#1f6f8b"; g.lineWidth = 1.5; g.beginPath(); sorted.forEach((p, i) => (i ? g.lineTo(X(p[0]), Y(p[1])) : g.moveTo(X(p[0]), Y(p[1])))); g.stroke(); }
  g.fillStyle = "#1f6f8b"; pts.forEach((p) => { g.beginPath(); g.arc(X(p[0]), Y(p[1]), 4, 0, Math.PI * 2); g.fill(); });
  if (o.fit && new Set(xs).size >= 2) {
    const n = pts.length, mx = xs.reduce((a, b) => a + b, 0) / n, my = ys.reduce((a, b) => a + b, 0) / n;
    let sxy = 0, sxx = 0; pts.forEach(([x, y]) => { sxy += (x - mx) * (y - my); sxx += (x - mx) * (x - mx); });
    const k = sxy / sxx, b = my - k * mx;
    g.strokeStyle = "#b8860b"; g.setLineDash([6, 4]); g.beginPath(); g.moveTo(X(x0), Y(k * x0 + b)); g.lineTo(X(x1), Y(k * x1 + b)); g.stroke(); g.setLineDash([]);
    res.fit = { k: +k.toPrecision(4), b: +b.toPrecision(4) };
  }
  res.png = cv.toDataURL("image/png").split(",")[1];
  // #endif
  return res;
}
