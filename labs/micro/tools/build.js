// 问渠微电子实验构建：先跑模型比对（RM2），再把组件库、模型、参数内联成单个 HTML（RM4）。
// 用法：node labs/micro/tools/build.js
const fs = require('fs'), path = require('path'), { execFileSync } = require('child_process');
const root = path.resolve(__dirname, '../../..');
const micro = path.join(root, 'labs/micro');

execFileSync('python3', [path.join(root, 'samples/数字集成电路设计/生成脚本/model.py')], { stdio: 'inherit' });
execFileSync('node', [path.join(micro, 'tools/check_model.js')], { stdio: 'inherit' });

const PAGES = [
  { src: 'dic-ch1/index.src.html', out: ['samples/数字集成电路设计/课程资料/第1章 CMOS反相器/虚拟实验/第1章虚拟实验（中英）.html', 'labs/micro/dic-ch1/index.html'] },
  { src: 'spice/index.src.html', out: ['labs/micro/spice/index.html'] },
  { src: 'verilog/index.src.html', out: ['labs/micro/verilog/index.html'] },
];

for (const p of PAGES) {
  const srcPath = path.join(micro, p.src), dir = path.dirname(srcPath);
  let html = fs.readFileSync(srcPath, 'utf8');
  html = html.replace(/<link rel="stylesheet" href="([^"]*kit[^"]+\.css)">/g, (_, f) => `<style>\n${fs.readFileSync(path.join(dir, f), 'utf8')}</style>`);
  html = html.replace(/<script src="([^"]*kit[^"]+\.js)"><\/script>/g, (_, f) => `<script>\n${fs.readFileSync(path.join(dir, f), 'utf8')}</script>`);
  const params = fs.readFileSync(path.join(micro, 'kit/models/params.json'), 'utf8');
  html = html.replace('<!--@params-->', `<script>window.WQ_PARAMS = ${params.trim()};</script>`);
  html = html.replace('/*@y2d*/', () => fs.readFileSync(path.join(micro, 'kit/vendor/y2d.min.js'), 'utf8'));
  if (/src="\.\.\/kit|href="\.\.\/kit/.test(html)) throw new Error('仍有未内联的组件库引用');
  for (const o of p.out) {
    const op = path.join(root, o);
    fs.mkdirSync(path.dirname(op), { recursive: true });
    fs.writeFileSync(op, html);
    console.log('写出', o, (html.length / 1024).toFixed(0) + ' KB');
  }
}
