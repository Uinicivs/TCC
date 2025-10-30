<template>
  <Popover ref="test-flow-popover">
    <div class="flex flex-col gap-3 min-w-64">
      <p>Você está prestes a testar o fluxo.</p>

      <div class="flex flex-col gap-2">
        <label class="text-sm flex items-center justify-between gap-3">
          Mostrar caminhos nunca alcançados
          <ToggleSwitch v-model="settings.showUnreachable" />
        </label>

        <label class="text-sm flex items-center justify-between gap-3">
          Mostrar caminhos alcançáveis
          <ToggleSwitch v-model="settings.showReachable" />
        </label>
      </div>

      <Button
        :loading="isLoading"
        label="Testar"
        size="small"
        severity="primary"
        @click="testFlowAction"
      />
    </div>
  </Popover>
</template>

<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { Popover, Button, ToggleSwitch } from 'primevue'

import { testFlow } from '@/services/flowService'
import { useFlowStore } from '@/stores/flow'
import type { TestFlowResult, TestFlowPruned } from '@/interfaces/testFlow'

interface Props {
  flowId: string
}

const props = defineProps<Props>()

const emit = defineEmits(['tested'])

const isLoading = ref(false)
const popover = useTemplateRef('test-flow-popover')
const flowStore = useFlowStore()

const settings = ref({
  showUnreachable: true,
  showReachable: false,
})

const highlightPrunedPaths = (prunedItems: TestFlowPruned[] = []) => {
  prunedItems.forEach((item) => {
    if (item.reason === 'unreachable' && settings.value.showUnreachable) {
      flowStore.highlightPathFromNode(item.nodeId, 'error')
    }
  })
}

// const highlightReachableEnds = (cases: TestFlowResult['cases'] = []) => {
//   if (settings.value.showReachable) {
//     const uniqueEndIds = Array.from(new Set((cases || []).map(({ endNodeId }) => endNodeId)))
//     uniqueEndIds.forEach((endId) => flowStore.highlightPathFromNode(endId))
//   }
// }

const testFlowAction = async () => {
  isLoading.value = true
  try {
    const response: TestFlowResult = await testFlow(props.flowId)
    flowStore.setReductionWarnings(response.reductions || [])

    highlightPrunedPaths(response.pruned || [])
    // highlightReachableEnds(response.cases || [])
    emit('tested')
  } finally {
    isLoading.value = false
    popover.value?.hide()
  }
}

defineExpose({
  toggle: (event: Event) => popover.value?.toggle(event),
  hide: () => popover.value?.hide(),
})
</script>
