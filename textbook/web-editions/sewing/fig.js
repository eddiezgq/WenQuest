// Usage: node fig.js in.html out.png   — renders the .fig element at 2x
const { chromium } = require('playwright'); const path=require('path');
(async()=>{const [,,inp,out]=process.argv;const b=await chromium.launch();
const p=await b.newPage({viewport:{width:1400,height:900},deviceScaleFactor:2});
await p.goto('file://'+path.resolve(inp));
if(/\.en\./.test(inp)) await p.addStyleTag({content:'@font-face{font-family:QFix;src:local("DejaVu Sans");unicode-range:U+2018-201D,U+2026}*{font-family:QFix,"Noto Sans CJK SC",sans-serif}.mono,code{font-family:"DejaVu Sans Mono",monospace!important}'});await p.waitForTimeout(300);
const el=await p.$('.fig')||await p.$('body');await el.screenshot({path:out});await b.close();console.log('ok',out);})();
