<script setup lang="ts">
import { computed } from 'vue'
import { Card, ScrollPanel } from 'primevue'

import { useFlowStore } from '@/stores/flow'

import type { IMappedNodes } from '@/interfaces/node'

const { availableNodeTypes } = defineProps<{ availableNodeTypes: IMappedNodes[] }>()
const emit = defineEmits<{ select: [node: IMappedNodes] }>()

const { getFirstNode } = useFlowStore()

const availableNodes = computed(() => {
  return getFirstNode
    ? availableNodeTypes.filter((node) => node.type !== 'start')
    : availableNodeTypes
})

const shouldDisableNode = (node: IMappedNodes) => {
  return !getFirstNode && node.type !== 'start'
}

const handleClick = (node: IMappedNodes) => {
  if (shouldDisableNode(node)) return
  emit('select', node)
}
</script>

<template>
  <ScrollPanel style="width: 100%; height: 200px" class="pr-2">
    <div class="space-y-4">
      <Card
        v-for="node in availableNodes"
        :key="node.type"
        class="border-[#e2e8f0] border-1 dark:border-neutral-800 !shadow-none hover:shadow-lg transition-shadow duration-200 w-full"
        :class="{
          disabled: shouldDisableNode(node),
          'cursor-pointer ': !shouldDisableNode(node),
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
