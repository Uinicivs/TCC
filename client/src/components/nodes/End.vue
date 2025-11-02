<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { OverlayBadge } from 'primevue'

import type { INode } from '@/interfaces/node'

import NodeTemplate from '@/components/nodes/NodeTemplate.vue'
import TestCasesDialog from '@/components/flows/show/TestCasesDialog.vue'
import { useFlowStore } from '@/stores/flow'

const props = defineProps<{ data: INode; id: string }>()

const flowStore = useFlowStore()
const dialogRef = useTemplateRef('testCasesDialog')

const caseCount = computed(() => {
  return flowStore.getCaseCountByNodeId[props.id] || 0
})

const hasCases = computed(() => caseCount.value > 0)

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
      <OverlayBadge v-if="hasCases" />
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

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
