<template>
  <Popover ref="test-flow-popover" class="!rounded-xl !shadow-lg">
    <div class="flex flex-col gap-3 min-w-64">
      <p>Você está prestes a testar o fluxo.</p>

      <div class="flex flex-col gap-3 my-2">
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
import { ref, useTemplateRef, watch, onMounted, onUnmounted } from 'vue'
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

const unreachableNodeIds = ref<Set<string>>(new Set())
const reachableNodeIds = ref<Set<string>>(new Set())

onMounted(() => {
  flowStore.setTestResetHandler(resetTestState)
})

onUnmounted(() => {
  flowStore.setTestResetHandler(() => {})
})

watch(
  () => settings.value.showUnreachable,
  (isEnabled) => {
    if (!isEnabled) {
      unreachableNodeIds.value.forEach((nodeId) => {
        flowStore.highlightPathFromNode(nodeId, 'none', 'unreachable')
      })
    } else if (unreachableNodeIds.value.size > 0) {
      unreachableNodeIds.value.forEach((nodeId) => {
        flowStore.highlightPathFromNode(nodeId, 'error', 'unreachable')
      })
    }
  },
)

watch(
  () => settings.value.showReachable,
  (isEnabled) => {
    if (!isEnabled) {
      reachableNodeIds.value.forEach((nodeId) => {
        flowStore.highlightPathFromNode(nodeId, 'none', 'reachable')
      })
    } else if (reachableNodeIds.value.size > 0) {
      reachableNodeIds.value.forEach((nodeId) => {
        flowStore.highlightPathFromNode(nodeId, 'success', 'reachable')
      })
    }
  },
)

const highlightPrunedPaths = (prunedItems: TestFlowPruned[] = []) => {
  unreachableNodeIds.value.clear()

  prunedItems.forEach((item) => {
    if (item.reason && ['unreachable', 'unsatisfiable'].includes(item.reason)) {
      unreachableNodeIds.value.add(item.nodeId)
      if (settings.value.showUnreachable) {
        flowStore.highlightPathFromNode(item.nodeId, 'error', 'unreachable')
      }
    }
  })
}

const highlightReachableEnds = (cases: TestFlowResult['cases'] = []) => {
  const uniqueEndIds = Array.from(new Set((cases || []).map(({ endNodeId }) => endNodeId)))
  reachableNodeIds.value = new Set(uniqueEndIds)

  if (settings.value.showReachable) {
    uniqueEndIds.forEach((endId) => flowStore.highlightPathFromNode(endId, 'success', 'reachable'))
  }
}

const testFlowAction = async () => {
  isLoading.value = true
  try {
    const response: TestFlowResult = await testFlow(props.flowId)
    flowStore.setReductionWarnings(response.reductions || [])
    flowStore.setUncoveredWarnings(response.uncovered || [])
    flowStore.setPrunedReasons(response.pruned || [])
    flowStore.setTestCases(response.cases || [])

    highlightPrunedPaths(response.pruned || [])
    highlightReachableEnds(response.cases || [])
    emit('tested')
  } finally {
    isLoading.value = false
    popover.value?.hide()
  }
}

const resetTestState = () => {
  unreachableNodeIds.value.clear()
  reachableNodeIds.value.clear()
  settings.value.showUnreachable = true
  settings.value.showReachable = false
}

defineExpose({
  toggle: (event: Event) => popover.value?.toggle(event),
  hide: () => popover.value?.hide(),
  resetTestState,
})
</script>
