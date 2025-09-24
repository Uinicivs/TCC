<script setup lang="ts">
import { computed, onMounted, type Component } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute } from 'vue-router'
import { VueFlow, type NodeDragEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'

import { useFlowStore } from '@/stores/flow'
import { getFlowById } from '@/services/flowService'
import { mapSchemaToFlow } from '@/utils/flowFormatters'

import AddNode from '@/components/flows/show/AddNode.vue'
import { Start, Conditional, End } from '@/components/nodes'

import { nodes as mappedNodes } from '@/constants/nodes'

const route = useRoute()
const flowId = route.params.id as string

const flowStore = useFlowStore()
const { nodes, edges } = storeToRefs(flowStore)

onMounted(async () => {
  flowStore.setFlowId(flowId)

  const flowData = await getFlowById(flowId)

  if (flowData.nodes && flowData.nodes.length > 0) {
    const frontendNodes = mapSchemaToFlow(flowData.nodes)
    flowStore.setNodes(frontendNodes)
  }
})

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
