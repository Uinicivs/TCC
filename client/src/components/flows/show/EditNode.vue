<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { Button, Drawer, Message } from 'primevue'

import NodeConfigForm from '@/components/flows/show/NodeConfigForm.vue'

import type { INode, IMappedNodes } from '@/interfaces/node'

import { useFlowStore } from '@/stores/flow'

import { nodes } from '@/constants/nodes'
import type { Variable } from '@/interfaces/variables'

const props = defineProps<{
  nodeId: string
}>()

const emit = defineEmits<{
  close: []
}>()

const { getStartNodeVariables, getNodeById, updateNode } = useFlowStore()

const visible = ref(false)
const selectedNode = ref<IMappedNodes | null>(null)

const nodeData = reactive<INode>({
  title: '',
  description: '',
  settings: {},
  parent: null,
  children: [],
})

const shouldDisableNextButton = computed(() => {
  if (selectedNode.value?.type === 'start') {
    const inputs = (nodeData.settings as Record<string, unknown>)?.inputs as Array<Variable>
    return !inputs?.length || !inputs?.every(({ displayName }: Variable) => Boolean(displayName))
  }

  if (selectedNode.value?.type === 'conditional') {
    const expression = nodeData.settings?.expression as string

    if (!expression || !expression.trim()) return true
    if (!getStartNodeVariables.length) return false

    const requiredVariables = getStartNodeVariables.filter(({ required }: Variable) => required)

    if (requiredVariables.length > 0) {
      return !requiredVariables.every(({ displayName }: Variable) =>
        expression.includes(displayName),
      )
    }
  }

  return !hasNodeLabelFilled.value
})

const getDisabledMessage = computed(() => {
  if (!hasNodeLabelFilled.value) {
    return 'Preencha o nome do nó para continuar'
  }

  if (selectedNode.value?.type === 'start') {
    const inputs = (nodeData.settings as Record<string, unknown>)?.inputs as Array<Variable>
    if (!inputs?.length) {
      return 'Adicione pelo menos uma variável de entrada'
    }
    if (!inputs?.every(({ displayName }: Variable) => Boolean(displayName))) {
      return 'Preencha o nome de todas as variáveis'
    }
  }

  if (selectedNode.value?.type === 'conditional') {
    const expression = nodeData.settings?.expression as string
    if (!expression || !expression.trim()) {
      return 'Digite uma expressão para continuar'
    }

    const requiredVariables = getStartNodeVariables.filter(({ required }: Variable) => required)
    if (requiredVariables.length > 0) {
      const missingVariables = requiredVariables.filter(
        ({ displayName }: Variable) => !expression.includes(displayName),
      )
      if (missingVariables.length > 0) {
        const variableNames = missingVariables
          .map(({ displayName }: Variable) => displayName)
          .join(', ')
        return `Inclua as variáveis obrigatórias na expressão: ${variableNames}`
      }
    }
  }

  return ''
})

const getDialogHeader = computed<string>(() => {
  return `Editar ${selectedNode.value?.name}`
})

const hasNodeLabelFilled = computed(() => nodeData.title?.trim().length > 0)

const loadNodeData = () => {
  const currentNode = getNodeById(props.nodeId)

  if (currentNode) {
    const node = currentNode
    const nodeType = node.type as keyof typeof nodes

    selectedNode.value = nodes[nodeType]

    Object.assign(nodeData, {
      ...node.data,
      title: node.data.title || '',
      description: node.data.description || '',
      settings: node.data.settings || {},
      parent: node.data.parent || null,
      children: node.data.children || [],
    })
  }
}

const handleUpdateNode = () => {
  if (!selectedNode.value || !nodeData.title.trim()) return

  const formattedNodeData = JSON.parse(JSON.stringify(nodeData))
  updateNode(props.nodeId, { data: formattedNodeData })
  visible.value = false
  emit('close')
}

const openDrawer = () => {
  visible.value = true
  loadNodeData()
}

const closeDrawer = () => {
  visible.value = false
  emit('close')
}

defineExpose({
  openDrawer,
  closeDrawer,
})
</script>

<template>
  <div class="edit-node-wrapper">
    <Drawer v-model:visible="visible" dismissable-mask position="right" :header="getDialogHeader"
      :style="{ width: '30rem' }" :breakpoints="{ '1199px': '75vw', '575px': '90vw' }" @hide="closeDrawer">
      <NodeConfigForm v-model:nodeData="nodeData" :selected-node="selectedNode" />

      <template #footer>
        <div class="flex flex-col w-full gap-5">
          <transition enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 transform -translate-y-2" enter-to-class="opacity-100 transform translate-y-0"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 transform translate-y-0" leave-to-class="opacity-0 transform -translate-y-2">
            <Message v-if="shouldDisableNextButton && getDisabledMessage" severity="warn" :closable="false" size="small"
              class="mt-5">
              <div class="flex gap-2 items-center">
                <i class="pi pi-exclamation-triangle text-amber-500" />
                <span>
                  {{ getDisabledMessage }}
                </span>
              </div>
            </Message>
          </transition>

          <div class="flex justify-between items-center w-full">
            <Button label="Atualizar nó" class="ml-auto" size="small" icon="pi pi-check"
              :disabled="!hasNodeLabelFilled || shouldDisableNextButton" @click="handleUpdateNode" />
          </div>
        </div>
      </template>
    </Drawer>
  </div>
</template>
