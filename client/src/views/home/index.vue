<script setup lang="ts">
import { computed, type Component } from 'vue'
import { storeToRefs } from 'pinia'
import { VueFlow, type NodeDragEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'

import { useFlowStore } from '@/stores/flow'

import AddNode from '@/components/home/AddNode.vue'
import { Start, Conditional, End } from '@/components/nodes'

import { nodes as mappedNodes } from '@/constants/nodes'

const flowStore = useFlowStore()
const { nodes, edges } = storeToRefs(flowStore)

const onNodeDragStop = (event: NodeDragEvent) => {
  const {
    node: { id: nodeId, position },
  } = event
  flowStore.updateNode(nodeId, { position })
}

const nodeComponents = computed<Record<keyof typeof mappedNodes, Component>>(() => ({
  start: Start,
  conditional: Conditional,
  end: End,
}))
</script>

<template>
  <div class="h-screen">
    <AddNode v-if="!nodes.length" class="fixed top-20 left-1/2 z-10" :parentId="null" />

    <VueFlow :nodes :edges @nodeDragStop="onNodeDragStop">
      <Background variant="dots" />
      <Controls :showInteractive="false" />

      <template v-for="(node, type) in nodeComponents" :key="type" #[`node-${type}`]="props">
        <component :is="node" v-bind="props" />
      </template>
    </VueFlow>
  </div>
</template>
