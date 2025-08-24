<script setup lang="ts">
import { computed, onMounted, type Component } from 'vue'
import { storeToRefs } from 'pinia'
import { VueFlow, type NodeDragEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'

import { useFlowStore } from '@/stores/flow'

import { Start, Conditional, End } from '@/components/nodes'

import { nodes as mappedNodes } from '@/constants/nodes'
import { DEFAULT_NODE_TITLES } from '@/constants/nodeConfig'

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

onMounted(() => {
  const startNode = {
    id: 'start-node',
    position: { x: window.innerWidth / 2 - 100, y: 100 },
    type: 'start',
    data: {
      title: DEFAULT_NODE_TITLES.start,
      parent: null,
    },
  }

  flowStore.addNodes(startNode)
})
</script>

<template>
  <div class="h-screen">
    <VueFlow :nodes :edges @nodeDragStop="onNodeDragStop">
      <Background variant="dots" />
      <Controls :showInteractive="false" />

      <template v-for="(node, type) in nodeComponents" :key="type" #[`node-${type}`]="props">
        <component :is="node" v-bind="props" />
      </template>
    </VueFlow>
  </div>
</template>
