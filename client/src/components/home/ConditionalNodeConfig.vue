<script setup lang="ts">
import Editor from 'primevue/editor'
import { Tag } from 'primevue'

const expression = defineModel<string>('expression', { required: true })
const tips = [
  {
    label: 'Use operadores de comparação:',
    items: ['==', '!=', '>', '<', '>=', '<='],
  },
  {
    label: 'Use operadores lógicos:',
    items: ['and', 'or', 'not'],
  },
  {
    label: 'Use funções de string:',
    items: ['length()', 'substring()', 'upper()'],
  },
]
</script>

<template>
  <div class="space-y-2">
    <p class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      Expressão <span class="text-red-700">*</span>
    </p>

    <Editor v-model="expression" editorStyle="height: 120px" placeholder="Digite a condição" />

    <div class="p-3">
      <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Dicas de uso:</p>
      <ul class="list-disc list-inside text-sm text-gray-600 dark:text-gray-400 space-y-2">
        <li v-for="(tip, i) in tips" :key="i">
          {{ tip.label }}

          <Tag v-for="(item, index) in tip.items" :key="index" class="mr-2" severity="secondary">
            {{ item }}
          </Tag>
        </li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
:deep(.ql-container) {
  font-family: var(--default-font-family) !important;
}

:deep(.p-tag) {
  padding: 0.25em !important;
}
</style>
