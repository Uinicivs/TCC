<script setup lang="ts">
import { computed } from 'vue'
import { Card, ScrollPanel } from 'primevue'

import { useFlowStore } from '@/stores/flow'

import type { IMappedNodes } from '@/interfaces/node'

const { availableNodeTypes, hasEndNodeInPath } = defineProps<{
  availableNodeTypes: IMappedNodes[]
  hasEndNodeInPath: boolean
}>()
const emit = defineEmits<{ select: [node: IMappedNodes] }>()

const { getFirstNode } = useFlowStore()

const availableNodes = computed(() => {
  return getFirstNode
    ? availableNodeTypes.filter((node) => node.type !== 'start')
    : availableNodeTypes
})

const isNodeDisabled = (node: IMappedNodes) => {
  if (!getFirstNode) {
    return node.type !== 'start'
  }

  if (node.type === 'start') {
    return true
  }

  if (node.type === 'end' && hasEndNodeInPath) {
    return true
  }

  return false
}

const getTooltipMessage = (node: IMappedNodes) => {
  if (!getFirstNode && node.type !== 'start') {
    return 'É necessário criar um nó de início primeiro'
  }

  if (node.type === 'end' && hasEndNodeInPath) {
    return 'O nó de fim só pode ser adicionado quando não há outros nós como filhos'
  }

  return ''
}

const handleClick = (node: IMappedNodes) => {
  if (isNodeDisabled(node)) return
  emit('select', node)
}
</script>

<template>
  <ScrollPanel style="width: 100%; height: 500px">
    <div class="space-y-4 h-full">
      <Card
        v-for="node in availableNodes"
        :key="node.type"
        v-tooltip.left="{
          value: getTooltipMessage(node),
          pt: { root: { style: { maxWidth: '15rem' } } },
          showDelay: 300,
        }"
        class="border-[#e2e8f0] border-1 dark:border-neutral-800 !shadow-none transition-shadow duration-200 w-ful"
        :class="{
          disabled: isNodeDisabled(node),
          'cursor-pointer': !isNodeDisabled(node),
          'cursor-not-allowed': isNodeDisabled(node),
        }"
        @click="handleClick(node)"
      >
        <template #content>
          <div class="h-full flex gap-4 items-center">
            <i
              v-if="node.icon"
              :class="[node.icon, node.extraClasses]"
              class="pi rounded-sm content-center"
              style="font-size: 1.2em"
            />

            <div class="overflow-auto">
              <h4 class="text-lg font-semibold">
                {{ node.name }}
              </h4>

              <p class="text-sm text-nowrap truncate">
                {{ node.description }}
              </p>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </ScrollPanel>
</template>

<style scoped>
.disabled {
  opacity: 0.6;
}
</style>
