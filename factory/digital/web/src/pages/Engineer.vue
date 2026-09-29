<template>
  <div class="page">
    <TaskBar v-if="teachStatus" :t="teachStatus" />
    <div class="page-title"><h1>设计与工艺</h1><span class="muted">工艺员工作区 · 输出轴 SH-301 的设计版本、工艺路线与键槽 G 代码</span></div>

    <div class="row">
      <section class="card grow">
        <div class="card-head"><h2>设计版本</h2><span class="muted small">由 FreeCAD 发布宏经总线发来（design/sh-301/release）</span></div>
        <div v-if="!d.releases.length" class="empty">还没有发布过新版本。现行为工厂数据里的第 1 版。</div>
        <table v-else class="t">
          <thead><tr><th>版本</th><th>时间</th><th>设计者</th><th>改动</th><th>BOM（45 钢）</th><th>文件</th></tr></thead>
          <tbody><tr v-for="r in d.releases" :key="r.id">
            <td class="mono b">rev {{ r.revision }}</td><td class="small">{{ timeOf(r.ts) }}</td><td>{{ r.author }}</td>
            <td>{{ r.change_note || '—' }}</td><td class="mono">{{ r.bom?.[0]?.qty }} kg</td>
            <td class="small"><a v-for="f in r.files" :key="f.sha256" :href="'/api' + f.url.replace(/^\/api/, '')" target="_blank" class="flink">{{ f.kind === 'drawing' ? '零件图' : f.kind === 'step' ? 'STEP' : f.name }}</a></td>
          </tr></tbody>
        </table>
        <div v-if="drawing" class="drawing"><img :src="drawing" alt="最新版零件图"></div>
      </section>
      <section class="card side">
        <div class="card-head"><h2>怎样发布新版本</h2></div>
        <ol class="small steps">
          <li>在 FreeCAD 里打开“宏 → 宏…”，把宏目录设为 <span class="mono">digital\freecad</span>。</li>
          <li>用 VS Code 打开 <span class="mono">wq_shaft.py</span>，修改 <span class="mono">PARAMS</span>（例如键槽长 45 → 42），保存。</li>
          <li>打开 <span class="mono">wq_publish.py</span>，把 CONFIG 里的名字改成你的名字，然后执行这个宏。</li>
          <li>回到这里刷新：新版本、零件图、G 代码出现；ERPNext 里 SH-301 的“设计版本”加一。</li>
        </ol>
        <p class="muted small">没装 FreeCAD 的电脑也能发布（不导出 STEP）：<span class="mono">py wq_publish.py --note "改动说明"</span></p>
        <div v-for="a in alerts" :key="a.id" class="alert small"><b>{{ a.title }}</b><div>{{ a.detail }}</div></div>
      </section>
    </div>

    <div class="row">
      <section class="card grow">
        <div class="card-head"><h2>键槽 G 代码</h2><span class="muted small">design/sh-301/gcode · 下达工单时随“铣键槽”工序派给 KEY-01</span>
          <router-link v-if="g" :to="{ path: '/3d', query: { gcode: g.gcode_ref } }" class="more">在 3D 车间回放 →</router-link></div>
        <div v-if="!g" class="empty">还没有 G 代码（随设计发布一起生成）。</div>
        <template v-else>
          <p class="small">rev {{ g.revision }} · 刀具 {{ g.tools.map((t) => t.type + ' Ø' + t.diameter_mm).join('、') }} ·
            切削长度 {{ g.cut_length_mm }} mm · 预计 {{ Math.round(g.est_time_s / 60 * 10) / 10 }} 分钟</p>
          <GcodeView :code="code" :slot="g.slot" />
          <pre class="code">{{ code }}</pre>
        </template>
      </section>
      <section class="card side">
        <div class="card-head"><h2>工艺路线 {{ rt?.routing }}</h2></div>
        <table v-if="rt" class="t">
          <thead><tr><th>工序</th><th class="num">分钟/件</th><th>设备</th></tr></thead>
          <tbody><tr v-for="o in rt.operations" :key="o.operation">
            <td>{{ o.operation.split(' ')[0] }}</td><td class="num">{{ o.minutes }}</td><td class="mono small">{{ o.units.map((u) => u.toUpperCase()).join(' / ') }}</td>
          </tr></tbody>
        </table>
        <p v-if="rt" class="small muted">标准成本：材料 ${{ rt.std_cost.material }} + 加工 ${{ rt.std_cost.operations }} / 件</p>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { get, session } from '../lib/api';
import { timeOf } from '../lib/fmt';
import GcodeView from '../components/GcodeView.vue';
import TaskBar from '../components/TaskBar.vue';

const d = ref({ releases: [], gcode: [] });
const rt = ref(null);
const code = ref('');
const alerts = ref([]);
const teachStatus = ref(null);
const g = computed(() => d.value.gcode[0]);
const drawing = computed(() => {
  const f = d.value.releases[0]?.files?.find((x) => x.kind === 'drawing');
  return f ? f.url : null;
});
onMounted(async () => {
  [d.value, rt.value] = await Promise.all([get('/design/SH-301'), get('/routing/SH-301')]);
  if (g.value) code.value = await (await fetch(g.value.gcode_ref)).text();
  const al = await get('/history?type=ai.alert&hours=72&limit=50');
  alerts.value = al.filter((a) => (a.data.key || '').startsWith('release:')).slice(0, 3).map((a) => ({ id: a.id, ...a.data }));
  if (session.user.mode === 'teach') teachStatus.value = await get('/teach');
});
</script>

<style scoped>
.grow { flex-grow: 1; min-width: 0; }
.side { width: 360px; flex-shrink: 0; }
.b { font-weight: 600; }
.flink { margin-right: 8px; }
.drawing { margin-top: 12px; border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
.drawing img { width: 100%; display: block; }
.steps { padding-left: 18px; line-height: 1.7; margin: 0 0 8px; }
.alert { background: var(--accent-bg); border-radius: 8px; padding: 8px 10px; margin-top: 8px; }
.code { background: var(--surface-2); border-radius: 8px; padding: 10px 12px; font-family: var(--mono); font-size: 12px; max-height: 220px; overflow: auto; }
@media (max-width: 1100px) { .side { width: auto; } }
</style>
