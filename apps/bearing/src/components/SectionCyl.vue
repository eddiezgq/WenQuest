<script setup>
// Half section of a cylindrical roller bearing: rings hatched, the roller, its crown drawn exaggerated so it can be seen.
import { computed } from 'vue'
import { t } from '../i18n'

const props = defineProps({ r: Object })
const W = 460, H = 400, PAD = 54, PADL = 78, PADR = 104

const v = computed(() => {
  const g = props.r?.geometry
  if (!g) return null
  const { d, D, B, dm, Dw, Lw, Lwe, di, do: dO } = g
  const s = Math.min((W - PADL - PADR) / B, (H - 2 * PAD) / ((D - d) / 2))
  const ox = PADL + (W - PADL - PADR) / 2, oy = H / 2 + ((D + d) / 4) * s
  const X = (x) => ox + x * s, Y = (r) => oy - r * s
  const rect = (x0, x1, r0, r1) => `M${X(x0)},${Y(r0)} L${X(x1)},${Y(r0)} L${X(x1)},${Y(r1)} L${X(x0)},${Y(r1)} Z`
  // the roller outline with its crown, drop scaled up so a few microns show (the scale is printed)
  const sl = props.r.slices
  let rollerPath, amp = 0
  const c0 = dm / 2
  if (sl && sl.drop.some((x) => x > 0)) {
    const maxDrop = Math.max(...sl.drop)
    amp = (0.12 * Dw) / maxDrop
    const top = sl.x.map((x, j) => `${X(x)},${Y(c0 + Dw / 2 - sl.drop[j] * amp)}`)
    const bot = sl.x.map((x, j) => `${X(x)},${Y(c0 - Dw / 2 + sl.drop[j] * amp)}`).reverse()
    rollerPath = `M${X(-Lw / 2)},${Y(c0 + Dw / 2 - maxDrop * amp)} L${top.join(' L')} L${X(Lw / 2)},${Y(c0 + Dw / 2 - maxDrop * amp)} L${X(Lw / 2)},${Y(c0 - Dw / 2 + maxDrop * amp)} L${bot.join(' L')} L${X(-Lw / 2)},${Y(c0 - Dw / 2 + maxDrop * amp)} Z`
  } else {
    rollerPath = rect(-Lw / 2, Lw / 2, c0 - Dw / 2, c0 + Dw / 2)
  }
  return {
    outer: rect(-B / 2, B / 2, dO / 2, D / 2), inner: rect(-B / 2, B / 2, d / 2, di / 2), roller: rollerPath, amp,
    pitch: Y(dm / 2), xL: X(-B / 2), xR: X(B / 2), yD: Y(D / 2), yd: Y(d / 2), g, rTop: Y(c0 + Dw / 2), rx: X(Lw / 2),
    lwe: [X(-Lwe / 2), X(Lwe / 2)], yLwe: Y(c0 - Dw / 2) + 16,
  }
})
const f = (x, k = 1) => (x == null ? '—' : Number(x).toFixed(k))
</script>

<template>
  <figure class="sect">
    <figcaption>{{ t('section') }}</figcaption>
    <svg v-if="v" :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="t('section')">
      <defs>
        <pattern id="hatchc" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
          <line x1="0" y1="0" x2="0" y2="7" class="hatch" />
        </pattern>
      </defs>
      <path :d="v.outer" class="ring" /><path :d="v.outer" fill="url(#hatchc)" />
      <path :d="v.inner" class="ring" /><path :d="v.inner" fill="url(#hatchc)" />
      <path :d="v.roller" class="ball" />
      <line :x1="v.xL - 18" :x2="v.xR + 18" :y1="v.pitch" :y2="v.pitch" class="centre" />
      <line :x1="v.lwe[0]" :x2="v.lwe[1]" :y1="v.yLwe" :y2="v.yLwe" class="dim" />
      <text :x="(v.lwe[0] + v.lwe[1]) / 2" :y="v.yLwe + 14" class="ann mid">Lwe {{ f(v.g.Lwe) }}</text>
      <line :x1="v.xL" :x2="v.xR" :y1="v.yD - 22" :y2="v.yD - 22" class="dim" />
      <text :x="(v.xL + v.xR) / 2" :y="v.yD - 28" class="ann mid">B {{ f(v.g.B) }}</text>
      <text :x="v.xL - 10" :y="v.yD + 4" class="ann end">⌀D {{ f(v.g.D) }}</text>
      <text :x="v.xL - 10" :y="v.yd + 4" class="ann end">⌀d {{ f(v.g.d) }}</text>
      <text :x="v.xR + 22" :y="v.pitch + 4" class="ann">⌀dm {{ f(v.g.dm) }}</text>
      <text :x="v.xR + 10" :y="v.rTop - 6" class="ann">⌀Dw {{ f(v.g.Dw, 2) }}</text>
    </svg>
    <p v-if="v && v.amp" class="cap-note">{{ t('dropLabel') }} × {{ Math.round(v.amp) }}</p>
  </figure>
</template>
