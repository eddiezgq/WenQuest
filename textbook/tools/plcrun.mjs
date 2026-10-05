// Run a PLC program of the book (第 18 轮): node plcrun.mjs < job.json > result.json
// job: { program: {st} | {decls, ladder}, io?: [...], plant?: "elevator" | ..., plantOpts?: {...}, cycle?: 10,
//        tests?: [test, ...], scenario?: {steps, faults, trace: [names], every?: ms, final?: [names]}, review?: true }
// The engine and the virtual machines are the platform's own (services/gateway/app/production/labkit), so the book's
// programs run exactly as in the students' lab.
import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
const require = createRequire(import.meta.url);
const KIT = new URL("../../services/gateway/app/production/labkit/", import.meta.url);
const P = require(new URL("plc.js", KIT).pathname);
const W = require(new URL("plants.js", KIT).pathname);

const job = JSON.parse(readFileSync(0, "utf8"));
const out = { ok: true, error: null, tests: [], review: [], scenario: null };
try {
  const plant = job.plant ? W[job.plant](job.plantOpts || {}) : null;
  const io = job.io || (plant && plant.io) || [];
  const rtOpts = Object.assign({ io, cycle: job.cycle || 10, filter: job.filter || 0 }, job.program);
  new P.Runtime(rtOpts);   // compile errors surface here
  for (const t of job.tests || []) {
    const r = P.runTest(rtOpts, plant, t);
    out.tests.push({ id: t.id, ok: r.ok, failures: r.failures.map((f) => f.msg), time: r.time, scans: r.scans });
    if (!r.ok) out.ok = false;
  }
  if (job.scenario) {
    const r = P.runTest(rtOpts, plant, Object.assign({ id: "scenario" }, job.scenario), { trace: job.scenario.trace || [], every: job.scenario.every, final: job.scenario.final });
    out.scenario = { ok: r.ok, failures: r.failures.map((f) => f.msg), time: r.time, trace: r.trace, log: r.log, final: r.final };
  }
  if (job.review) out.review = P.review(job.program, io);
} catch (e) {
  out.ok = false;
  out.error = (e.line ? `line ${e.line}: ` : "") + (e.message || String(e));
}
process.stdout.write(JSON.stringify(out));
