<template>
  <view>
      <view class="wq-head">
        <view>
          <text class="wq-h1">{{ t("catalog.title") }}</text>
          <text class="wq-muted">{{ t("catalog.lead") }}</text>
        </view>
      </view>
      <text v-if="loading" class="wq-muted">{{ t("common.loading") }}</text>
      <text v-else-if="error" class="wq-error">{{ error }}</text>
      <view v-else-if="!courses.length" class="wq-empty">{{ t("catalog.empty") }}</view>
      <view class="grid">
        <view v-for="(c, i) in courses" :key="c.id" class="cc">
          <view class="cover" :style="{ background: covers[i % covers.length] }">
            <text class="price" :class="c.mode">{{ c.mode === "free" ? t("catalog.free") : money(c) }}</text>
            <text class="cover-name">{{ c.name }}</text>
          </view>
          <view class="cc-body">
            <text class="teachers">{{ c.teachers.join("、") || "—" }}</text>
            <text class="summary">{{ c.blurb || c.summary || t("catalog.noSummary") }}</text>
            <text class="meta">{{ t("catalog.meta", { ch: c.chapters, st: c.students }) }}</text>
            <view class="cc-act">
              <view v-if="c.enrolled" class="wq-btn dark" @click="enter(c.id)">{{ t("catalog.enter") }} →</view>
              <view v-else-if="c.requested" class="wq-btn disabled">{{ t("catalog.requested") }}</view>
              <view v-else-if="!token" class="wq-btn primary" @click="signIn">{{ t("catalog.signInToJoin") }}</view>
              <view v-else-if="c.mode === 'free'" class="wq-btn primary" :class="{ disabled: busy === c.id }" @click="join(c)">{{ t("catalog.join") }}</view>
              <view v-else class="wq-btn primary" @click="asking = c.id; note = ''">{{ t("catalog.request") }}</view>
            </view>
            <view v-if="asking === c.id" class="ask">
              <text class="wq-muted block">{{ t("catalog.requestHint", { price: money(c) }) }}</text>
              <textarea v-model="note" class="wq-textarea short" :placeholder="t('catalog.notePh')" />
              <view class="wq-row">
                <view class="wq-btn primary small" :class="{ disabled: busy === c.id }" @click="join(c)">{{ t("catalog.sendRequest") }}</view>
                <text class="wq-link" @click="asking = 0">{{ t("common.cancel") }}</text>
              </view>
            </view>
          </view>
        </view>
      </view>
  </view>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { type CatalogCourse, accountApi } from "../../accountApi";
import { ApiError, token } from "../../api";
import { errorText, t } from "../../i18n";

const courses = ref<CatalogCourse[]>([]);
const loading = ref(true);
const error = ref("");
const busy = ref(0);
const asking = ref(0);
const note = ref("");
const covers = ["linear-gradient(135deg,#14212b,#1f6f8b)", "linear-gradient(135deg,#2e5b4a,#7fb069)", "linear-gradient(135deg,#5b2e4a,#c06c84)",
  "linear-gradient(135deg,#3d3a8c,#6c8cd5)", "linear-gradient(135deg,#8a5a00,#f2b705)"];

async function load() {
  loading.value = true;
  error.value = "";
  try { courses.value = (await accountApi.catalog()).courses; } catch (e) { error.value = errorText(e instanceof ApiError ? e.code : "unknown"); }
  finally { loading.value = false; }
}
async function join(c: CatalogCourse) {
  busy.value = c.id;
  try {
    const r = await accountApi.join(c.id, note.value);
    asking.value = 0;
    if (r.status === "enrolled") return enter(c.id);
    uni.showToast({ title: t("catalog.requestSent"), icon: "none" });
    await load();
  } catch (e) { error.value = errorText(e instanceof ApiError ? e.code : "unknown"); } finally { busy.value = 0; }
}
const enter = (id: number) => uni.navigateTo({ url: `/pages/course/course?id=${id}` });
const signIn = () => uni.navigateTo({ url: `/pages/login/login?back=${encodeURIComponent("/pages/catalog/catalog")}` });
const money = (c: CatalogCourse) => (c.currency === "USD" ? `$${c.price}` : `¥${c.price}`);
onMounted(load);
defineExpose({ load });
</script>

<style scoped>
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 18px; margin-top: 8px; }
.cc { background: #fff; border: 1px solid var(--wq-line); border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; }
.cover { height: 120px; position: relative; padding: 14px; display: flex; align-items: flex-end; box-sizing: border-box; }
.cover-name { color: #fff; font-weight: 700; font-size: 18px; line-height: 1.35; text-shadow: 0 1px 3px rgba(0,0,0,.3); }
.price { position: absolute; top: 12px; right: 12px; font-size: 13px; font-weight: 700; border-radius: 999px; padding: 2px 10px; }
.price.free { background: #e3f3ea; color: var(--wq-ok); }
.price.paid { background: var(--wq-accent); color: var(--wq-ink); }
.cc-body { padding: 14px 16px 16px; display: flex; flex-direction: column; gap: 6px; flex: 1; }
.teachers { font-size: 13px; color: var(--wq-link); }
.summary { font-size: 14px; color: var(--wq-text); line-height: 1.6; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.meta { font-size: 12px; color: var(--wq-muted); }
.cc-act { margin-top: auto; padding-top: 8px; }
.ask { margin-top: 8px; }
.short { min-height: 60px; margin: 6px 0; }
.block { display: block; }
</style>
