<script setup>
// The end play sweep of a tapered roller bearing pair (round 64, plan section 十六): how the largest contact stress,
// the rollers carrying load and the axial stiffness change with the end play set at mounting. The software does not
// pick a "best" value: the criteria are the company's.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const W = 620, PH = 92, PL = 56, PR = 16, GAP = 18
const panels = computed(() => {
  const c = props.r?.setting_curve
  if (!c) return null
  const xs = c.e_um, x0 = Math.min(...xs), x1 = Math.max(...xs)
  const X = (x) => PL + ((x - x0) / (x1 - x0)) * (W - PL - PR)
  const now = props.r.pair?.endplay_um
  const xr = ['crossed', 'thin'].includes(props.r.type)  // robot joint bearings: the tilting stiffness is the one that matters
  const nk = props.r.type === 'thin' ? 'scNb' : xr ? 'scNx' : 'scN'
  return [['p_max', 'scP', 'MPa', 0], xr ? ['k_tilt', 'scKt', 'N·m/mrad', 0] : ['k_axial', 'scK', 'N/µm', 0], ['loaded', nk, '', 0]].map(([k, key, unit], i) => {
    const ys = c[k].map((y) => (y == null ? null : Number(y)))
    const ok = ys.filter((y) => y != null)
    const lo = Math.min(...ok), hi = Math.max(...ok), pad = (hi - lo) * 0.1 || Math.abs(hi) * 0.05 || 1
    const top = 8 + i * (PH + GAP)
    const Y = (y) => top + (1 - (y - lo + pad) / (hi - lo + 2 * pad)) * PH
    const pts = xs.map((x, j) => (ys[j] == null ? null : [X(x), Y(ys[j])])).filter(Boolean)
    const f = (y) => (Math.abs(y) >= 100 ? y.toFixed(0) : y.toFixed(1))
    return { key, unit, top, path: pts.map((p) => p.join(',')).join(' '), pts, hi: f(hi), lo: f(lo), now: now != null && now >= x0 && now <= x1 ? X(now) : null }
  }).concat([{ axis: true, x0, x1, X }])
})
const H = 8 + 3 * (PH + GAP) + 10
</script>

<template>
  <section v-if="panels" class="setting">
    <h3>{{ t(['crossed', 'thin'].includes(r.type) ? 'scTitleX' : 'scTitle') }} <small>{{ t('scHint') }}</small></h3>
    <figure class="curve">
      <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t(['crossed', 'thin'].includes(r.type) ? 'scTitleX' : 'scTitle')">
        <g v-for="p in panels.slice(0, 3)" :key="p.key">
          <rect :x="PL" :y="p.top" :width="W - PL - PR" :height="PH" class="frame" />
          <text :x="PL - 6" :y="p.top + 10" class="ann end">{{ p.hi }}</text>
          <text :x="PL - 6" :y="p.top + PH" class="ann end">{{ p.lo }}</text>
          <text :x="PL + 6" :y="p.top + 14" class="ann">{{ t(p.key) }}{{ p.unit ? '（' + p.unit + '）' : '' }}</text>
          <line v-if="p.now != null" :x1="p.now" :x2="p.now" :y1="p.top" :y2="p.top + PH" class="contact" />
          <polyline :points="p.path" class="line" />
          <circle v-for="(q, j) in p.pts" :key="j" :cx="q[0]" :cy="q[1]" r="2.2" class="pt" />
        </g>
        <text :x="PL" :y="H - 2" class="ann">{{ panels[3].x0 }} µm</text>
        <text :x="W - PR" :y="H - 2" class="ann end">{{ panels[3].x1 }} µm</text>
        <text :x="(PL + W - PR) / 2" :y="H - 2" class="ann mid">{{ t(r.type === 'crossed' || (r.type === 'thin' && r.thin?.section !== 'A') ? 'scXr' : 'scX') }}</text>
      </svg>
    </figure>
  </section>
</template>

<style scoped>
.setting { margin-top: 12px; border-top: 1px solid var(--line); padding-top: 10px; }
.setting h3 { font: 700 13px/1.3 var(--serif-zh); margin: 0 0 6px; }
.setting h3 small { font: 400 12px var(--body); color: var(--muted); margin-left: 6px; }
.frame { fill: none; stroke: var(--line); }
.pt { fill: var(--accent-ink); }
.ann.end { text-anchor: end; } .ann.mid { text-anchor: middle; }
</style>
