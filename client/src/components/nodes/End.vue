<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'

import type { INode } from '@/interfaces/node'

import NodeTemplate from '@/components/nodes/NodeTemplate.vue'
import TestCasesDialog from '@/components/flows/show/TestCasesDialog.vue'
import WarningTooltip from '@/components/shared/WarningTooltip.vue'
import { useFlowStore } from '@/stores/flow'

const props = defineProps<{ data: INode; id: string }>()

const flowStore = useFlowStore()
const dialogRef = useTemplateRef('testCasesDialog')

const caseCount = computed(() => {
  return flowStore.getCaseCountByNodeId[props.id] || 0
})

const hasCases = computed(() => caseCount.value > 0)

const prunedReason = computed(() => {
  return flowStore.getPrunedReasonByNodeId(props.id)
})

const handleClick = () => {
  if (hasCases.value && dialogRef.value) {
    const cases = flowStore.getCasesByNodeId(props.id)
    dialogRef.value.open(cases)
  }
}
</script>

<template>
  <div @click="handleClick" :class="{ 'cursor-pointer': hasCases }">
    <transition name="fade">
      <WarningTooltip
        v-if="hasCases"
        type="success"
        message="Clique para visualizar os casos de teste"
      />
    </transition>

    <transition name="fade">
      <WarningTooltip v-if="prunedReason" type="error" :message="prunedReason" />
    </transition>

    <NodeTemplate
      class="!w-20"
      container-class="!rounded-full h-20 text-center !w-full outline-red-500 outline-4"
      :id
      :data
    />
  </div>

  <TestCasesDialog ref="testCasesDialog" :nodeName="data.title" />
</template>
