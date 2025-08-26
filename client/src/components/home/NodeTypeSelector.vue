<script setup lang="ts">
import { Card, ScrollPanel } from 'primevue'

import type { IMappedNodes } from '@/interfaces/node'

defineProps<{ availableNodeTypes: IMappedNodes[] }>()

const emit = defineEmits<{ select: [node: IMappedNodes] }>()
</script>

<template>
  <ScrollPanel style="width: 100%; height: 200px" class="pr-2">
    <div class="grid md:grid-cols-2 gap-4 sm:grid-cols-1">
      <Card
        v-for="node in availableNodeTypes"
        :key="node.type"
        class="border-[#e2e8f0] border-1 dark:border-neutral-800 !shadow-none cursor-pointer hover:shadow-lg transition-shadow duration-200"
        @click="emit('select', node)"
      >
        <template #content>
          <div class="h-full flex gap-4 items-center">
            <i
              v-if="node.icon"
              :class="[node.icon, node.iconColor]"
              class="pi rounded-sm content-center"
              style="font-size: 1.2em"
            />

            <div class="overflow-auto">
              <h4 class="text-lg font-semibold">
                {{ node.name }}
              </h4>

              <p class="text-sm">
                {{ node.description }}
              </p>
            </div>
          </div>
        </template>
      </Card>
    </div>
  </ScrollPanel>
</template>
