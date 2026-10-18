// 第 39 轮：用教材共用库 lockstitch-kit.js 算一组配置，输出 JSON，给 test_sewcore.py 与 Python 版逐项对数。
// 用法：node sewkit_dump.js <lockstitch-kit.js> < cases.json
const fs = require('fs');
require(require('path').resolve(process.argv[2]));
const K = globalThis.WQLS;
const cases = JSON.parse(fs.readFileSync(0, 'utf8'));
const out = cases.map(c => {
  const t = K.machine.trial(c, 30, 7), ev = t.ev;
  const core = K.timing.core({dh: c.dh || 0, dt: c.dt || 0, dT: c.dT || 0});
  const R = K.takeup.compute({mode: 'link', u: c.u || 0, t: 1.5, s: 3, phc: 206, rpm: 5000, lk: Object.assign({}, K.takeup.LK0)}, null);
  return {faults: ev.faults.map(f => f.key), catch: ev.catch, fmax: ev.fmax, res: t.res,
    hook: {fc: ev.hook.fc, h: ev.hook.h, D: ev.hook.D, g: ev.hook.g, wAt: ev.hook.wAt},
    supply: {k: ev.supply.k, neg: ev.supply.neg, margin: ev.supply.margin, pre: ev.supply.pre},
    tension: {z: ev.tension.z, peak: ev.tension.peak, shrink: ev.tension.shrink},
    feed: {drag: ev.feed.drag, back: ev.feed.back, eps: ev.feed.eps, ply: ev.feed.ply, net: ev.feed.net},
    core: {margin: core.margin, pre: core.pre, neg: core.neg, rc: core.rc, drag: core.F.drag, feedrise: core.feedrise, ok: core.ok},
    takeup: {top: R.top, bot: R.bot, fin: R.fin, margin: R.margin, waste: R.waste, pre: R.pre, neg: R.neg, Smax: R.Smax, acc: R.acc, mu: R.mu}};
});
process.stdout.write(JSON.stringify({PHC0: K.needle.PHC0, FE: K.feed.FE, cases: out}));
