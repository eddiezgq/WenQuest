<script setup>
// Clearance and groove position dimension chain (round 64, plan section 二十, part 2): sizes with deviations →
// clearance, contact angle, axial play, standout by extremes, statistics and Monte Carlo side by side.
import { computed, reactive, ref } from 'vue'
import { api } from '../api'
import { t, lang } from '../i18n'
import { result as design } from '../store'

const KEY = 'wqbearing-tolerance'
const ROWS = ['di', 'do', 'Dw', 'ri', 'ro', 'ai', 'ao']
const blank = () => ({ rows: Object.fromEntries(ROWS.map((k) => [k, { nom: null, es: null, ei: null }])), dist: 'normal', n: 100000, tmin: null, tmax: null, fict: false })
const saved = (() => { try { return JSON.parse(localStorage.getItem(KEY) || 'null') } catch { return null } })()
const f = reactive(saved || blank())
const out = ref(null), err = ref(null), busy = ref(false)
function keep() { try { localStorage.setItem(KEY, JSON.stringify(f)) } catch { /* private mode */ } }
const num = (x) => (x === null || x === '' || x === undefined ? null : Number(x))

function fromDesign() {
  const g = design.value?.geometry
  if (!g || !(['deep_groove', 'angular'].includes(g.type) || g.flex)) { err.value = { message: t('tolNeedBall'), zh: t('tolNeedBall') }; return }
  const r6 = (x) => Math.round(x * 1e6) / 1e6
  Object.assign(f.rows.di, { nom: r6(g.di) }); Object.assign(f.rows.do, { nom: r6(g.do) }); Object.assign(f.rows.Dw, { nom: r6(g.Dw) })
  Object.assign(f.rows.ri, { nom: r6(g.fi * g.Dw) }); Object.assign(f.rows.ro, { nom: r6(g.fo * g.Dw) })
  f.fict = false; err.value = null; keep()
}
function demo() {  // made-up deviations to try the page with (µm)
  fromDesign()
  if (err.value) return
  const dev = { di: [4, -4], do: [4, -4], Dw: [0.5, -0.5], ri: [10, -10], ro: [10, -10] }
  for (const [k, [es, ei]] of Object.entries(dev)) Object.assign(f.rows[k], { es, ei })
  f.fict = true; keep()
}
async function go() {
  busy.value = true; keep()
  const spec = {}
  for (const k of ROWS) {
    const r = f.rows[k]
    if (['ai', 'ao'].includes(k) && num(r.nom) == null) continue
    spec[k] = { nom: num(r.nom), es: num(r.es) == null ? null : num(r.es) / 1000, ei: num(r.ei) == null ? null : num(r.ei) / 1000 }
  }
  const target = (num(f.tmin) != null || num(f.tmax) != null) ? { Pd: { min: num(f.tmin) == null ? null : num(f.tmin) / 1000, max: num(f.tmax) == null ? null : num(f.tmax) / 1000 } } : null
  try { out.value = await api('/tolerance', { spec, n: num(f.n) || 100000, dist: f.dist, target }); err.value = null } catch (e) { err.value = e; out.value = null } finally { busy.value = false }
}
// rows of the result table: µm for lengths, degrees for the angle
const OUT = [['Pd', 'tolPd', 1000, 'µm', 1], ['alpha0', 'tolA', 1, '°', 3], ['Ga', 'tolGa', 1000, 'µm', 1], ['s', 'tolS', 1000, 'µm', 1]]
const table = computed(() => {
  const o = out.value
  if (!o) return []
  return OUT.map(([k, key, m, u, dp]) => {
    const f2 = (x) => (x == null ? '—' : (x * m).toFixed(dp))
    const e = o.extremes[k], s = o.statistical[k], mc = o.montecarlo[k]
    return { key, u, nom: f2(o.nominal[k]), ext: e ? `${f2(e.min)} … ${f2(e.max)}` : '—', st: s ? `${f2(s.lo)} … ${f2(s.hi)}` : '—',
      mc: mc ? `${f2(mc.p_lo)} … ${f2(mc.p_hi)}` : '—', mean: mc ? f2(mc.mean) : '—' }
  })
})
const share = computed(() => {
  const s = out.value?.sensitivity?.Pd
  if (!s) return []
  return Object.entries(s).map(([k, v]) => ({ k, p: v.share * 100, d: v.dfdx })).sort((a, b) => b.p - a.p)
})
const W = 520, H = 160, PL = 34, PB = 26, PR = 16
const hist = computed(() => {
  const mc = out.value?.montecarlo?.Pd
  if (!mc) return null
  const m = Math.max(...mc.hist, 1), n = mc.hist.length, bw = (W - PL - PR) / n
  const lo = mc.edges[0] * 1000, hi = mc.edges[n] * 1000
  const X = (v) => PL + ((v - lo) / (hi - lo)) * (W - PL - PR), Y = (c) => 8 + (1 - c / m) * (H - 8 - PB)
  const lines = []
  if (num(f.tmin) != null) lines.push(X(num(f.tmin)))
  if (num(f.tmax) != null) lines.push(X(num(f.tmax)))
  return { bars: mc.hist.map((c, k) => ({ x: PL + k * bw + 1, y: Y(c), w: bw - 2, h: H - PB - Y(c) })), base: H - PB,
    ticks: [lo, (lo + hi) / 2, hi].map((v) => ({ x: X(v), lab: v.toFixed(1) })), lines: lines.filter((x) => x >= PL && x <= W - PR) }
})
const pct = (x) => (x * 100).toFixed(x < 0.01 ? 3 : 2) + ' %'
</script>

<template>
  <div class="asm">
    <aside class="edit"><div class="pane">
      <h2>{{ t('tolTitle') }}</h2>
      <p class="hint">{{ t('tolIntro') }}</p>
      <div class="tolwrap"><table class="casetbl tol">
        <thead><tr><th></th><th>{{ t('tolNom') }} mm</th><th>{{ t('tolEs') }} µm</th><th>{{ t('tolEi') }} µm</th></tr></thead>
        <tbody><tr v-for="k in ROWS" :key="k"><th :title="t('tol_' + k)">{{ t('tol_' + k) }}</th>
          <td><input v-model.number="f.rows[k].nom" type="number" step="any" @change="keep"></td>
          <td><input v-model.number="f.rows[k].es" type="number" step="any" @change="keep"></td>
          <td><input v-model.number="f.rows[k].ei" type="number" step="any" @change="keep"></td></tr></tbody>
      </table></div>
      <p class="hint">{{ t('tolPosHint') }}</p>
      <label class="num"><span class="lab">{{ t('tolDist') }}</span><select v-model="f.dist" @change="keep"><option value="normal">{{ t('tolNormal') }}</option><option value="uniform">{{ t('tolUniform') }}</option></select></label>
      <label class="num"><span class="lab">{{ t('tolN') }}</span><span class="box"><input v-model.number="f.n" type="number" step="1000" @change="keep"><i></i></span></label>
      <label class="num"><span class="lab">{{ t('tolTmin') }}<small>{{ t('tolTHint') }}</small></span><span class="box"><input v-model.number="f.tmin" type="number" step="any" @change="keep"><i>µm</i></span></label>
      <label class="num"><span class="lab">{{ t('tolTmax') }}</span><span class="box"><input v-model.number="f.tmax" type="number" step="any" @change="keep"><i>µm</i></span></label>
      <div class="btns"><button type="button" class="accent" :disabled="busy" @click="go">{{ busy ? t('busy') : t('tolRun') }}</button>
        <button type="button" class="ghost" @click="fromDesign">{{ t('tolFromDesign') }}</button>
        <button type="button" class="ghost" @click="demo">{{ t('tolDemo') }}</button></div>
      <p v-if="f.fict" class="fict">{{ t('tolDemoNote') }}</p>
    </div></aside>
    <section class="stage">
      <p v-if="err" class="err" role="alert">{{ t('error') }}：{{ lang === 'zh' ? err.zh || err.message : err.message }}</p>
      <p v-if="!out && !err" class="hint">{{ t('tolEmpty') }}</p>
      <template v-if="out">
        <p v-if="f.fict" class="fict">{{ t('tolDemoNote') }}</p>
        <div class="tblwrap"><table class="casetbl">
          <thead><tr><th></th><th>{{ t('tolNom') }}</th><th>{{ t('tolExt') }}</th><th>{{ t('tolStat') }}</th><th>{{ t('tolMc') }}</th><th>{{ t('tolMean') }}</th></tr></thead>
          <tbody><tr v-for="r in table" :key="r.key"><th>{{ t(r.key) }} <small>{{ r.u }}</small></th><td class="mono">{{ r.nom }}</td><td class="mono">{{ r.ext }}</td><td class="mono">{{ r.st }}</td><td class="mono">{{ r.mc }}</td><td class="mono">{{ r.mean }}</td></tr></tbody>
        </table></div>
        <p class="hint">{{ t('tolNote').replace('{n}', out.montecarlo.n).replace('{seed}', out.montecarlo.seed) }}</p>
        <p v-if="out.interference_possible" class="err">{{ t('tolInterf').replace('{p}', pct(out.montecarlo.interference)) }}</p>
        <p v-if="out.montecarlo.Pd && out.montecarlo.Pd.outside != null" class="mono">{{ t('tolOutside').replace('{p}', pct(out.montecarlo.Pd.outside)) }}</p>
        <figure v-if="hist" class="curve">
          <figcaption>{{ t('tolHist') }}</figcaption>
          <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('tolHist')">
            <rect v-for="(b, k) in hist.bars" :key="k" :x="b.x" :y="b.y" :width="b.w" :height="b.h" class="bar-a" />
            <line v-for="(x, k) in hist.lines" :key="'l' + k" :x1="x" :x2="x" y1="4" :y2="hist.base" class="contact" />
            <line :x1="PL" :x2="W - PR" :y1="hist.base" :y2="hist.base" class="dim" />
            <text v-for="tk in hist.ticks" :key="tk.lab" :x="tk.x" :y="hist.base + 16" class="ann mid">{{ tk.lab }}</text>
          </svg>
        </figure>
        <section>
          <h3>{{ t('tolShare') }}</h3>
          <table class="casetbl"><thead><tr><th></th><th>{{ t('tolShareCol') }}</th><th>∂Pd/∂x</th></tr></thead>
            <tbody><tr v-for="s in share" :key="s.k"><th>{{ t('tol_' + s.k) }}</th><td class="mono">{{ s.p.toFixed(1) }} %</td><td class="mono">{{ s.d.toFixed(3) }}</td></tr></tbody></table>
        </section>
      </template>
    </section>
  </div>
</template>

<style scoped>
.tolwrap { overflow-x: auto; }
.tol input { width: 100%; min-width: 0; font-size: 12px; }
.tol th { font-weight: 500; font-size: 12px; white-space: normal; }
.tol td { padding: 2px 3px; }
th small { color: var(--muted); font-weight: 400; }
</style>
