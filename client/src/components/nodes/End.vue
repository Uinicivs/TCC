<script setup lang="ts">
import type { INode } from '@/interfaces/node'

import NodeTemplate from '@/components/nodes/NodeTemplate.vue'

defineProps<{ data: INode; id: string }>()
</script>

<template>
  <NodeTemplate
    class="!w-20"
    container-class="!rounded-full h-20 text-center !w-full outline-red-500 outline-4"
    :id
    :data
  />
</template>
