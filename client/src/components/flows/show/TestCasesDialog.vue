<template>
  <Dialog
    v-model:visible="isVisible"
    modal
    dismissable-mask
    :header="`Casos de Teste - ${nodeName}`"
    :style="{ width: '50rem' }"
    :breakpoints="{ '960px': '75vw', '641px': '90vw' }"
  >
    <TestedCasesTable :cases="cases" />
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Dialog } from 'primevue'
import TestedCasesTable from '@/components/flows/show/TestedCasesTable.vue'
import type { TestFlowCase } from '@/interfaces/testFlow'

interface Props {
  nodeName?: string
}

defineProps<Props>()

const isVisible = ref(false)
const cases = ref<TestFlowCase[]>([])

const open = (testCases: TestFlowCase[]) => {
  cases.value = testCases
  isVisible.value = true
}

const close = () => {
  isVisible.value = false
}

defineExpose({
  open,
  close,
})
</script>
