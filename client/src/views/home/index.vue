<script setup lang="ts">
import { storeToRefs } from 'pinia'
import { VueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'

import { useFlowStore } from '@/stores/flow'

import Navbar from '@/components/shared/Navbar.vue'
import AddNode from '@/components/home/AddNode.vue'
import Trigger from '@/components/nodes/Trigger.vue'

const { nodes, edges } = storeToRefs(useFlowStore())
</script>

<template>
  <div class="h-screen">
    <Navbar class="z-10 fixed mt-4 mx-4" />
    <VueFlow :nodes :edges>
      <Background variant="dots" />
      <Controls :showInteractive="false" />
      <AddNode />

      <template #node-trigger="props">
        <Trigger v-bind="props" />
      </template>
    </VueFlow>
  </div>
</template>
