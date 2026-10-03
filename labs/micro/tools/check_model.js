// RM2：JS 模型与 model.py 的 ref.json 逐项比对，相对误差 > 0.5% 则退出码 1
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '../../..');
const P = JSON.parse(fs.readFileSync(path.join(root, 'labs/micro/kit/models/params.json'), 'utf8'));
const ref = JSON.parse(fs.readFileSync(path.join(root, 'samples/数字集成电路设计/生成脚本/ref.json'), 'utf8'));
const js = require('../kit/models/mos.js').create(P).reference();
let n = 0, bad = 0;
(function walk(a, b, k) {
  if (typeof a === 'number') {
    n++; const e = Math.abs(a - b) / Math.max(Math.abs(a), 1e-30);
    if (!(e <= 0.005)) { bad++; console.log('差异', k, a, b, (e * 100).toFixed(3) + '%'); }
    return;
  }
  for (const key of Object.keys(a)) walk(a[key], b[key], k + '.' + key);
})(ref, js, 'ref');
console.log(`比对 ${n} 项，超差 ${bad} 项`);
process.exit(bad ? 1 : 0);
