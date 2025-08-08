<script setup lang="ts">
import { ref } from 'vue'

import type { Node, Edge } from '@vue-flow/core'
import { VueFlow } from '@vue-flow/core'
import { MiniMap } from '@vue-flow/minimap'
import { Background } from '@vue-flow/background'

const nodes = ref<Node[]>([])
const edges = ref<Edge[]>([])
</script>

<template>
  <div class="h-screen">
    <VueFlow :nodes :edges>
      <Background variant="dots" />
      <MiniMap pannable zoomable />
    </VueFlow>
  </div>
</template>
