<script setup lang="ts">
import type { INode, IMappedNodes } from '@/interfaces/node'

defineProps<{
  nodeData: INode
  selectedNode: IMappedNodes | null
}>()
</script>

<template>
  <div class="space-y-6">
    <div class="p-6">
      <h3 class="text-lg font-semibold mb-4">Resumo do Nó</h3>
      <div class="space-y-4">
        <div
          class="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-600"
        >
          <span class="text-gray-600 dark:text-gray-400">Tipo:</span>
          <span class="font-medium truncate">{{ selectedNode?.name }}</span>
        </div>

        <div
          class="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-600"
        >
          <span class="text-gray-600 dark:text-gray-400">Título:</span>
          <span class="font-medium truncate">{{ nodeData.title }}</span>
        </div>

        <div
          v-if="nodeData.description"
          class="flex items-start justify-between py-2 border-b border-gray-200 dark:border-gray-600"
        >
          <span class="text-gray-600 dark:text-gray-400">Descrição:</span>
          <span class="font-medium text-right max-w-xs truncate">{{ nodeData.description }}</span>
        </div>

        <div
          v-if="nodeData.settings && selectedNode?.type === 'conditional'"
          class="flex items-start justify-between py-2 border-b border-gray-200 dark:border-gray-600"
        >
          <span class="text-gray-600 dark:text-gray-400">Expressão:</span>
          <span class="font-medium text-right max-w-xs truncate">{{ nodeData.settings }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
