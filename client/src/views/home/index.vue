<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { VueFlow } from '@vue-flow/core'
import { MiniMap } from '@vue-flow/minimap'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'

import { useFlowStore } from '@/stores/flow'

import Trigger from '@/components/nodes/Trigger.vue'

const { nodes, edges } = storeToRefs(useFlowStore())
</script>

<template>
  <div class="h-screen">
    <VueFlow :nodes :edges>
      <Background variant="dots" />
      <MiniMap pannable zoomable maskColor="#fafafa" />
      <Controls :showInteractive="false" />

      <template #node-trigger="props">
        <Trigger v-bind="props" />
      </template>
    </VueFlow>
  </div>
</template>
