// G 代码解析成刀位点 [x, y, z, 是否快移]，规则与 freecad/wq_cam_keyway.py 的 parse() 相同
export function parseGcode(text) {
  const pos = { X: 0, Y: 0, Z: 0 };
  const pts = [];
  for (const raw of text.split(/\r?\n/)) {
    const line = raw.split('(')[0].trim().toUpperCase();
    if (!line || line === '%') continue;
    const words = line.split(/\s+/);
    const g = words.find((w) => ['G00', 'G01', 'G0', 'G1'].includes(w));
    if (!g) continue;
    for (const w of words) if (w[0] in pos) pos[w[0]] = parseFloat(w.slice(1));
    pts.push([pos.X, pos.Y, pos.Z, g === 'G00' || g === 'G0']);
  }
  return pts;
}
