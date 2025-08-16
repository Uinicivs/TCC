<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'

import { useFlowStore } from '@/stores/flow'

import AddNode from '@/components/home/AddNode.vue'
import Trigger from '@/components/nodes/Trigger.vue'

const { nodes, edges } = storeToRefs(useFlowStore())
</script>

<template>
  <div class="h-screen">
    <AddNode v-if="!nodes.length" class="fixed top-20 left-1/2 z-10" :parentId="null" />

    <VueFlow :nodes :edges>
      <Background variant="dots" />
      <Controls :showInteractive="false" />

      <template #node-trigger="props">
        <Trigger v-bind="props" />
      </template>
    </VueFlow>
  </div>
</template>
