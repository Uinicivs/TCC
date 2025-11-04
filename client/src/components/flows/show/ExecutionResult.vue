<template>
  <div class="mt-4 p-3 rounded-lg result-wrapper">
    <h4 class="font-medium mb-2 flex items-center gap-2">
      <i class="pi pi-check-circle text-emerald-600" />
      Resultado da Execução
    </h4>
    <div class="p-3 font-mono text-sm">
      <pre>{{ JSON.stringify(result, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  result: unknown
}

defineProps<Props>()
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-break: break-word;
}

.result-wrapper {
  border: 1px solid var(--p-surface-200);
}
</style>
