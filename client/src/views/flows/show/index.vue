<script setup lang="ts">
import { computed, onMounted, ref, type Component } from 'vue'
import { storeToRefs } from 'pinia'
import { onBeforeRouteLeave, useRoute, useRouter } from 'vue-router'
import { VueFlow, type NodeDragEvent } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { ProgressSpinner, Button, Card, Toolbar } from 'primevue'

import { useFlowStore } from '@/stores/flow'

import { getFlowById } from '@/services/flowService'
import { mapSchemaToFlow } from '@/utils/flowFormatters'

import AddNode from '@/components/flows/show/AddNode.vue'
import { Start, Conditional, End } from '@/components/nodes'

import { nodes as mappedNodes } from '@/constants/nodes'

const route = useRoute()
const router = useRouter()
const flowId = route.params.id as string

const flowStore = useFlowStore()
const { nodes, edges } = storeToRefs(flowStore)

const isLoading = ref<boolean>(true)
const error = ref<string | null>(null)
const flowName = ref<string>('')

onMounted(async () => {
  try {
    isLoading.value = true
    error.value = null

    flowStore.setFlowId(flowId)

    const flowData = await getFlowById(flowId)
    flowName.value = flowData.flowName

    if (flowData.nodes && flowData.nodes.length > 0) {
      const frontendNodes = mapSchemaToFlow(flowData.nodes)
      flowStore.setNodes(frontendNodes)
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Erro inesperado ao carregar o fluxo'

    if (err instanceof Error && err.message.includes('não encontrado')) goBack()
  } finally {
    isLoading.value = false
  }
})

onBeforeRouteLeave(() => {
  flowStore.clearFlow()
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

const goBack = () => {
  router.push('/')
}
</script>

<template>
  <div class="h-screen">
    <div class="h-full flex flex-col">
      <div class="flex-1">
        <div v-if="isLoading" class="fixed z-10 w-full h-full backdrop">
          <Card class="w-96 fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <template #content>
              <div class="text-center p-4">
                <ProgressSpinner class="mb-4" />
                <p class="text-muted-color">Carregando fluxo...</p>
              </div>
            </template>
          </Card>
        </div>

        <div v-else-if="error" class="w-full h-full fixed z-10 backdrop">
          <Card class="w-96 fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
            <template #content>
              <div class="text-center">
                <div class="mb-4">
                  <i class="pi pi-exclamation-triangle !text-xl mr-2 inline text-red-500" />
                  <h3 class="font-semibold mb-2 text-xl inline">Erro ao carregar fluxo</h3>
                  <p>{{ error }}</p>
                </div>

                <Button label="Voltar" class="w-full" @click="goBack" size="small" />
              </div>
            </template>
          </Card>
        </div>

        <VueFlow v-else :nodes :edges @nodeDragStop="onNodeDragStop">
          <Toolbar class="w-full z-10 fixed !rounded-t-none">
            <template #start>
              <Button
                icon="pi pi-arrow-left"
                size="small"
                severity="secondary"
                variant="text"
                class="mr-2"
                @click="goBack"
              />

              {{ flowName }}
            </template>
          </Toolbar>

          <AddNode v-if="!nodes.length" class="fixed top-20 left-1/2 z-10" :parentId="null" />
          <Background variant="dots" />
          <Controls :showInteractive="false" />

          <template
            v-for="(nodeComponent, type) in nodeComponents"
            :key="type"
            #[`node-${type}`]="props"
          >
            <component :is="nodeComponent" v-bind="props" />
          </template>
        </VueFlow>
      </div>
    </div>
  </div>
</template>

<style scoped>
.backdrop {
  background: rgba(0, 0, 0, 0.4);
}
</style>
