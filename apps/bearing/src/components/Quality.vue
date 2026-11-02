<script setup>
// 检测与 SPC (round 64, step 5): roundness and waviness of a raceway; control charts and process capability.
import { computed, reactive, ref } from 'vue'
import { api } from '../api'
import { t, lang } from '../i18n'
import LineChart from './LineChart.vue'

const KEY = 'wqbearing-quality'
const saved = (() => { try { return JSON.parse(localStorage.getItem(KEY) || 'null') } catch { return null } })()
const f = reactive(saved || { tab: 'profile', prof: '', bands: '', profSynth: false, name: '', unit: 'mm', lsl: null, usl: null, chart: '', data: '', spcSynth: false })
function keep() { try { localStorage.setItem(KEY, JSON.stringify(f)) } catch { /* private mode */ } }
const prof = ref(null), spc = ref(null), err = ref(null), busy = ref(false)

const rows = (txt) => txt.split('\n').map((l) => l.trim()).filter(Boolean).map((l) => l.split(/[\s,;\t]+/).map(Number))
async function synthProfile() {
  const d = await api('/quality/synthetic/profile')
  f.prof = d.r.join('\n'); f.profSynth = true; keep()
}
async function synthSpc() {
  const d = await api('/quality/synthetic/spc')
  f.data = d.data.map((r) => r.join(', ')).join('\n'); f.spcSynth = true; f.name = f.name || t('qSynthName'); keep()
}
async function runProfile() {
  busy.value = true; keep()
  try {
    const rs = rows(f.prof)
    const body = rs.every((r) => r.length >= 2) ? { points: rs.map((r) => [r[0], r[1]]) } : { r: rs.map((r) => r[0]) }
    body.bands = rows(f.bands).map((r, k) => [r[0], r[1], f.bands.split('\n').filter((l) => l.trim())[k].split(/[\s,;\t]+/)[2] || `${r[0]}–${r[1]}`])
    prof.value = await api('/quality/profile', body); err.value = null
  } catch (e) { err.value = e; prof.value = null } finally { busy.value = false }
}
async function runSpc() {
  busy.value = true; keep()
  try {
    spc.value = await api('/quality/spc', { data: rows(f.data), chart: f.chart || undefined, lsl: f.lsl, usl: f.usl, name: f.name, unit: f.unit })
    err.value = null
  } catch (e) { err.value = e; spc.value = null } finally { busy.value = false }
}
// polar picture of the deviations about the least-squares circle (exaggerated) and the amplitude spectrum
const P = 300, C = P / 2
const polar = computed(() => {
  const p = prof.value
  if (!p) return null
  const r = p.resid, m = Math.max(...r.map(Math.abs), 1e-9), R0 = 90, k = 40 / m
  const pts = r.map((v, i) => { const a = (2 * Math.PI * i) / r.length; return `${C + (R0 + v * k) * Math.cos(a)},${C - (R0 + v * k) * Math.sin(a)}` })
  return { path: 'M' + pts.join(' L') + ' Z', R0, scale: k }
})
const spec = computed(() => {
  const p = prof.value
  if (!p) return null
  const top = Math.min(p.amp.length - 1, 100), W = 600, H = 170, PL = 40, PB = 22
  const a = p.amp.slice(2, top + 1), m = Math.max(...a, 1e-9)
  const bw = (W - PL - 10) / (top - 1)
  return { W, H, PB, bars: a.map((v, i) => ({ x: PL + i * bw, w: Math.max(bw - 1, 1), y: 8 + (1 - v / m) * (H - 8 - PB), h: (v / m) * (H - 8 - PB), o: i + 2 })),
    ticks: [2, 25, 50, 75, 100].filter((o) => o <= top).map((o) => ({ x: PL + (o - 2) * bw, o })), m }
})
const flagged = computed(() => [...new Set((spc.value?.rules || []).flatMap((h) => h.points))])
const fx = (x, d = 3) => (x == null ? '—' : Number(x).toFixed(d))
</script>

<template>
  <div class="asm">
    <aside class="edit"><div class="pane">
      <div class="seg two" role="tablist">
        <button type="button" role="tab" :aria-selected="f.tab === 'profile'" :class="{ on: f.tab === 'profile' }" @click="f.tab = 'profile'; keep()">{{ t('qProfileTab') }}</button>
        <button type="button" role="tab" :aria-selected="f.tab === 'spc'" :class="{ on: f.tab === 'spc' }" @click="f.tab = 'spc'; keep()">{{ t('qSpcTab') }}</button>
      </div>
      <template v-if="f.tab === 'profile'">
        <p class="hint">{{ t('qProfileIntro') }}</p>
        <label class="area"><span class="lab">{{ t('qProfile') }}<small>{{ t('qProfileHint') }}</small></span><textarea v-model="f.prof" rows="9" spellcheck="false" @input="f.profSynth = false"></textarea></label>
        <label class="area"><span class="lab">{{ t('qBands') }}<small>{{ t('qBandsHint') }}</small></span><textarea v-model="f.bands" rows="3" spellcheck="false"></textarea></label>
        <div class="btns"><button type="button" class="accent" :disabled="busy" @click="runProfile">{{ t('qAnalyse') }}</button><button type="button" class="ghost" @click="synthProfile">{{ t('asmSynth') }}</button></div>
        <p v-if="f.profSynth" class="fict">{{ t('qSynthNote') }}</p>
      </template>
      <template v-else>
        <p class="hint">{{ t('qSpcIntro') }}</p>
        <label class="num"><span class="lab">{{ t('qName') }}</span><span class="box"><input v-model="f.name" @change="keep"><i></i></span></label>
        <label class="num"><span class="lab">{{ t('qUnit') }}</span><span class="box"><input v-model="f.unit" @change="keep"><i></i></span></label>
        <label class="num"><span class="lab">{{ t('qLsl') }}</span><span class="box"><input v-model.number="f.lsl" type="number" step="any" @change="keep"><i>{{ f.unit }}</i></span></label>
        <label class="num"><span class="lab">{{ t('qUsl') }}</span><span class="box"><input v-model.number="f.usl" type="number" step="any" @change="keep"><i>{{ f.unit }}</i></span></label>
        <label class="num"><span class="lab">{{ t('qChart') }}</span><select v-model="f.chart" @change="keep"><option value="">{{ t('qAuto') }}</option><option value="xbar_r">{{ t('qXR') }}</option><option value="xbar_s">{{ t('qXS') }}</option><option value="i_mr">{{ t('qIMR') }}</option></select></label>
        <label class="area"><span class="lab">{{ t('qData') }}<small>{{ t('qDataHint') }}</small></span><textarea v-model="f.data" rows="9" spellcheck="false" @input="f.spcSynth = false"></textarea></label>
        <div class="btns"><button type="button" class="accent" :disabled="busy" @click="runSpc">{{ t('qPlot') }}</button><button type="button" class="ghost" @click="synthSpc">{{ t('asmSynth') }}</button></div>
        <p v-if="f.spcSynth" class="fict">{{ t('qSynthNote') }}</p>
      </template>
    </div></aside>

    <section class="stage">
      <p v-if="err" class="err" role="alert">{{ t('error') }}：{{ lang === 'zh' ? err.zh || err.message : err.message }}</p>
      <template v-if="f.tab === 'profile'">
        <p v-if="!prof" class="hint">{{ t('qProfileEmpty') }}</p>
        <template v-else>
          <p v-if="f.profSynth" class="fict">{{ t('qSynthNote') }}</p>
          <div class="cmp">
            <div class="big"><b class="mono">{{ fx(prof.roundness) }}</b><span>{{ t('qRoundness') }}</span><small>{{ t('qLsc') }}</small></div>
            <div class="big alt"><b class="mono">{{ fx(prof.eccentricity) }}</b><span>{{ t('qEcc') }}</span><small>{{ t('qEccNote') }}</small></div>
            <div class="facts"><span>{{ prof.n }} {{ t('qPoints') }}</span></div>
          </div>
          <div class="figs">
            <figure><figcaption>{{ t('qPolar') }}</figcaption>
              <svg v-if="polar" :viewBox="`0 0 ${P} ${P}`" role="img" :aria-label="t('qPolar')">
                <circle :cx="C" :cy="C" :r="polar.R0" class="centre" fill="none" /><path :d="polar.path" class="ringline" />
              </svg></figure>
            <section v-if="prof.bands.length"><h3>{{ t('qBandRes') }}</h3>
              <table class="casetbl"><thead><tr><th>{{ t('qBand') }}</th><th>{{ t('qOrders') }}</th><th>RMS</th><th>{{ t('qPeak') }}</th></tr></thead>
                <tbody><tr v-for="b in prof.bands" :key="b.name"><td>{{ b.name }}</td><td class="mono">{{ b.from }}–{{ b.to }}</td><td class="mono">{{ fx(b.rms, 4) }}</td><td class="mono">{{ b.peak_order }}</td></tr></tbody></table>
            </section>
          </div>
          <figure v-if="spec" class="curve"><figcaption>{{ t('qSpectrum') }}</figcaption>
            <svg :viewBox="`0 0 ${spec.W} ${spec.H}`" role="img" :aria-label="t('qSpectrum')">
              <rect v-for="b in spec.bars" :key="b.o" :x="b.x" :y="b.y" :width="b.w" :height="b.h" class="bar-a"><title>{{ b.o }}: {{ b.h }}</title></rect>
              <text v-for="tk in spec.ticks" :key="tk.o" :x="tk.x" :y="spec.H - 6" class="ann mid">{{ tk.o }}</text>
            </svg></figure>
        </template>
      </template>
      <template v-else>
        <p v-if="!spc" class="hint">{{ t('qSpcEmpty') }}</p>
        <template v-else>
          <p v-if="f.spcSynth" class="fict">{{ t('qSynthNote') }}</p>
          <div class="cmp">
            <div class="big"><b class="mono">{{ spc.capability.Cpk != null ? fx(spc.capability.Cpk, 2) : '—' }}</b><span>Cpk</span><small>Cp {{ spc.capability.Cp != null ? fx(spc.capability.Cp, 2) : '—' }}</small></div>
            <div class="big alt"><b class="mono">{{ spc.capability.Ppk != null ? fx(spc.capability.Ppk, 2) : '—' }}</b><span>Ppk</span><small>Pp {{ spc.capability.Pp != null ? fx(spc.capability.Pp, 2) : '—' }}</small></div>
            <div class="facts"><span>{{ t('q_' + spc.chart) }}，{{ spc.k }} × {{ spc.n }}</span><span>{{ t('qOutSpec') }} {{ spc.out_of_spec }}</span>
              <span v-if="spc.capability.Cp == null">{{ t('qNoSpec') }}</span></div>
          </div>
          <LineChart :c="spc.main" :flags="flagged" :title="spc.main.name + (spc.name ? '：' + spc.name : '') + (spc.unit ? '（' + spc.unit + '）' : '')" />
          <LineChart :c="spc.spread" :flags="spc.spread_out" :title="spc.spread.name" />
          <section><h3>{{ t('qRules') }}</h3>
            <p v-if="!spc.rules.length && !spc.spread_out.length" class="hint">{{ t('qNoRule') }}</p>
            <ul class="left">
              <li v-for="h in spc.rules" :key="h.rule"><b>{{ t('qRule') }} {{ h.rule }}</b>：{{ t('nelson' + h.rule) }} — {{ t('qAtPoints') }} {{ h.points.map((i) => i + 1).join('、') }}</li>
              <li v-if="spc.spread_out.length">{{ spc.spread.name }}：{{ t('qSpreadOut') }} {{ spc.spread_out.map((i) => i + 1).join('、') }}</li>
            </ul>
            <p class="hint">{{ t('qRulesSrc') }}</p>
          </section>
        </template>
      </template>
    </section>
  </div>
</template>
