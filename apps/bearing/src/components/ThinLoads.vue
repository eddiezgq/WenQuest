<script setup>
// Thin-section bearing (plan section 二十一): the contact load of every ball round the bearing — a four-point
// bearing's two diagonals (or a pair's two rows) one outwards and one inwards — and the largest value at each contact.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const x = computed(() => props.r?.thin)
const S = 260, C = S / 2, R0 = 78, RM = 44
const sets = computed(() => {
  const c = x.value
  if (!c) return null
  // the two sets drawn: X the diagonals (inner arcs + and −), A a pair's rows, C one set
  const n = c.psi_deg.length
  if (c.section === 'X') return [{ key: 'thinDiagP', q: c.Q.map((r) => r[0]), idx: [...Array(n).keys()] }, { key: 'thinDiagM', q: c.Q.map((r) => r[1]), idx: [...Array(n).keys()] }]
  const rows = [...new Set(c.row)]
  if (rows.length === 2) return rows.map((rw, k) => ({ key: k === 0 ? 'thinRowA' : 'thinRowB', q: c.Q.filter((_, j) => c.row[j] === rw).map((r) => r[0]), idx: [...Array(n).keys()].filter((j) => c.row[j] === rw) }))
  return [{ key: 'thinBall', q: c.Q.map((r) => r[0]), idx: [...Array(n).keys()] }]
})
const bars = computed(() => {
  const ss = sets.value
  if (!ss) return null
  const qm = Math.max(...ss.flatMap((s) => s.q), 1e-9)
  return ss.flatMap((s, k) => s.q.map((q, j) => {
    const a = (x.value.psi_deg[s.idx[j]] * Math.PI) / 180, L = (q / qm) * RM, out = k === 0 ? 1 : -1
    return { x1: C + R0 * Math.cos(a), y1: C - R0 * Math.sin(a), x2: C + (R0 + out * L) * Math.cos(a), y2: C - (R0 + out * L) * Math.sin(a), plus: k === 0, on: q > 0 }
  }))
})
const table = computed(() => {
  const c = x.value
  if (!c) return []
  return c.slots.map((sl, k) => {
    let qm = 0, at = 0
    c.Q.forEach((r, j) => { if (r[k] > qm) { qm = r[k]; at = j } })
    const pm = Math.max(...c.p.map((r) => r[k]))
    const side = sl.side > 0 ? ' +' : sl.side < 0 ? ' −' : ''
    return { name: t(sl.ring === 'inner' ? 'innerRing' : 'outerRing') + side, q: qm, a: qm > 0 ? Math.abs(c.angle_deg[at][k]) : null, p: pm }
  })
})
const f = (v, k = 0) => (v == null ? '—' : Number(v).toFixed(k))
</script>

<template>
  <div v-if="bars" class="tl">
    <figure>
      <figcaption>{{ t('thinLoads') }}</figcaption>
      <svg :viewBox="`0 0 ${S} ${S}`" role="img" :aria-label="t('thinLoads')">
        <circle :cx="C" :cy="C" :r="R0" class="base" />
        <line v-for="(l, j) in bars" :key="j" :x1="l.x1" :y1="l.y1" :x2="l.x2" :y2="l.y2" :class="['bar', l.plus ? 'p' : 'm', { off: !l.on }]" />
      </svg>
      <p class="legend"><template v-for="(s, k) in sets" :key="k"><span :class="['sw', k === 0 ? 'p' : 'm']"></span>{{ t(s.key) }}{{ sets.length > 1 ? (k === 0 ? ' ↗' : ' ↙') : '' }} </template></p>
    </figure>
    <figure>
      <figcaption>{{ t('thinTable') }}</figcaption>
      <div class="tw">
        <table>
          <thead><tr><th>{{ t('thinWhere') }}</th><th>Q N</th><th>{{ t('thinAngle') }} °</th><th>p MPa</th></tr></thead>
          <tbody><tr v-for="(row, k) in table" :key="k"><td>{{ row.name }}</td><td>{{ f(row.q) }}</td><td>{{ f(row.a, 1) }}</td><td>{{ f(row.p) }}</td></tr></tbody>
        </table>
      </div>
    </figure>
  </div>
</template>

<style scoped>
.tl { display: grid; grid-template-columns: minmax(0, 260px) minmax(0, 1fr); gap: 16px; align-items: start; margin-top: 8px; }
figure { margin: 0; min-width: 0; }
figcaption { font: 600 13px var(--serif-zh); margin-bottom: 4px; }
svg { width: 100%; height: auto; display: block; }
.base { fill: none; stroke: var(--line); }
.bar { stroke-width: 3; stroke-linecap: round; }
.bar.p { stroke: #b0632a; } .bar.m { stroke: #2f6f8f; } .bar.off { opacity: .25; }
.legend { font-size: 12px; color: var(--muted); margin: 4px 0 0; display: flex; flex-wrap: wrap; gap: 4px 10px; align-items: center; }
.sw { display: inline-block; width: 14px; height: 3px; margin-right: 4px; vertical-align: middle; }
.sw.p { background: #b0632a; } .sw.m { background: #2f6f8f; }
.tw { overflow-x: auto; }
table { border-collapse: collapse; font-size: 12.5px; width: 100%; }
th, td { padding: 4px 8px; border-bottom: 1px solid var(--line); text-align: right; white-space: nowrap; }
th:first-child, td:first-child { text-align: left; }
th { font-weight: 600; color: var(--muted); }
@media (max-width: 760px) { .tl { grid-template-columns: minmax(0, 1fr); } }
</style>
