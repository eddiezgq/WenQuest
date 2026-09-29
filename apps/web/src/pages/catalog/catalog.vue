<template>
  <AppShell v-if="token" nav="catalog" :title="t('catalog.title')"><CatalogList ref="list" /></AppShell>
  <PublicFrame v-else><CatalogList ref="list" /></PublicFrame>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { onShow } from "@dcloudio/uni-app";
import AppShell from "../../components/AppShell.vue";
import PublicFrame from "../../components/auth/PublicFrame.vue";
import CatalogList from "../../components/catalog/CatalogList.vue";
import { token } from "../../api";
import { t } from "../../i18n";

// Open to visitors: signed-in people see it inside the platform, others with a sign-in bar.
const list = ref<InstanceType<typeof CatalogList> | null>(null);
let first = true;
onShow(() => {
  if (first) return (first = false);
  list.value?.load();
});
</script>
