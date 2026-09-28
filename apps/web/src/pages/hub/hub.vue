<template>
  <AppShell :nav="view" :title="t(view === 'help' ? 'help.title' : 'shell.' + view)">
    <!-- Help: short answers to the questions people ask first -->
    <view v-if="view === 'help'" class="help">
      <text class="h1">{{ t("help.title") }}</text>
      <view v-for="qa in FAQ" :key="qa[0]" class="qa">
        <text class="q">{{ qa[0] }}</text>
        <text class="a">{{ qa[1] }}</text>
      </view>
      <text class="contact">{{ t("help.contact") }}</text>
    </view>

    <!-- Calendar and inbox: new-UI versions come in steps 5 and 4 -->
    <view v-else>
      <text class="h1">{{ t("shell." + view) }}</text>
      <view class="soon">
        <text class="soon-h">{{ t("hub.what") }}</text>
        <text class="soon-p">{{ t("hub." + view) }}</text>
        <text class="soon-step">{{ t("hub.step", { n: view === "calendar" ? 5 : 4 }) }}</text>
        <view v-if="link" class="primary" @click="open(link)">{{ t("hub.classic") }} ↗</view>
      </view>
    </view>
  </AppShell>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { onLoad, onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import { api, token } from "../../api";
import { t } from "../../i18n";
import { classicBase } from "../../store";

// Page query parameters must not fall through onto the layout component.
defineOptions({ inheritAttrs: false });

const FAQ = computed(() => [
  [t("help.qStart"), t("help.aStart")], [t("help.qFind"), t("help.aFind")], [t("help.qSubmit"), t("help.aSubmit")],
  [t("help.qBuild"), t("help.aBuild")], [t("help.qDiffer"), t("help.aDiffer")],
]);
const view = ref("help");
const base = ref(classicBase());
const link = computed(() => {
  if (!base.value) return "";
  if (view.value === "calendar") return `${base.value}/calendar/view.php?view=month`;
  if (view.value === "inbox") return `${base.value}/message/index.php`;
  return "";
});

function open(url: string) {
  // #ifdef H5
  window.open(url, "_blank", "noopener");
  // #endif
  // #ifndef H5
  uni.setClipboardData({ data: url, success: () => uni.showToast({ title: t("activity.linkCopied"), icon: "none" }) });
  // #endif
}

onLoad((q: any) => {
  view.value = ["calendar", "inbox", "help"].includes(q?.view) ? q.view : "help";
});
onShow(async () => {
  if (!token.value) return uni.reLaunch({ url: "/pages/login/login" });
  uni.setNavigationBarTitle({ title: t(view.value === "help" ? "help.title" : "shell." + view.value) });
  if (!base.value) {
    try { await api.me(); base.value = classicBase(); } catch { /* the page still explains itself */ }
  }
});
</script>

<style scoped>
.h1 { display: block; font-size: 26px; font-weight: 700; color: var(--wq-ink); margin-bottom: 18px; }
.help { max-width: 820px; }
.qa { background: #fff; border: 1px solid var(--wq-line); border-radius: 6px; padding: 16px 20px; margin-bottom: 10px; }
.q { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 6px; }
.a { display: block; color: var(--wq-text); line-height: 1.75; }
.contact { display: block; color: var(--wq-muted); margin-top: 16px; }
.soon { max-width: 820px; background: #fff; border: 1px solid var(--wq-line); border-left: 4px solid var(--wq-accent); border-radius: 6px; padding: 18px 22px; }
.soon-h { display: block; font-weight: 600; color: var(--wq-ink); margin-bottom: 6px; }
.soon-p { display: block; color: var(--wq-text); line-height: 1.75; }
.soon-step { display: block; font-size: 13px; color: var(--wq-muted); margin-top: 10px; }
.primary { display: inline-block; margin-top: 14px; background: var(--wq-accent); color: var(--wq-ink); font-weight: 600; padding: 9px 18px; border-radius: 8px; cursor: pointer; }
</style>
