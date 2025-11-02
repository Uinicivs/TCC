<template>
  <div class="my-4">
    <DataTable :value="cases" responsiveLayout="scroll" size="small">
      <Column
        v-for="variable in variables"
        :key="variable.displayName"
        :header="variable.displayName"
        class="w-full"
      >
        <template #body="{ data }">
          <span class="text-sm">
            {{ data.concrete?.[variable.displayName] ?? '-' }}
          </span>
        </template>
      </Column>
      <Column header="Resultado" class="min-w-[200px]">
        <template #body="{ data }">
          <pre class="text-xs font-mono rounded">{{
            formatResponse(data.endMetadata?.response)
          }}</pre>
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DataTable, Column } from 'primevue'
import { useFlowStore } from '@/stores/flow'
import type { Variable } from '@/interfaces/variables'
import type { TestFlowCase } from '@/interfaces/testFlow'

defineProps<{ cases: TestFlowCase[] }>()
const flowStore = useFlowStore()

const variables = computed<Variable[]>(() => flowStore.getStartNodeVariables)

const formatResponse = (response: unknown): string => {
  if (!response) return '-'

  try {
    if (typeof response === 'string') {
      const parsed = JSON.parse(response)
      return JSON.stringify(parsed, null, 2)
    }
    return JSON.stringify(response, null, 2)
  } catch {
    return String(response)
  }
}
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-break: keep-all;
}
</style>
