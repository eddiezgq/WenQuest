// 《数字集成电路设计》第 1 章教材实验（textbook/dic/ch01/lab/lab1_N.js）的生成器。
// 教材的实验平台要求每个实验是一个自足的 WQ.lab({...}) 程序；为了全书只有一份器件模型，这里把
// labs/micro/kit/models/mos.js（模型）和 params.json（参数）嵌进每个实验，再接上 labs/micro/textbook/lab1_N.body.js。
// 用法：node labs/micro/tools/textbook_labs.js          （build.js 会自动运行；--check 只检查是否最新）
const fs = require('fs'), path = require('path');
const root = path.resolve(__dirname, '../../..');
const kit = path.join(root, 'labs/micro/kit/models');
const mos = fs.readFileSync(path.join(kit, 'mos.js'), 'utf8');
const params = JSON.stringify(JSON.parse(fs.readFileSync(path.join(kit, 'params.json'), 'utf8')));
const src = path.join(root, 'labs/micro/textbook');
const out = path.join(root, 'textbook/dic/ch01/lab');
const check = process.argv.includes('--check');
let stale = [];
for (const f of fs.readdirSync(src).filter((x) => /^lab1_\d\.body\.js$/.test(x)).sort()) {
  const n = f.match(/lab1_(\d)/)[1];
  const body = fs.readFileSync(path.join(src, f), 'utf8');
  const code = `// 由 labs/micro/tools/textbook_labs.js 生成，不要手改：改 labs/micro/textbook/${f}、模型 mos.js 或参数 params.json 后重新运行。
// 器件模型与参数（与书中程序 conventions/mos.py 一一对应，构建时比对）
const M1_${n} = (function () {
  var module, self = {};
${mos.replace(/^/gm, '  ').replace(/\s+$/, '')}
  return self.WQMos.create(${params});
})();
${body}`;
  const target = path.join(out, `lab1_${n}.js`);
  if (check) { if (!fs.existsSync(target) || fs.readFileSync(target, 'utf8') !== code) stale.push(`lab1_${n}.js`); }
  else { fs.mkdirSync(out, { recursive: true }); fs.writeFileSync(target, code); console.log('写出', path.relative(root, target)); }
}
if (check && stale.length) { console.error('教材实验不是最新的：' + stale.join('、') + '（运行 node labs/micro/tools/textbook_labs.js）'); process.exit(1); }
