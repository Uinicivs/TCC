<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { VueFlow, type NodeDragEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'

import { useFlowStore } from '@/stores/flow'

import AddNode from '@/components/home/AddNode.vue'
import Trigger from '@/components/nodes/Trigger.vue'

const flowStore = useFlowStore()
const { nodes, edges } = storeToRefs(flowStore)

const onNodeDragStop = (event: NodeDragEvent) => {
  const { node: { id: nodeId, position } } = event
  flowStore.updateNode(nodeId, { position })
}
</script>

<template>
  <div class="h-screen">
    <AddNode v-if="!nodes.length" class="fixed top-20 left-1/2 z-10" :parentId="null" />

    <VueFlow :nodes :edges @nodeDragStop="onNodeDragStop">
      <Background variant="dots" />
      <Controls :showInteractive="false" />

      <template #node-trigger="props">
        <Trigger v-bind="props" />
      </template>

      <template #node-conditional="props">
        <Trigger v-bind="props" />
      </template>
    </VueFlow>
  </div>
</template>
