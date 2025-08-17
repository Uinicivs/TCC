<script setup lang="ts">
import { Card } from 'primevue'
import type { IMappedNodes } from '@/interfaces/node'

defineProps<{
  availableNodeTypes: IMappedNodes[]
}>()

const emit = defineEmits<{
  select: [node: IMappedNodes]
}>()
</script>

<template>
  <div class="grid auto-rows-auto grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
    <Card
      v-for="node in availableNodeTypes"
      :key="node.type"
      class="border-[#e2e8f0] border-1 dark:border-neutral-800 !shadow-none h-40 cursor-pointer hover:shadow-lg transition-shadow duration-200 hover:border-blue-300 dark:hover:border-emerald-600"
      @click="emit('select', node)"
    >
      <template #content>
        <div class="h-full flex flex-col justify-between gap-4 text-center">
          <i
            v-if="node.icon"
            :class="[node.icon, node.iconColor]"
            class="pi p-4 rounded-sm w-full h-20 content-center"
            style="font-size: 1.5em"
          />
          <div class="overflow-auto">
            <h4 class="text-lg font-semibold">
              {{ node.name }}
            </h4>
          </div>
        </div>
      </template>
    </Card>
  </div>
</template>
