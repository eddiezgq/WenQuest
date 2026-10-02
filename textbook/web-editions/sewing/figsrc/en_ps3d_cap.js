const { chromium } = require('playwright');
const fs=require('fs');
(async () => {
  const [,, lang, out, setjson, w, h] = process.argv;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: +(w||1280), height: +(h||800) }, deviceScaleFactor: +(process.argv[7]||2) });
  await p.route(/cdnjs\.cloudflare\.com.*three.*\.js/, r => r.fulfill({body: fs.readFileSync('/home/claude/sm/node_modules/three/build/three.min.js'), contentType:'application/javascript'}));
  await p.route(/fonts\.(googleapis|gstatic)\.com/, r => r.fulfill({body:'', contentType:'text/css'}));
  await p.addInitScript(()=>{window.__still=true;}); const errs=[]; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file:///home/claude/sm/src/'+lang+'/labs/model-pattern.html#capture', { waitUntil: 'networkidle' });
  await p.waitForTimeout(800);
  await p.addStyleTag({content:'a[href="../index.html"]{display:none!important}'}); await p.evaluate(o=>window.__set(o), JSON.parse(setjson));
  await p.waitForTimeout(1500); if(process.argv[8]){ await p.evaluate(process.argv[8]); await p.waitForTimeout(200);}
  await p.screenshot({ path: out });
  console.log(JSON.stringify(errs));
  await b.close();
})();
