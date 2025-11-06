<template>
  <div>
    <div v-for="(testCase, index) in cases" :key="index" class="space-y-4">
      <DataTable :value="[testCase]" responsiveLayout="scroll" size="small" class="mb-4">
        <Column
          v-for="variable in variables"
          :key="variable.displayName"
          :header="variable.displayName"
        >
          <template #body="{ data }">
            <span class="text-sm">
              {{ data.concrete?.[variable.displayName] ?? '-' }}
            </span>
          </template>
        </Column>
      </DataTable>

      <ExecutionResult v-if="testCase.endMetadata" :result="testCase.endMetadata" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DataTable, Column } from 'primevue'

import ExecutionResult from '@/components/flows/show/ExecutionResult.vue'

import { useFlowStore } from '@/stores/flow'
import type { Variable } from '@/interfaces/variables'
import type { TestFlowCase } from '@/interfaces/testFlow'

defineProps<{ cases: TestFlowCase[] }>()
const flowStore = useFlowStore()

const variables = computed<Variable[]>(() => flowStore.getStartNodeVariables)
</script>
