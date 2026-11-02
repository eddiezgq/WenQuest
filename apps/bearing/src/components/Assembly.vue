<script setup>
// 合套选配 (round 64, step 5): measured inner rings, outer rings and ball groups into bearings whose radial
// clearance is in range. Piece by piece (most sets, clearances nearest the target) beside the usual size classes.
import { computed, reactive, ref } from 'vue'
import { api, saveText } from '../api'
import { t, lang } from '../i18n'
import { result as design } from '../store'

const KEY = 'wqbearing-assembly'
const saved = (() => { try { return JSON.parse(localStorage.getItem(KEY) || 'null') } catch { return null } })()
const f = reactive(saved || { Z: null, Pmin: null, Pmax: null, Pt: null, h: null, inner: '', outer: '', groups: '', synthetic: false })
const out = ref(null), err = ref(null), busy = ref(false)
function keep() { try { localStorage.setItem(KEY, JSON.stringify(f)) } catch { /* private mode */ } }

const lines = (txt) => txt.split('\n').map((l) => l.trim()).filter(Boolean).map((l) => l.split(/[\s,;\t]+/))
const rings = (txt) => lines(txt).map((r) => (r.length > 1 ? { id: r[0], d: Number(r[1]) } : { d: Number(r[0]) }))
const groups = (txt) => lines(txt).map((r) => ({ id: r[0], Dw: Number(r[1]), qty: Number(r[2]) }))
const um = (x) => (x == null || x === '' ? null : Number(x) / 1000)

async function synth() {
  const g = design.value?.geometry
  if (!g || !['deep_groove', 'angular'].includes(g.type)) { err.value = { message: t('asmNeedBall'), zh: t('asmNeedBall') }; return }
  try {
    const d = await api('/assembly/synthetic', { n: 100, di: g.di, do: g.do, Dw: g.Dw, Z: g.Z })
    f.inner = d.inner.map((r) => `${r.id}, ${r.d}`).join('\n')
    f.outer = d.outer.map((r) => `${r.id}, ${r.d}`).join('\n')
    f.groups = d.groups.map((r) => `${r.id}, ${r.Dw}, ${r.qty}`).join('\n')
    f.Z = d.Z; f.synthetic = true
    if (f.Pmin == null && design.value?.geometry?.type === 'deep_groove') {
      const pd = (g.do - g.di - 2 * g.Dw) * 1000
      f.Pmin = Math.round(pd - 6); f.Pmax = Math.round(pd + 6)
    }
    keep(); err.value = null
  } catch (e) { err.value = e }
}
async function go() {
  busy.value = true; keep()
  try {
    out.value = await api('/assembly', { Z: f.Z, P_min: um(f.Pmin), P_max: um(f.Pmax), P_target: um(f.Pt), h: um(f.h),
      inner: rings(f.inner), outer: rings(f.outer), groups: groups(f.groups) })
    err.value = null
  } catch (e) { err.value = e; out.value = null } finally { busy.value = false }
}
function edited() { f.synthetic = false; keep() }
function csv() {
  const rows = [['inner', 'outer', 'group', 'clearance_um'], ...out.value.piecewise.sets.map((s) => [s.inner, s.outer, s.group, (s.P * 1000).toFixed(2)])]
  saveText('selective-assembly.csv', rows.map((r) => r.join(',')).join('\n'), 'text/csv')
}
// clearance histogram (µm), piece by piece against the classes
const W = 520, H = 170, PL = 34, PB = 26, PR = 24
const hist = computed(() => {
  const o = out.value
  if (!o || !o.piecewise.count) return null
  const lo = o.P_min * 1000, hi = o.P_max * 1000, n = 12, w = (hi - lo) / n
  const bin = (sets) => { const c = Array(n).fill(0); for (const s of sets) { const k = Math.min(n - 1, Math.max(0, Math.floor((s.P * 1000 - lo) / w))); if (s.ok !== false) c[k]++ } return c }
  const a = bin(o.piecewise.sets), b = bin(o.grouped.sets)
  const m = Math.max(...a, ...b, 1)
  const bw = (W - PL - PR) / n
  const X = (k) => PL + k * bw, Y = (v) => 8 + (1 - v / m) * (H - 8 - PB)
  return { a: a.map((v, k) => ({ x: X(k) + 2, y: Y(v), h: H - PB - Y(v), w: bw / 2 - 3 })),
    b: b.map((v, k) => ({ x: X(k) + bw / 2, y: Y(v), h: H - PB - Y(v), w: bw / 2 - 3 })),
    ticks: [0, n / 2, n].map((k) => ({ x: X(k), lab: (lo + k * w).toFixed(1) })), tx: Y(o.P_target * 1000), m, base: H - PB,
    target: PL + ((o.P_target * 1000 - lo) / (hi - lo)) * (W - PL - PR) }
})
const fmtUm = (x) => (x * 1000).toFixed(1)
</script>

<template>
  <div class="asm">
    <aside class="edit"><div class="pane">
      <h2>{{ t('asmTitle') }}</h2>
      <p class="hint">{{ t('asmIntro') }}</p>
      <label class="num"><span class="lab">{{ t('asmZ') }}</span><span class="box"><input v-model.number="f.Z" type="number" step="1" @change="keep"><i></i></span></label>
      <label class="num"><span class="lab">{{ t('asmPmin') }}</span><span class="box"><input v-model.number="f.Pmin" type="number" step="any" @change="keep"><i>µm</i></span></label>
      <label class="num"><span class="lab">{{ t('asmPmax') }}</span><span class="box"><input v-model.number="f.Pmax" type="number" step="any" @change="keep"><i>µm</i></span></label>
      <label class="num"><span class="lab">{{ t('asmPt') }}<small>{{ t('asmPtHint') }}</small></span><span class="box"><input v-model.number="f.Pt" type="number" step="any" @change="keep"><i>µm</i></span></label>
      <label class="num"><span class="lab">{{ t('asmH') }}<small>{{ t('asmHHint') }}</small></span><span class="box"><input v-model.number="f.h" type="number" step="any" @change="keep"><i>µm</i></span></label>
      <label class="area"><span class="lab">{{ t('asmInner') }}<small>{{ t('asmRingHint') }}</small></span><textarea v-model="f.inner" rows="6" spellcheck="false" @input="edited"></textarea></label>
      <label class="area"><span class="lab">{{ t('asmOuter') }}</span><textarea v-model="f.outer" rows="6" spellcheck="false" @input="edited"></textarea></label>
      <label class="area"><span class="lab">{{ t('asmGroups') }}<small>{{ t('asmGroupHint') }}</small></span><textarea v-model="f.groups" rows="4" spellcheck="false" @input="edited"></textarea></label>
      <div class="btns"><button type="button" class="accent" :disabled="busy" @click="go">{{ busy ? t('busy') : t('asmRun') }}</button>
        <button type="button" class="ghost" @click="synth">{{ t('asmSynth') }}</button></div>
      <p v-if="f.synthetic" class="fict">{{ t('asmSynthNote') }}</p>
    </div></aside>

    <section class="stage">
      <p v-if="err" class="err" role="alert">{{ t('error') }}：{{ lang === 'zh' ? err.zh || err.message : err.message }}</p>
      <p v-if="!out && !err" class="hint">{{ t('asmEmpty') }}</p>
      <template v-if="out">
        <p v-if="f.synthetic" class="fict">{{ t('asmSynthNote') }}</p>
        <div class="cmp">
          <div class="big"><b class="mono">{{ out.piecewise.count }}</b><span>{{ t('asmPiece') }}</span>
            <small>{{ out.piecewise.count >= out.piecewise.upper ? t('asmMaxReached') : out.piecewise.optimal ? t('asmOptimal') : t('asmNotProven') }}</small></div>
          <div class="big alt"><b class="mono">{{ out.grouped.count }}</b><span>{{ t('asmGrouped') }}</span>
            <small>{{ t('asmOut').replace('{n}', out.grouped.out_of_range) }}</small></div>
          <div class="facts"><span>{{ t('asmOf').replace('{i}', out.n_inner).replace('{o}', out.n_outer) }}</span>
            <span v-if="out.stats">{{ t('asmStats') }} {{ fmtUm(out.stats.mean) }} ± {{ fmtUm(out.stats.std) }} µm</span></div>
        </div>
        <figure v-if="hist" class="curve">
          <figcaption>{{ t('asmHist') }} <span class="key in">{{ t('asmPiece') }}</span> <span class="key out">{{ t('asmGrouped') }}</span></figcaption>
          <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('asmHist')">
            <rect v-for="(r, k) in hist.a" :key="'a' + k" :x="r.x" :y="r.y" :width="r.w" :height="r.h" class="bar-a" />
            <rect v-for="(r, k) in hist.b" :key="'b' + k" :x="r.x" :y="r.y" :width="r.w" :height="r.h" class="bar-b" />
            <line :x1="hist.target" :x2="hist.target" y1="4" :y2="hist.base" class="contact" />
            <line :x1="PL" :x2="W - PR" :y1="hist.base" :y2="hist.base" class="dim" />
            <text v-for="tk in hist.ticks" :key="tk.lab" :x="tk.x" :y="hist.base + 16" class="ann mid">{{ tk.lab }}</text>
          </svg>
        </figure>
        <div class="asmgrid">
          <section>
            <h3>{{ t('asmGroupUse') }}</h3>
            <table class="casetbl"><thead><tr><th>{{ t('asmGroup') }}</th><th>Dw mm</th><th>{{ t('asmQty') }}</th><th>{{ t('asmUsed') }}</th></tr></thead>
              <tbody><tr v-for="g in out.groups" :key="g.id"><td>{{ g.id }}</td><td class="mono">{{ g.Dw.toFixed(4) }}</td><td class="mono">{{ g.qty }}</td><td class="mono">{{ g.used }} / {{ g.sets_max }}</td></tr></tbody></table>
          </section>
          <section v-if="out.left_inner.length || out.left_outer.length">
            <h3>{{ t('asmLeft') }}</h3>
            <ul class="left">
              <li v-for="x in out.left_inner" :key="'i' + x.id">{{ t('asmInnerOne') }} {{ x.id }}（{{ x.d }}）：{{ x.why === 'none' ? t('asmWhyNone') : t('asmWhyTaken') }}</li>
              <li v-for="x in out.left_outer" :key="'o' + x.id">{{ t('asmOuterOne') }} {{ x.id }}（{{ x.d }}）：{{ x.why === 'none' ? t('asmWhyNone') : t('asmWhyTaken') }}</li>
            </ul>
          </section>
        </div>
        <section>
          <h3>{{ t('asmSets') }} <button type="button" class="ghost" @click="csv">{{ t('asmCsv') }}</button></h3>
          <div class="tblwrap sets"><table class="casetbl"><thead><tr><th>#</th><th>{{ t('asmInnerOne') }}</th><th>{{ t('asmOuterOne') }}</th><th>{{ t('asmGroup') }}</th><th>{{ t('asmClear') }} µm</th></tr></thead>
            <tbody><tr v-for="(s, k) in out.piecewise.sets" :key="k"><td class="mono">{{ k + 1 }}</td><td>{{ s.inner }}</td><td>{{ s.outer }}</td><td>{{ s.group }}</td><td class="mono">{{ fmtUm(s.P) }}</td></tr></tbody></table></div>
        </section>
      </template>
    </section>
  </div>
</template>
