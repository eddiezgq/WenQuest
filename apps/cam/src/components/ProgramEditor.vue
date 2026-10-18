<script setup>
// The motion program: rises, dwells and returns adding up to 360°, or a table of points (round 39).
import { computed, ref, watch } from 'vue'
import { project, laws } from '../store'
import { t, lang } from '../i18n'

const prog = computed(() => project.program)
const rad = computed(() => prog.value.unit === 'rad')
const liftKey = computed(() => (rad.value ? 'h_deg' : 'h'))
const total = computed(() => (prog.value.segments || []).reduce((a, s) => a + (Number(s.deg) || 0), 0))
const useTable = ref(!!prog.value.table)
const tableText = ref('')

function tableToText() {
  const tb = prog.value.table
  if (!tb) return ''
  const s = rad.value ? tb.s_deg : tb.s
  return tb.deg.map((d, i) => `${d}, ${s?.[i] ?? ''}`).join('\n')
}
watch(useTable, (on) => {
  if (on) {
    tableText.value = tableToText() || '0, 0\n45, 2\n90, 8\n135, 14\n180, 16\n225, 14\n270, 8\n315, 2'
    applyTable()
  } else {
    delete project.program.table
    if (!project.program.segments?.length) project.program.segments = [{ kind: 'rise', deg: 180, [liftKey.value]: 10, law: 'cycloidal' }, { kind: 'return', deg: 180, [liftKey.value]: 10, law: 'cycloidal' }]
  }
})
function applyTable() {
  const pts = tableText.value.split(/\n/).map((l) => l.split(/[,\s\t]+/).filter(Boolean).map(Number)).filter((p) => p.length >= 2 && p.every(Number.isFinite))
  project.program.table = { deg: pts.map((p) => p[0]), [rad.value ? 's_deg' : 's']: pts.map((p) => p[1]) }
}

function add() { project.program.segments.push({ kind: 'dwell', deg: 30 }) }
function remove(i) { project.program.segments.splice(i, 1) }
function move(i, d) {
  const a = project.program.segments, j = i + d
  if (j < 0 || j >= a.length) return
  ;[a[i], a[j]] = [a[j], a[i]]
}
function kind(seg, k) {
  seg.kind = k
  if (k === 'dwell') { delete seg.h; delete seg.h_deg; delete seg.law } else { seg.law ||= 'cycloidal'; seg[liftKey.value] ||= 10 }
}
const lawName = (l) => (lang.value === 'zh' ? l.zh : l.en)
</script>

<template>
  <div class="prog">
    <label class="check"><input v-model="useTable" type="checkbox"> {{ t('useTable') }}</label>
    <template v-if="!useTable">
      <table class="segs">
        <thead><tr><th>{{ t('kind') }}</th><th>{{ t('angle') }}</th><th>{{ t('lift') }} ({{ rad ? '°' : 'mm' }})</th><th>{{ t('law') }}</th><th /></tr></thead>
        <tbody>
          <tr v-for="(s, i) in prog.segments" :key="i">
            <td><select :value="s.kind" @change="kind(s, $event.target.value)">
              <option value="rise">{{ t('rise') }}</option><option value="dwell">{{ t('dwell') }}</option><option value="return">{{ t('ret') }}</option></select></td>
            <td><input v-model.number="s.deg" type="number" min="0.1" step="any" class="num"></td>
            <td><input v-if="s.kind !== 'dwell'" v-model.number="s[liftKey]" type="number" min="0" step="any" class="num"></td>
            <td><select v-if="s.kind !== 'dwell'" v-model="s.law"><option v-for="l in laws" :key="l.key" :value="l.key">{{ lawName(l) }}</option></select></td>
            <td class="acts"><button type="button" title="↑" @click="move(i, -1)">↑</button><button type="button" title="↓" @click="move(i, 1)">↓</button><button type="button" title="×" @click="remove(i)">×</button></td>
          </tr>
        </tbody>
      </table>
      <div class="foot"><button type="button" class="ghost" @click="add">+ {{ t('addSeg') }}</button>
        <span :class="['tot', Math.abs(total - 360) > 1e-6 && 'bad']">{{ t('total') }} {{ +total.toFixed(4) }}° / 360°</span></div>
    </template>
    <template v-else>
      <p class="hint">{{ t('tableHint') }}</p>
      <textarea v-model="tableText" rows="12" class="mono" @change="applyTable" />
    </template>
  </div>
</template>

<style scoped>
.segs { width: 100%; border-collapse: collapse; font-size: 13px; }
.segs th { text-align: left; font-weight: 500; color: var(--muted); padding: 4px 3px; font-size: 12px; }
.segs td { padding: 3px; }
.segs select, .segs input { width: 100%; }
.segs .num { width: 64px; }
.acts { white-space: nowrap; }
.acts button { border: 0; background: none; color: var(--muted); cursor: pointer; padding: 2px 4px; font-size: 14px; }
.acts button:hover { color: var(--ink); }
.foot { display: flex; justify-content: space-between; align-items: center; margin-top: 8px; }
.tot { font: 500 13px/1 var(--mono); color: var(--ok); }
.tot.bad { color: var(--bad); }
.check { display: flex; gap: 6px; align-items: center; font-size: 13px; margin-bottom: 10px; color: var(--muted); }
.hint { font-size: 12.5px; color: var(--muted); margin: 0 0 6px; }
textarea { width: 100%; }
</style>
