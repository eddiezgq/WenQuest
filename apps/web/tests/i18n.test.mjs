// Every UI string must exist in both languages, and every key used in the pages must be defined.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync, statSync } from "node:fs";
import { join } from "node:path";

const src = readFileSync(new URL("../src/i18n.ts", import.meta.url), "utf8");
const block = (name) => {
  const start = src.indexOf(`  ${name}: {`);
  const end = src.indexOf("\n  },", start);
  return new Set([...src.slice(start, end).matchAll(/"([a-zA-Z_.]+)":/g)].map((m) => m[1]));
};
const zh = block("zh");
const en = block("en");

test("zh and en define the same keys", () => {
  assert.ok(zh.size > 30);
  assert.deepEqual([...zh].filter((k) => !en.has(k)), []);
  assert.deepEqual([...en].filter((k) => !zh.has(k)), []);
});

test("every t('...') key used in the app exists", () => {
  const files = [];
  const walk = (d) => readdirSync(d).forEach((f) => {
    const p = join(d, f);
    statSync(p).isDirectory() ? walk(p) : /\.(vue|ts)$/.test(f) && files.push(p);
  });
  walk(new URL("../src", import.meta.url).pathname);
  const missing = [];
  for (const f of files) {
    for (const m of readFileSync(f, "utf8").matchAll(/\bt\(\s*["']([a-zA-Z_.]+)["']/g)) {
      if (!m[1].endsWith(".") && !zh.has(m[1])) missing.push(`${f}: ${m[1]}`);
    }
  }
  assert.deepEqual(missing, []);
});

test("every gateway error code has a translation", () => {
  const gw = readFileSync(new URL("../../../services/gateway/app/moodle.py", import.meta.url), "utf8");
  const codes = new Set([...gw.matchAll(/\("([a-z_]+)", \d{3}\)/g)].map((m) => m[1]));
  const untranslated = [...codes].filter((c) => !zh.has(`error.${c}`) && c !== "engine_error");
  assert.deepEqual(untranslated, []);
});
