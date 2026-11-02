<script setup>
// 工艺路线与工序卡 (round 64, step 5): the ring operations, their sizes worked back from the finished sizes and the
// company's allowances, the stock checks, and one printable sheet per operation. No default numbers.
import { computed, onMounted, ref, watch } from 'vue'
import { api, saveText } from '../api'
import { t, lang } from '../i18n'
import { project, replace } from '../store'

const KEY = 'wqbearing-process'
const KINDS = ['turn', 'heat', 'grind', 'superfinish', 'cut', 'wash', 'assemble', 'inspect', 'other']
const CUTS = ['turn', 'grind', 'superfinish', 'cut']
const SIZE_F = ['Z', 'T', 'Zreq', 'Zmax', 'setup'], STOCK_F = ['Z', 'dz', 'Zreq'], HEAT_F = ['change', 'scatter', 'distortion']

const tpl = ref((() => { try { return JSON.parse(localStorage.getItem(KEY) || 'null') } catch { return null } })())
const feats = ref(null), out = ref(null), err = ref(null), busy = ref(false), ring = ref('inner'), open = ref(-1)
const sheets = ref(false), fileInput = ref(null), examples = ref([])

const design = () => JSON.parse(JSON.stringify(project))
const L = (o) => (o ? (lang.value === 'zh' ? o.zh : o.en) : '')
const fname = (fid) => L(feats.value?.[ring.value]?.find((f) => f.id === fid)) || fid
const fieldsOf = (o) => (o.kind === 'heat' ? HEAT_F : CUTS.includes(o.kind) ? ((o.mode || (o.kind === 'superfinish' ? 'stock' : 'size')) === 'stock' ? STOCK_F : SIZE_F) : [])

async function loadFeatures() {
  try { feats.value = (await api('/process/template', design())).features; if (!tpl.value) await blankChain(); else err.value = null } catch (e) { feats.value = null; err.value = e }
}
async function blankChain() {
  try { const d = await api('/process/template', design()); feats.value = d.features; tpl.value = d.template; open.value = -1; err.value = null } catch (e) { err.value = e }
}
async function example(id) {
  try {
    const ex = await api('/process/examples/' + id)
    if (ex.design) replace(await api('/examples/' + ex.design))
    tpl.value = ex; open.value = -1
    await loadFeatures()
  } catch (e) { err.value = e }
}
let timer = 0, seq = 0
function runSoon() {
  try { localStorage.setItem(KEY, JSON.stringify(tpl.value)) } catch { /* private mode */ }
  clearTimeout(timer)
  timer = setTimeout(async () => {
    if (!tpl.value) return
    const my = ++seq
    busy.value = true
    try { const r = await api('/process', { design: design(), process: tpl.value }); if (my === seq) { out.value = r; err.value = null } }
    catch (e) { if (my === seq) { err.value = e; out.value = null } } finally { if (my === seq) busy.value = false }
  }, 300)
}
watch(tpl, runSoon, { deep: true })
watch(() => [project.type, project.size, project.inner], () => { loadFeatures(); runSoon() }, { deep: true })
onMounted(async () => {
  try { examples.value = await api('/process/examples') } catch { /* fine without */ }
  if (tpl.value) { await loadFeatures(); runSoon() } else await blankChain()
})

const R = computed(() => tpl.value?.rings?.[ring.value])
const ops = computed(() => R.value?.ops || [])
function addOp() {
  const last = ops.value.at(-1)
  ops.value.push({ no: (last?.no || 0) + 10, kind: 'grind', mode: 'size', name: { zh: '', en: '' }, equipment: '', params: [], features: {} })
  open.value = ops.value.length - 1
}
function move(k, d) { const a = ops.value, j = k + d; if (j < 0 || j >= a.length) return; [a[k], a[j]] = [a[j], a[k]]; open.value = j }
function drop(k) { ops.value.splice(k, 1); open.value = -1 }
function toggleFeature(o, fid, on) {
  if (on) o.features[fid] = Object.fromEntries(fieldsOf(o).map((n) => [n, null]))
  else delete o.features[fid]
}
function setKind(o, kind) {
  o.kind = kind
  if (CUTS.includes(kind)) o.mode = kind === 'superfinish' ? 'stock' : 'size'; else delete o.mode
  for (const fid of Object.keys(o.features)) toggleFeature(o, fid, CUTS.includes(kind) || kind === 'heat')
}
function setMode(o, mode) { o.mode = mode; for (const fid of Object.keys(o.features)) toggleFeature(o, fid, true) }
const num = (v) => (v === '' || v == null || Number.isNaN(v) ? null : Number(v))

function saveFile() {
  const name = (lang.value === 'zh' ? project.title.zh : project.title.en) || t('untitled')
  saveText(name.replace(/[\\/:*?"<>|]+/g, '_') + '.wqprocess.json', JSON.stringify(tpl.value, null, 1), 'application/json')
}
async function openFile(e) {
  const f = e.target.files?.[0]
  if (!f) return
  try { const d = JSON.parse(await f.text()); if (!d.rings) throw new Error(); tpl.value = d; open.value = -1 } catch { err.value = { message: t('pcNotFile'), zh: t('pcNotFile') } }
  e.target.value = ''
}

// numbers on the page
const mm = (x, d = 4) => (x == null ? '—' : x.toFixed(d))
const dev = (x) => (x === 0 ? '0' : (x > 0 ? '+' : '−') + Math.abs(x).toFixed(3))
const sizeStr = (s) => (s ? `${s.size.toFixed(4)} ${dev(s.upper)}/${dev(s.lower)}` : t('unknown'))
const resRing = computed(() => out.value?.rings?.[ring.value])
const colFeats = computed(() => resRing.value?.features || [])
const routeRows = computed(() => {
  const r = resRing.value
  if (!r) return []
  const rows = [{ key: 'blank', no: '', name: t('pcBlank'), cells: colFeats.value.map((f) => { const b = r.table[f.id]?.blank; return b ? (b.T_known ? sizeStr(b) : `${b.size.toFixed(4)} ${t('pcTolUnknown')}`) : '' }) }]
  for (const c of r.cards) {
    rows.push({ key: c.op, no: c.no, name: L(c.name) || t('k_' + c.kind), kind: c.kind, bad: c.checks.some((x) => x.status === 'fail'),
      cells: colFeats.value.map((f) => {
        const l = c.lines.find((x) => x.feature === f.id)
        if (!l) return ''
        if (c.kind === 'heat') return l.change == null ? t('unknown') : `Δ ${dev(l.change)}` + (l.after ? ` → ${sizeStr(l.after)}` : '')
        return sizeStr(l.size)
      }) })
  }
  return rows
})
const counts = computed(() => {
  const c = { pass: 0, fail: 0, unknown: 0 }
  for (const x of resRing.value?.checks || []) if (x.status in c) c[x.status]++
  return c
})
const print = () => window.print()
const allCards = computed(() => ['inner', 'outer'].filter((k) => out.value?.rings?.[k]).flatMap((k) => out.value.rings[k].cards.map((c) => ({ ...c, ring: k }))))
const ringFeat = (rk, fid) => L(out.value?.rings?.[rk]?.features.find((f) => f.id === fid)) || fid
const fmtZ = (x) => (x == null ? '—' : x.toFixed(4))
</script>

<template>
  <div class="asm proc">
    <aside class="edit"><div class="pane">
      <h2>{{ t('pcTitle') }}</h2>
      <p class="hint">{{ t('pcIntro') }}</p>
      <div class="btns">
        <button type="button" class="ghost" @click="blankChain">{{ t('pcBlankChain') }}</button>
        <button v-for="e in examples" :key="e.id" type="button" class="ghost" @click="example(e.id)">{{ t('pcExample') }}</button>
      </div>
      <div class="btns">
        <button type="button" class="ghost" @click="fileInput.click()">{{ t('pcOpen') }}</button>
        <input ref="fileInput" type="file" accept=".json" hidden @change="openFile">
        <button type="button" class="ghost" :disabled="!tpl" @click="saveFile">{{ t('pcSave') }}</button>
      </div>
      <div class="seg two" role="tablist">
        <button v-for="k in ['inner', 'outer']" :key="k" type="button" :class="{ on: ring === k }" :aria-pressed="ring === k" @click="ring = k; open = -1">{{ t('pc_' + k) }}</button>
      </div>

      <template v-if="R">
        <ol class="ops">
          <li v-for="(o, k) in ops" :key="k" :class="{ open: open === k }">
            <div class="ophead">
              <input v-model.number="o.no" class="opno mono" type="number" step="1" :aria-label="t('pcNo')">
              <button type="button" class="opname" :aria-expanded="open === k" @click="open = open === k ? -1 : k">
                {{ L(o.name) || t('k_' + o.kind) }}<small>{{ Object.keys(o.features).map(fname).join(lang === 'zh' ? '、' : ', ') }}</small>
              </button>
              <span class="opbtn"><button type="button" :aria-label="t('pcUp')" @click="move(k, -1)">↑</button><button type="button" :aria-label="t('pcDown')" @click="move(k, 1)">↓</button><button type="button" :aria-label="t('pcDel')" @click="drop(k)">×</button></span>
            </div>
            <div v-if="open === k" class="opbody">
              <label class="num"><span class="lab">{{ t('pcName') }}</span><span class="box"><input v-model="o.name[lang]" type="text"><i></i></span></label>
              <label class="num"><span class="lab">{{ t('pcKind') }}</span><span class="box"><select :value="o.kind" @change="setKind(o, $event.target.value)"><option v-for="x in KINDS" :key="x" :value="x">{{ t('k_' + x) }}</option></select><i></i></span></label>
              <label v-if="CUTS.includes(o.kind)" class="num"><span class="lab">{{ t('pcMode') }}<small>{{ t('pcModeHint') }}</small></span><span class="box"><select :value="o.mode || 'size'" @change="setMode(o, $event.target.value)"><option value="size">{{ t('pcModeSize') }}</option><option value="stock">{{ t('pcModeStock') }}</option></select><i></i></span></label>
              <label class="num"><span class="lab">{{ t('pcEquip') }}</span><span class="box"><input v-model="o.equipment" type="text"><i></i></span></label>
              <template v-if="CUTS.includes(o.kind) || o.kind === 'heat'">
                <p class="sub">{{ t('pcFeatures') }}</p>
                <div class="fchecks"><label v-for="f in feats?.[ring] || []" :key="f.id"><input type="checkbox" :checked="f.id in o.features" @change="toggleFeature(o, f.id, $event.target.checked)"> {{ L(f) }}</label></div>
                <div v-for="(d, fid) in o.features" :key="fid" class="fbox">
                  <b>{{ fname(fid) }}</b>
                  <label v-for="n in fieldsOf(o)" :key="n" class="num"><span class="lab">{{ t('pf_' + n) }}</span><span class="box"><input :value="d[n]" type="number" step="any" @change="d[n] = num($event.target.value)"><i>mm</i></span></label>
                </div>
              </template>
              <p class="sub">{{ t('pcParams') }}<small>{{ t('pcParamsHint') }}</small></p>
              <div class="cases"><table><tbody>
                <tr v-for="(p, j) in o.params" :key="j"><td><input v-model="p.k" :placeholder="t('pcPk')"></td><td><input v-model="p.v" :placeholder="t('pcPv')"></td><td><input v-model="p.u" :placeholder="t('pcPu')"></td><td><button type="button" class="x" :aria-label="t('pcDel')" @click="o.params.splice(j, 1)">×</button></td></tr>
              </tbody></table><button type="button" class="ghost" @click="o.params.push({ k: '', v: '', u: '' })">{{ t('pcAddParam') }}</button></div>
            </div>
          </li>
        </ol>
        <button type="button" class="ghost" @click="addOp">{{ t('pcAddOp') }}</button>

        <p class="sub">{{ t('pcFinish') }}<small>{{ t('pcFinishHint') }}</small></p>
        <div class="cases fin"><table><thead><tr><th></th><th>{{ t('pcEs') }}</th><th>{{ t('pcEi') }}</th></tr></thead><tbody>
          <tr v-for="f in feats?.[ring] || []" :key="f.id"><td>{{ L(f) }} <small class="mono">{{ f.size.toFixed(3) }}</small></td>
            <td><input :value="R.finish?.[f.id]?.es" type="number" step="any" @change="(R.finish ||= {})[f.id] = { ...(R.finish[f.id] || {}), es: num($event.target.value) }"></td>
            <td><input :value="R.finish?.[f.id]?.ei" type="number" step="any" @change="(R.finish ||= {})[f.id] = { ...(R.finish[f.id] || {}), ei: num($event.target.value) }"></td></tr>
        </tbody></table></div>
        <p class="sub">{{ t('pcBlankT') }}<small>{{ t('pcBlankTHint') }}</small></p>
        <div class="cases fin"><table><tbody>
          <tr v-for="f in feats?.[ring] || []" :key="f.id"><td>{{ L(f) }}</td>
            <td><input :value="R.blank?.[f.id]?.T" type="number" step="any" @change="(R.blank ||= {})[f.id] = { T: num($event.target.value) }"></td></tr>
        </tbody></table></div>
      </template>
    </div></aside>

    <section class="stage">
      <p v-if="err" class="err" role="alert">{{ t('error') }}：{{ lang === 'zh' ? err.zh || err.message : err.message }}</p>
      <p v-if="tpl?.fictional" class="fict">{{ L(tpl.note) }}</p>
      <template v-if="resRing">
        <div class="phead">
          <p class="verdict" :class="resRing.status">{{ t('pc_' + ring) }}：{{ t(resRing.status === 'pass' ? 'pcAllPass' : resRing.status === 'fail' ? 'pcSomeFail' : 'pcSomeUnknown') }}
            <small>{{ t('pass') }} {{ counts.pass }} · {{ t('fail') }} {{ counts.fail }} · {{ t('unknown') }} {{ counts.unknown }}</small></p>
          <button type="button" class="accent" @click="sheets = true">{{ t('pcSheets') }}</button>
        </div>
        <h3>{{ t('pcRoute') }} <small>{{ t('pcRouteHint') }}</small></h3>
        <div class="tblwrap"><table class="casetbl route">
          <thead><tr><th>{{ t('pcNo') }}</th><th>{{ t('pcName') }}</th><th v-for="f in colFeats" :key="f.id">{{ L(f) }}<small class="mono">{{ f.size.toFixed(3) }}</small></th></tr></thead>
          <tbody><tr v-for="r in routeRows" :key="r.key" :class="{ heat: r.kind === 'heat', bad: r.bad }"><td class="mono">{{ r.no }}</td><td>{{ r.name }}</td><td v-for="(c, j) in r.cells" :key="j" class="mono">{{ c }}</td></tr></tbody>
        </table></div>
        <section class="checks">
          <h3>{{ t('pcChecks') }} <small>{{ t('pcChecksHint') }}</small></h3>
          <ul>
            <li v-for="(c, j) in resRing.checks" :key="j" :class="c.status">
              <span class="chip">{{ t(c.status) }}</span>
              <span class="what">{{ lang === 'zh' ? c.zh : c.en }}<small v-if="c.note">{{ lang === 'zh' ? c.note_zh : c.note }}</small></span>
              <span class="val mono">{{ c.value == null ? '—' : c.value.toFixed(4) + ' mm' }}<small v-if="c.limit != null && c.status !== 'info'">{{ t(c.id === 'stock_max' || c.id === 'finish_tol' ? 'pcAtMost' : 'pcAtLeast') }} {{ c.limit.toFixed(4) }}</small></span>
            </li>
          </ul>
        </section>
        <ul class="pnotes"><li v-for="(n, j) in out.notes" :key="j">{{ L(n) }}</li></ul>
      </template>
      <p v-else-if="!err" class="hint">{{ busy ? t('busy') : t('pcEmpty') }}</p>
    </section>

    <div v-if="sheets && out" class="report-wrap" role="dialog" aria-modal="true" :aria-label="t('pcSheets')">
      <div class="report-bar no-print">
        <button type="button" class="accent" @click="print">{{ t('print') }}</button>
        <button type="button" class="ghost" @click="sheets = false">{{ t('close') }}</button>
      </div>
      <article class="report sheets">
        <section v-for="c in allCards" :key="c.ring + c.op" class="sheet">
          <header>
            <h1>{{ t('pcSheet') }}</h1>
            <p class="sub">{{ (lang === 'zh' ? project.title.zh : project.title.en) || t('untitled') }} · {{ t('pc_' + c.ring) }} · {{ t('pcNo') }} {{ c.no }} {{ L(c.name) || t('k_' + c.kind) }}</p>
            <p v-if="out.fictional" class="fict">{{ L(tpl.note) || t('fictional') }}</p>
          </header>
          <table><tbody>
            <tr><th>{{ t('pcKind') }}</th><td>{{ t('k_' + c.kind) }}</td></tr>
            <tr><th>{{ t('pcEquip') }}</th><td>{{ c.equipment || '　' }}</td></tr>
          </tbody></table>
          <table v-if="c.lines.length" class="ck">
            <thead v-if="c.kind === 'heat'"><tr><th></th><th>{{ t('pf_change') }}</th><th>{{ t('pf_scatter') }}</th><th>{{ t('pf_distortion') }}</th></tr></thead>
            <thead v-else><tr><th></th><th>{{ t('pcOpSize') }}</th><th>{{ t('pf_Z') }}</th><th>{{ t('pcZrange') }}</th><th>{{ t('pf_Zreq') }}</th></tr></thead>
            <tbody>
              <tr v-for="l in c.lines" :key="l.feature">
                <th>{{ ringFeat(c.ring, l.feature) }}</th>
                <template v-if="c.kind === 'heat'"><td class="mono">{{ fmtZ(l.change) }}</td><td class="mono">{{ fmtZ(l.scatter) }}</td><td class="mono">{{ fmtZ(l.distortion) }}</td></template>
                <template v-else><td class="mono">{{ sizeStr(l.size) }}</td><td class="mono">{{ fmtZ(l.Z) }}</td><td class="mono">{{ fmtZ(l.Zmin) }} – {{ fmtZ(l.Zmax) }}</td><td class="mono">{{ fmtZ(l.Zreq) }}</td></template>
              </tr>
            </tbody>
          </table>
          <h2>{{ t('pcParams') }}</h2>
          <table><tbody>
            <tr v-for="(p, j) in c.params" :key="j"><th>{{ p.k }}</th><td class="mono">{{ p.v }} {{ p.u }}</td></tr>
            <tr v-for="j in Math.max(0, 4 - c.params.length)" :key="'e' + j" class="blankrow"><th>　</th><td>　</td></tr>
          </tbody></table>
          <p v-if="c.checks.some((x) => x.status !== 'pass')" class="warn">{{ t('pcSheetWarn') }}：{{ c.checks.filter((x) => x.status !== 'pass').map((x) => (lang === 'zh' ? x.zh : x.en) + '（' + t(x.status) + '）').join('；') }}</p>
          <p class="gen">{{ t('pcSheetFoot') }}</p>
          <p class="sign">{{ t('pcSign') }}</p>
        </section>
      </article>
    </div>
  </div>
</template>
