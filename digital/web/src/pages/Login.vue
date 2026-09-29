<template>
  <div class="wrap">
    <form class="box" @submit.prevent="go">
      <div class="brand"><span class="logo">渠</span><div><b>问渠数字工厂</b><small>WenQuest Digital Factory</small></div></div>
      <p class="muted">一个平台，两种用途：学生在这里扮演工厂的各个岗位完成生产任务；企业在这里接单、设计、排产、加工、检验。</p>
      <div class="field"><label for="n">姓名</label><input id="n" v-model="name" autocomplete="name" required placeholder="例如：王小明"></div>
      <div class="field">
        <label>角色</label>
        <div class="roles">
          <button v-for="r in ROLES" :key="r.key" type="button" :class="{ on: role === r.key }" @click="role = r.key">
            <b>{{ r.name }}</b><small>{{ r.en }}</small>
          </button>
        </div>
      </div>
      <div class="field">
        <label>模式</label>
        <div class="modes">
          <button type="button" :class="{ on: mode === 'teach' }" @click="mode = 'teach'"><b>教学模式</b><small>有任务、提示和评分，机床为仿真</small></button>
          <button type="button" :class="{ on: mode === 'prod' }" @click="mode = 'prod'"><b>生产模式</b><small>工厂日常工作台，AI 可代办</small></button>
        </div>
      </div>
      <div v-if="err" class="err">{{ err }}</div>
      <button class="btn primary big" :disabled="busy">进入工厂</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { login, ROLES } from '../lib/api';

const route = useRoute();
const router = useRouter();
const name = ref('');
const role = ref('manager');
const mode = ref('teach');
const err = ref(null);
const busy = ref(false);
async function go() {
  busy.value = true; err.value = null;
  try {
    await login(name.value.trim(), role.value, mode.value);
    router.push(route.query.next || '/');
  } catch (e) { err.value = e.message; } finally { busy.value = false; }
}
</script>

<style scoped>
.wrap { min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 16px; background: var(--rail); }
.box { width: min(560px, 100%); background: #fff; border-radius: 14px; padding: 28px; display: flex; flex-direction: column; gap: 16px; }
.brand { display: flex; align-items: center; gap: 12px; }
.brand b { font-size: 20px; display: block; }
.brand small { color: var(--muted); }
.logo { width: 44px; height: 44px; border-radius: 10px; background: var(--brand); display: flex; align-items: center;
  justify-content: center; font-weight: 700; font-size: 22px; }
.roles { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; }
.modes { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.roles button, .modes button { border: 1px solid var(--line); background: var(--surface-2); border-radius: 8px; padding: 10px;
  cursor: pointer; display: flex; flex-direction: column; gap: 3px; text-align: left; }
.roles button small, .modes button small { font-size: 11px; color: var(--muted); }
.roles button.on, .modes button.on { border-color: var(--accent); background: var(--accent-bg); }
@media (max-width: 560px) { .roles { grid-template-columns: repeat(3, 1fr); } .modes { grid-template-columns: 1fr; } }
</style>
