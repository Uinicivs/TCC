<script setup lang="ts">
import { ref } from 'vue'

import type { Node, Edge } from '@vue-flow/core'
import { VueFlow } from '@vue-flow/core'
import { MiniMap } from '@vue-flow/minimap'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'

import Trigger from '@/components/nodes/Trigger.vue'

const nodes = ref<Node[]>([
  {
    id: '1',
    type: 'trigger',
    position: { x: 450, y: 400 },
  },
  {
    id: '2',
    type: 'trigger',
    position: { x: 450, y: 600 },
  },
])
const edges = ref<Edge[]>([
  {
    id: '1',
    source: '1',
    target: '2',
    animated: true,
  },
])
</script>

<template>
  <div class="h-screen">
    <VueFlow :nodes :edges>
      <Background variant="dots" />
      <MiniMap pannable zoomable />
      <Controls :showInteractive="false" />

      <template #node-trigger="props">
        <Trigger v-bind="props" />
      </template>
    </VueFlow>
  </div>
</template>
