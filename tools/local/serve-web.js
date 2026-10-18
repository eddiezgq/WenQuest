// Local stand-in for the web container's Caddy: static build + /api proxy to the gateway.
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = '/home/claude/wenquest/apps/web/dist/build/h5';
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.mjs': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.json': 'application/json', '.woff2': 'font/woff2' };
http.createServer((req, res) => {
  if (req.url.startsWith('/api/')) {
    const p = http.request({ host: '127.0.0.1', port: 8090, path: req.url, method: req.method, headers: req.headers }, (r) => { res.writeHead(r.statusCode, r.headers); r.pipe(res); });
    p.on('error', () => { res.writeHead(502); res.end(); });
    return req.pipe(p);
  }
  // /vendor/ (three.js, fonts) is served from site/vendor like the production Caddy does (round 39: the 3D prototype needs it)
  if (req.url.startsWith('/vendor/')) {
    const V = '/home/claude/wenquest/site';
    const g = path.join(V, decodeURIComponent(req.url.split('?')[0]));
    if (g.startsWith(V + '/vendor/') && fs.existsSync(g) && fs.statSync(g).isFile()) {
      res.writeHead(200, { 'Content-Type': TYPES[path.extname(g)] || 'application/octet-stream' });
      return fs.createReadStream(g).pipe(res);
    }
    res.writeHead(404); return res.end();
  }
  let f = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) f = path.join(ROOT, 'index.html');
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(8088);
