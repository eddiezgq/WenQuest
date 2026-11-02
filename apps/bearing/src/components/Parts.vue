<script setup>
// 零件图与三维 (round 64, step 5): each part's half section from the design, STEP and DXF downloads.
import { onMounted, ref } from 'vue'
import { api, saveText } from '../api'
import { project } from '../store'
import { t, lang } from '../i18n'

defineEmits(['close'])
const dr = ref(null), err = ref(null), busy = ref('')
const body = () => JSON.parse(JSON.stringify(project))
onMounted(async () => { try { dr.value = await api('/parts/drawings', body()) } catch (e) { err.value = e } })
async function get(path, mime) {
  busy.value = path
  try { const r = await api(path, body()); saveText(r.name, r.text, mime) } catch (e) { err.value = e } finally { busy.value = '' }
}
const W = 300, H = 210, PAD = 26
function fig(part) {
  const pts = part.outline
  const zs = pts.map((p) => p[0]), rs = pts.map((p) => p[1])
  const z0 = Math.min(...zs), z1 = Math.max(...zs), r0 = Math.min(...rs), r1 = Math.max(...rs)
  const s = Math.min((W - 2 * PAD) / (z1 - z0 || 1), (H - 2 * PAD) / (r1 - r0 || 1))
  const X = (z) => W / 2 + (z - (z0 + z1) / 2) * s, Y = (r) => H / 2 - (r - (r0 + r1) / 2) * s
  return { d: 'M' + pts.map((p) => `${X(p[0])},${Y(p[1])}`).join(' L') + ' Z', yTop: Y(r1), yBot: Y(r0), xL: X(z0), xR: X(z1) }
}
const f3 = (x) => Number(x).toFixed(3)
const print = () => window.print()
</script>

<template>
  <div class="report-wrap" role="dialog" aria-modal="true" :aria-label="t('partsTitle')">
    <div class="report-bar no-print">
      <button type="button" class="accent" @click="print">{{ t('print') }}</button>
      <button type="button" class="ghost" @click="$emit('close')">{{ t('close') }}</button>
    </div>
    <article class="report parts">
      <h1>{{ t('partsTitle') }}</h1>
      <p v-if="err" class="err" role="alert">{{ t('error') }}：{{ lang === 'zh' ? err.zh || err.message : err.message }}</p>
      <template v-if="dr">
        <div class="no-print dl">
          <span>{{ t('partsStep') }}</span>
          <button v-for="w in ['bearing', 'inner', 'outer', 'element']" :key="w" type="button" class="ghost" :disabled="busy !== ''" @click="get(`/parts/${w}.step`, 'model/step')">{{ t('part_' + w) }}</button>
        </div>
        <div class="no-print dl">
          <span>{{ t('partsDxf') }}</span>
          <button v-for="w in ['inner', 'outer', 'element']" :key="w" type="button" class="ghost" :disabled="busy !== ''" @click="get(`/parts/${w}.dxf`, 'application/dxf')">{{ t('part_' + w) }}</button>
        </div>
        <div class="partgrid">
          <section v-for="k in ['inner', 'outer', 'element']" :key="k">
            <h2>{{ lang === 'zh' ? dr[k].zh : dr[k].en }}</h2>
            <svg :viewBox="`0 0 ${W} ${H}`" role="img" :aria-label="lang === 'zh' ? dr[k].zh : dr[k].en">
              <defs><pattern :id="'ph' + k" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="hatch" /></pattern></defs>
              <path :d="fig(dr[k]).d" class="ring" /><path :d="fig(dr[k]).d" :fill="`url(#ph${k})`" />
            </svg>
            <dl class="rows">
              <template v-if="k !== 'element'">
                <dt>⌀ {{ t('partsIn') }}</dt><dd class="mono">{{ f3(dr[k].r_min * 2) }} mm</dd>
                <dt>⌀ {{ t('partsOut') }}</dt><dd class="mono">{{ f3(dr[k].r_max * 2) }} mm</dd>
                <dt>{{ t('B') }}</dt><dd class="mono">{{ f3(dr[k].width) }} mm</dd>
              </template>
              <template v-else>
                <dt>⌀</dt><dd class="mono">{{ f3(dr[k].r_max * 2) }} mm</dd>
                <dt v-if="dr.kind !== 'ball'">{{ t('Lw') }}</dt><dd v-if="dr.kind !== 'ball'" class="mono">{{ f3(dr[k].width) }} mm</dd>
              </template>
              <template v-for="(a, j) in dr[k].arcs" :key="j"><dt>R{{ j + 1 }}</dt><dd class="mono">{{ f3(a.r) }} mm</dd></template>
              <dt>{{ t('partsVol') }}</dt><dd class="mono">{{ (dr[k].volume / 1000).toFixed(3) }} cm³</dd>
              <dt>{{ t('partsTol') }}</dt><dd>{{ t('unknown') }}</dd>
            </dl>
          </section>
        </div>
        <p v-for="(n, j) in dr.notes" :key="j" class="hint">{{ lang === 'zh' ? n.zh : n.en }}</p>
      </template>
    </article>
  </div>
</template>
