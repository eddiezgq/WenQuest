<script setup>
// The digital factory's CAE for a cam system (round 39, step 4d): the arm's strength, natural frequencies and fatigue
// life, and the whole system's multibody dynamics compared with this software's own torque; the example's results
// computed beforehand, and new computations for activated company accounts.
import { computed, onMounted, ref } from 'vue'
import { system, caeExample, sysPayload } from '../sysstore'
import { api } from '../api'
import { t, lang } from '../i18n'
import NumField from './NumField.vue'
import LineChart from './LineChart.vue'

const MATERIALS = [['45-QT', '45 钢（调质）', '45 steel (Q&T)'], ['40Cr-QT', '40Cr（调质）', '40Cr (Q&T)'],
  ['20CrMnTi-CQ', '20CrMnTi（渗碳淬火）', '20CrMnTi (case-hardened)'], ['Q345', 'Q345', 'Q345'],
  ['QT500-7', 'QT500-7 球墨铸铁', 'QT500-7 ductile iron'], ['7075-T6', '7075-T6 铝合金', '7075-T6 aluminium']]
const zh = computed(() => lang.value === 'zh')
const arm = computed(() => system.arm || (system.arm = {}))
const cae = computed(() => system.cae || (system.cae = {}))
const me = ref(null)
const mine = ref({})
const status = ref({})
const fmt = (v, d = 1) => (v == null || !Number.isFinite(+v) ? '—' : (+v).toFixed(d))

onMounted(async () => { try { me.value = await api('/cae/me') } catch { me.value = { configured: false } } })
const gate = computed(() => {
  const m = me.value
  if (!m) return ''
  if (!m.configured) return t('caeNotSetup')
  if (!m.login) return t('caeLogin')
  if (!m.licensed) return t('caeLicense')
  return ''
})

async function poll(jid, key) {
  for (let i = 0; i < 900; i++) {
    const j = await api('/cae/jobs/' + jid)
    status.value = { ...status.value, [key]: j.status + (j.position ? ` · ${zh.value ? '前面还有' : 'ahead'} ${j.position}` : '') }
    if (['done', 'failed', 'error'].includes(j.status)) return j
    await new Promise((r) => setTimeout(r, 3000))
  }
  throw new Error('timeout')
}
async function runArm() {
  status.value = { ...status.value, arm: t('queued') }
  try {
    const r = await api('/cae/arm', sysPayload())
    const j = await poll(r.job.id, 'arm')
    const out = { job: j, loads: r.loads }
    if (j.status === 'done') {
      status.value = { ...status.value, arm: zh.value ? '强度完成，算固有频率…' : 'strength done, natural frequencies…' }
      out.modal = await api(`/cae/jobs/${j.id}/modal`, sysPayload())
      status.value = { ...status.value, arm: zh.value ? '算疲劳寿命…' : 'fatigue life…' }
      out.fatigue = await api(`/cae/jobs/${j.id}/fatigue`, sysPayload())
      status.value = { ...status.value, arm: t('done') }
    }
    mine.value = { ...mine.value, arm: out }
  } catch (e) { status.value = { ...status.value, arm: (zh.value ? e.zh : e.message) || 'error' } }
}
async function runMbd() {
  status.value = { ...status.value, mbd: t('queued') }
  try {
    const r = await api('/cae/mbd', sysPayload())
    const j = await poll(r.job.id, 'mbd')
    const out = { job: j, notes: r.notes }
    if (j.status === 'done') out.compare = await api(`/cae/jobs/${j.id}/compare`, sysPayload())
    status.value = { ...status.value, mbd: t('done') }
    mine.value = { ...mine.value, mbd: out }
  } catch (e) { status.value = { ...status.value, mbd: (zh.value ? e.zh : e.message) || 'error' } }
}
function lifeText(f) {
  const s = f?.summary || f
  if (!s) return '—'
  if (s.infinite || s.life_hours > 1e9) return t('infiniteLife')
  const y = s.life_hours / 24 / 365
  return y >= 1 ? `${fmt(y, 1)} ${zh.value ? '年' : 'years'}` : `${fmt(s.life_hours, 0)} h`
}
const sets = computed(() => {
  const out = []
  if (caeExample.value) out.push({ key: 'ex', title: t('caeExample'), note: zh.value ? caeExample.value.note.zh : caeExample.value.note.en, d: caeExample.value })
  if (mine.value.arm || mine.value.mbd) out.push({ key: 'me', title: t('caeMine'), d: { arm: mine.value.arm, modal: mine.value.arm?.modal, fatigue: mine.value.arm?.fatigue, mbd: mine.value.mbd, compare: mine.value.mbd?.compare } })
  return out
})
function best(motors) { return motors?.joints?.[0]?.best }
</script>

<template>
  <main class="work caew">
    <aside class="edit">
      <div class="pane form">
        <h4>{{ t('arm') }}</h4>
        <NumField :obj="arm" k="R_tip" :label="t('armRtip')" unit="mm" />
        <NumField :obj="arm" k="R_hub" :label="t('armRhub')" unit="mm" />
        <NumField :obj="arm" k="bore" :label="t('armBore')" unit="mm" />
        <NumField :obj="arm" k="w_root" :label="t('armWroot')" unit="mm" />
        <NumField :obj="arm" k="w_tip" :label="t('armWtip')" unit="mm" />
        <NumField :obj="arm" k="R_grip" :label="t('armRgrip')" unit="mm" />
        <NumField :obj="arm" k="r_fork" :label="t('armRfork')" unit="mm" />
        <NumField :obj="arm" k="thickness" :label="t('armT')" unit="mm" />
        <NumField :obj="arm" k="fillet" :label="t('armFillet')" unit="mm" />
        <h4>{{ zh ? '工况' : 'Duty' }}</h4>
        <NumField :obj="cae" k="tool_mass" :label="t('toolMass')" unit="kg" />
        <NumField :obj="cae" k="changes_per_day" :label="t('changesDay')" unit="" />
        <label class="sel">{{ t('material') }}
          <select v-model="cae.material_id"><option v-for="m in MATERIALS" :key="m[0]" :value="m[0]">{{ zh ? m[1] : m[2] }}</option></select></label>
        <p class="note">{{ t('loadsAt') }}</p>
      </div>
    </aside>

    <section class="stage plots">
      <article v-for="s in sets" :key="s.key" class="set">
        <header><h3>{{ s.title }}</h3><p v-if="s.note" class="note">{{ s.note }}</p></header>
        <div class="cards">
          <div v-if="s.d.arm?.job?.stats" class="card">
            <h4>{{ zh ? '换刀臂强度（有限元）' : 'Arm strength (FEA)' }}</h4>
            <dl>
              <div><dt>{{ t('vmMax') }}</dt><dd>{{ fmt(s.d.arm.job.stats.vm_max_mpa) }} MPa</dd></div>
              <div><dt>{{ t('safety') }}</dt><dd>{{ fmt(s.d.arm.job.stats.safety_factor, 2) }}</dd></div>
              <div><dt>{{ t('uMax') }}</dt><dd>{{ fmt(s.d.arm.job.stats.u_max_mm * 1000, 1) }} µm</dd></div>
              <div><dt>{{ t('meshInfo') }}</dt><dd>{{ s.d.arm.job.stats.elements }} · {{ fmt(s.d.arm.job.stats.mesh_size_mm, 1) }} mm</dd></div>
              <div v-if="s.d.arm.loads"><dt>{{ zh ? '每把刀的惯性力' : 'Inertia force per tool' }}</dt><dd>{{ fmt(s.d.arm.loads.F_max, 0) }} N @ {{ fmt(s.d.arm.loads.deg, 0) }}°</dd></div>
            </dl>
          </div>
          <div v-if="s.d.modal?.freqs" class="card">
            <h4>{{ t('modes') }}</h4>
            <dl><div v-for="f in s.d.modal.freqs.slice(0, 4)" :key="f.mode"><dt>{{ f.mode }}</dt><dd>{{ fmt(f.hz, 1) }} Hz</dd></div></dl>
            <p class="note">{{ t('armModalNote') }}</p>
          </div>
          <div v-if="s.d.fatigue" class="card">
            <h4>{{ t('life') }}</h4>
            <p class="big">{{ lifeText(s.d.fatigue) }}</p>
            <p class="note">{{ zh ? `每天 ${cae.changes_per_day || '—'} 次换刀；最危险点应力幅 ${fmt((s.d.fatigue.summary || s.d.fatigue).hot_cycles?.[0]?.sigma_a, 1)} MPa` : `${cae.changes_per_day || '—'} tool changes a day` }}</p>
          </div>
          <div v-if="s.d.compare?.compare" class="card wide">
            <h4>{{ t('caeMbd') }}</h4>
            <dl>
              <div><dt>{{ t('peakMbd') }}</dt><dd>{{ fmt(s.d.compare.compare.peak_mbd) }} N·m</dd></div>
              <div><dt>{{ t('peakCamkit') }}</dt><dd>{{ fmt(s.d.compare.compare.peak_camkit) }} N·m</dd></div>
              <div><dt>{{ t('relDiff') }}</dt><dd>{{ fmt(s.d.compare.compare.rel_rms * 100, 1) }} %</dd></div>
            </dl>
            <LineChart :w="640" :title="t('camTorque')" unit="N·m" :x="s.d.compare.compare.t.map((v) => (v / s.d.compare.compare.t[s.d.compare.compare.t.length - 1]) * 360)"
              :series="[{ y: s.d.compare.compare.mbd, label: 'MuJoCo' }, { y: s.d.compare.compare.camkit, label: zh ? '本软件解析' : 'camkit', cls: 'b' }]" />
            <p class="note">{{ zh ? '横轴为一次换刀的时间进程（0–360 对应开始到结束）。' : 'Horizontal axis: progress through one tool change (0–360 = start to stop).' }}</p>
            <template v-if="best(s.d.compare.motors)">
              <h4>{{ t('motorSel') }}</h4>
              <p class="mono small">{{ best(s.d.compare.motors).motor }} + {{ best(s.d.compare.motors).gear }} · i = {{ best(s.d.compare.motors).ratio }} · {{ zh ? '余量' : 'margin' }} {{ best(s.d.compare.motors).margin_pct }}%</p>
              <p class="note">{{ zh ? '电机库是数字工厂的通用典型值（伺服 + 谐波减速器），选型前以厂家样本为准；本例实际用蜗杆减速器时按其效率另核。' : 'The library holds typical values (servo + harmonic reducer); check against a catalogue. With a worm reducer, check with its efficiency.' }}</p>
            </template>
          </div>
        </div>
      </article>
      <p v-if="!sets.length" class="hint">{{ zh ? '这个项目还没有 CAE 结果。' : 'No CAE results for this project yet.' }}</p>
    </section>

    <aside class="side">
      <h4>{{ t('caeSubmit') }}</h4>
      <p v-if="gate" class="gate">{{ gate }}</p>
      <div class="dl">
        <button type="button" class="ghost" :disabled="!!gate" @click="runArm">{{ t('caeArm') }}</button>
        <p v-if="status.arm" class="note">{{ status.arm }}</p>
        <button type="button" class="ghost" :disabled="!!gate" @click="runMbd">{{ t('caeMbd') }}</button>
        <p v-if="status.mbd" class="note">{{ status.mbd }}</p>
      </div>
      <p class="note">{{ zh ? '计算在问渠数字工厂的计算服务上排队进行（有限元 Gmsh + CalculiX、疲劳 pyLife、多体动力学 MuJoCo），每个单位每天有用量上限。' : 'Runs on the WenQuest digital factory CAE service (Gmsh + CalculiX, pyLife, MuJoCo), queued; each company has a daily allowance.' }}</p>
    </aside>
  </main>
</template>

<style scoped>
.caew { grid-template-rows: auto; }
.caew .stage { grid-row: 1; }
.form { display: grid; gap: 8px; align-content: start; }
h4 { margin: 8px 0 2px; font-size: 13px; }
h3 { margin: 0; font: 700 17px/1.3 var(--serif-zh); }
.note { font-size: 12px; color: var(--muted); margin: 2px 0; }
.sel { display: grid; grid-template-columns: 1fr 140px; align-items: center; gap: 8px; font-size: 13px; }
.plots { display: grid; gap: 14px; align-content: start; padding: 12px; overflow: auto; grid-template-rows: none; }
.set header { margin-bottom: 8px; }
.cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; }
.card { background: var(--paper); border: 1px solid var(--line); border-radius: 8px; padding: 8px 10px; }
.card.wide { grid-column: 1 / -1; }
dl { margin: 0; display: grid; gap: 3px; font-size: 13px; }
dl div { display: flex; justify-content: space-between; gap: 8px; border-bottom: 1px solid var(--line); padding: 2px 0; }
dt { color: var(--muted); } dd { margin: 0; font-family: var(--mono); }
.big { font: 700 20px/1.3 var(--serif-zh); margin: 4px 0; }
.small { font-size: 12.5px; }
.gate { color: var(--hold); background: var(--hold-bg); border-radius: 6px; padding: 6px 8px; font-size: 12.5px; }
.dl { display: grid; gap: 6px; }
.hint { color: var(--muted); }
</style>
