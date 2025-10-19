<script setup lang="ts">
import type { INode } from '@/interfaces/node'

import NodeTemplate from '@/components/nodes/NodeTemplate.vue'

const { data } = defineProps<{ data: INode; id: string }>()
</script>

<template>
  <NodeTemplate
    class="!w-20"
    container-class="h-20 text-center outline-4 outline-amber-500 !w-full rotate-45"
    :id
    :data
  />
</template>

<style scoped>
:deep(.node-content > div) {
  transform: rotateZ(-45deg);
}

:deep(.add-node-button) {
  bottom: -5em;
}
</style>
