<template>
  <router-view v-if="route.meta.public" />
  <div v-else class="shell">
    <nav class="rail" aria-label="工作区">
      <router-link to="/" class="brand">
        <span class="logo">渠</span>
        <span class="brand-text"><b>问渠数字工厂</b><small>WenQuest Digital Factory</small></span>
      </router-link>
      <div class="group">
        <span class="group-title">工作区</span>
        <router-link v-for="n in nav" :key="n.to" :to="n.to" class="nav" :class="{ mine: n.role === session.user?.role }">
          {{ n.label }}<span v-if="n.role === session.user?.role" class="me">我的</span>
        </router-link>
        <a href="#" class="nav" @click.prevent="ai.open = true">AI 工厂助手</a>
        <router-link v-if="session.user?.mode === 'teach'" to="/teach" class="nav">实验 7 · 任务</router-link>
      </div>
      <div class="group">
        <span class="group-title">专业软件</span>
        <a v-for="a in apps" :key="a.name" :href="a.href" :target="a.ext ? '_blank' : null" class="app"
          @click="a.route && ($event.preventDefault(), router.push(a.route))">
          <span>{{ a.name }}</span><span class="muted-r">{{ a.role }}</span>
        </a>
      </div>
      <router-link to="/bus" class="busbox">
        <span class="group-title">统一数据总线</span>
        <span class="bus-state"><i :style="{ background: bus.connected ? 'var(--good)' : 'var(--bad)' }"></i>
          {{ bus.connected ? '已连接' : '未连接' }} · {{ Object.keys(bus.machines).length + Object.keys(bus.agvs).length }} 个设备</span>
        <span class="mono small">wq/gearbox/# · {{ bus.rate }} 条/分</span>
      </router-link>
    </nav>
    <main class="main">
      <header class="top">
        <div class="title">
          <b>问渠减速器厂 · {{ pageName }}</b>
          <small>{{ clock }} · 第 1 班（08:00–17:00）· 数据实时刷新</small>
        </div>
        <div class="modes" role="group" aria-label="模式">
          <button type="button" :class="{ on: session.user?.mode === 'teach' }" @click="setMode('teach')">教学模式</button>
          <button type="button" :class="{ on: session.user?.mode === 'prod' }" :disabled="session.user?.teacher === false"
            :title="session.user?.teacher === false ? '生产模式只对老师开放' : ''" @click="setMode('prod')">生产模式</button>
        </div>
        <label class="role">角色
          <select :value="session.user?.role" @change="setRole($event.target.value)">
            <option v-for="r in rolesFor(session.user)" :key="r.key" :value="r.key">{{ r.name }}</option>
          </select>
        </label>
        <button class="avatar" :title="session.user?.name + '（点击退出）'" @click="doLogout">{{ (session.user?.name || '?').slice(0, 1) }}</button>
      </header>
      <router-view :key="session.user?.mode + session.user?.role" />
    </main>
    <AiDrawer />
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { session, rolesFor, switchTo, logout, loadConfig } from './lib/api';
import { bus, connectBus, setBusMode } from './lib/bus';
import AiDrawer from './components/AiDrawer.vue';
import { ai } from './lib/ai';

const route = useRoute();
const router = useRouter();
const nav = [
  { to: '/', label: '首页 · 运营总览' },
  { to: '/work/planner', label: '订单与计划', role: 'planner' },
  { to: '/work/engineer', label: '设计与工艺', role: 'engineer' },
  { to: '/work/operator', label: '车间执行', role: 'operator' },
  { to: '/work/quality', label: '质量', role: 'quality' },
  { to: '/work/manager', label: '经营与成本', role: 'manager' },
  { to: '/3d', label: '3D 车间' },
];
const cfg = ref({});
const apps = computed(() => [
  { name: 'ERPNext', role: 'ERP / MRP', href: cfg.value.erpnext_url || '#', ext: true },
  { name: 'FreeCAD', role: 'CAD / CAM', href: '/work/engineer', route: '/work/engineer' },
  { name: '车间终端', role: 'MES', href: '/work/operator', route: '/work/operator' },
  { name: 'Node-RED', role: '数据流', href: cfg.value.nodered_url || '#', ext: true },
].filter((a) => a.name !== 'Node-RED' || cfg.value.nodered_url));   // 线上 Node-RED 不对外（第 3 轮 D8）
const pageName = computed(() => ({
  '/': '运营总览', '/work/planner': '订单与计划', '/work/engineer': '设计与工艺', '/work/operator': '车间终端',
  '/work/quality': '质量', '/work/manager': '经营与成本', '/3d': '3D 车间', '/teach': '实验 7', '/bus': '统一数据总线',
}[route.path] || ''));
const clock = ref('');
let timer;
function tick() {
  const d = new Date();
  clock.value = d.toLocaleString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit', weekday: 'short',
    hour: '2-digit', minute: '2-digit', hour12: false });
}
async function setMode(m) { if (session.user.mode !== m && !(m === 'prod' && session.user.teacher === false)) { await switchTo({ mode: m }); setBusMode(m); } }
async function setRole(r) { await switchTo({ role: r }); }
function doLogout() { if (confirm('退出登录？')) { logout(); router.push('/login'); } }

onMounted(async () => {
  tick();
  timer = setInterval(tick, 20000);
  if (session.token) start();
});
watch(() => session.token, (t) => { if (t) start(); });
async function start() {
  try {
    cfg.value = await loadConfig();
    connectBus(cfg.value.mqtt_ws.replace('localhost', location.hostname), session.user.mode);
  } catch (e) { /* 首页会显示错误 */ }
}
onUnmounted(() => clearInterval(timer));
</script>

<style scoped>
.shell { display: flex; min-height: 100vh; }
.rail { width: 208px; flex-shrink: 0; background: var(--rail); color: #E7ECEF; display: flex; flex-direction: column;
  padding: 20px 14px; gap: 22px; position: sticky; top: 0; height: 100vh; overflow-y: auto; }
.brand { display: flex; align-items: center; gap: 10px; padding: 0 6px; color: inherit; text-decoration: none; }
.logo { width: 34px; height: 34px; border-radius: 8px; background: var(--brand); color: var(--ink); display: flex;
  align-items: center; justify-content: center; font-weight: 700; font-size: 18px; }
.brand-text { display: flex; flex-direction: column; line-height: 1.25; }
.brand-text b { font-size: 15px; font-weight: 600; }
.brand-text small { font-size: 11px; color: #9AA8B4; }
.group { display: flex; flex-direction: column; gap: 2px; }
.group-title { font-size: 11px; letter-spacing: .08em; color: var(--rail-muted); padding: 0 10px 6px; }
.nav { display: flex; justify-content: space-between; align-items: center; padding: 9px 10px; border-radius: 6px;
  color: var(--rail-ink); text-decoration: none; font-size: 14px; }
.nav:hover { background: #22303C; text-decoration: none; }
.nav.router-link-exact-active { background: #2E3E4C; color: #fff; font-weight: 500; }
.me { font-size: 10px; background: var(--brand); color: var(--ink); border-radius: 8px; padding: 1px 6px; }
.app { display: flex; justify-content: space-between; align-items: center; padding: 8px 10px; border-radius: 6px;
  color: var(--rail-ink); text-decoration: none; font-size: 13px; }
.app:hover { background: #22303C; text-decoration: none; }
.muted-r { font-size: 11px; color: var(--rail-muted); }
.busbox { margin-top: auto; padding: 12px 10px; border-radius: 8px; background: var(--rail-2); display: flex;
  flex-direction: column; gap: 6px; color: #E7ECEF; text-decoration: none; }
.busbox .group-title { padding: 0; }
.bus-state { font-size: 13px; display: flex; align-items: center; gap: 8px; }
.bus-state i { width: 8px; height: 8px; border-radius: 50%; display: inline-block; }
.busbox .small { color: #9AA8B4; font-size: 11px; }
.main { flex-grow: 1; min-width: 0; display: flex; flex-direction: column; }
.top { height: 64px; flex-shrink: 0; background: #fff; border-bottom: 1px solid var(--line); display: flex;
  align-items: center; padding: 0 28px; gap: 20px; position: sticky; top: 0; z-index: 10; }
.title { display: flex; flex-direction: column; line-height: 1.3; }
.title b { font-size: 17px; font-weight: 600; }
.title small { font-size: 12px; color: var(--muted); }
.modes { margin-left: auto; display: flex; gap: 4px; background: var(--bg); border-radius: 8px; padding: 3px; }
.modes button { height: 30px; padding: 0 14px; border: 0; border-radius: 6px; background: transparent; color: #3D4852; cursor: pointer; }
.modes button.on { background: var(--accent); color: #fff; font-weight: 500; }
.modes button:disabled { opacity: .45; cursor: not-allowed; }
.role { display: flex; align-items: center; gap: 8px; font-size: 13px; color: var(--muted); }
.role select { height: 34px; border: 1px solid var(--line); border-radius: 6px; padding: 0 8px; background: #fff; }
.avatar { width: 34px; height: 34px; border-radius: 50%; background: var(--accent); color: #fff; border: 0;
  font-weight: 600; cursor: pointer; }
@media (max-width: 900px) {
  .shell { flex-direction: column; }
  .rail { width: 100%; height: auto; position: static; flex-direction: row; flex-wrap: wrap; gap: 8px; padding: 10px; }
  .group { flex-direction: row; flex-wrap: wrap; }
  .group-title, .busbox { display: none; }
  .top { padding: 0 16px; gap: 10px; height: auto; flex-wrap: wrap; padding-top: 8px; padding-bottom: 8px; }
  .title small { display: none; }
}
</style>
