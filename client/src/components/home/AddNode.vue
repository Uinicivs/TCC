<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { storeToRefs } from 'pinia'
import {
  Button,
  Dialog,
  Card,
  Stepper,
  StepList,
  Step,
  InputText,
  Textarea,
  Message,
} from 'primevue'
import type { Node } from '@vue-flow/core'

import type { INode, IMappedNodes } from '@/interfaces/node'
import { nodes as mappedNodes } from '@/constants/nodes'

import { useFlowStore } from '@/stores/flow'

const flowStore = useFlowStore()
const { nodes } = storeToRefs(flowStore)

const steps = {
  chooseNode: 1,
  setupTitle: 2,
  setupNode: 3,
}

const visible = ref(false)
const currentStep = ref(steps.chooseNode)
const selectedNode = ref<IMappedNodes | null>(null)

const nodeData = reactive<INode>({ title: '' })

const toggleCreateNodeDialog = () => {
  visible.value = !visible.value
  if (visible.value) {
    currentStep.value = 1
    selectedNode.value = null
    nodeData.title = ''
  }
}

const handleNodeSelect = (node: IMappedNodes) => {
  selectedNode.value = node
  currentStep.value = steps.setupTitle
}

const handleNextStep = () => {
  if (currentStep.value >= steps.setupNode) return
  currentStep.value++
}

const handlePreviousStep = () => {
  if (currentStep.value <= steps.chooseNode) return
  currentStep.value--
}

const handleStepClick = (stepNumber: number) => {
  if (stepNumber === steps.chooseNode) {
    currentStep.value = steps.chooseNode
    return
  }

  if (stepNumber === steps.setupTitle && !hasNodeTypeSelected.value) return

  if (stepNumber === steps.setupNode && (!hasNodeTypeSelected.value || !hasNodeLabelFilled.value)) {
    return
  }

  currentStep.value = stepNumber
}

const handleCreateNode = () => {
  if (!selectedNode.value || !nodeData.title.trim()) return

  const [{ position: lastNodePosition } = {}] = nodes.value.slice(-1)
  const axiosY = (lastNodePosition?.y ?? 0) + 200

  const formatNode: Node = {
    id: Date.now().toString(),
    position: { x: window.innerWidth / 2 - 150, y: axiosY },
    type: selectedNode.value.type,
    data: nodeData,
  }

  flowStore.addNodes(formatNode)
  toggleCreateNodeDialog()
}

const handleConfigData = (configData: Record<string, any>) => {
  nodeData.config = configData
}

const availableNodeTypes = computed<Array<IMappedNodes>>(() => Object.values(mappedNodes))
const hasNodeTypeSelected = computed(() => selectedNode.value !== null)
const hasNodeLabelFilled = computed(() => nodeData.title.trim().length > 0)
const shouldShowConfigStep = computed(() => !!selectedNode.value?.configComponent)
const getDialogHeader = computed<string>(() => {
  switch (currentStep.value) {
    case steps.chooseNode:
      return 'Escolha o tipo do nó'
    case steps.setupTitle:
      return `Configurar ${selectedNode.value?.name}`
    case steps.setupNode:
      return `Configurar ${selectedNode.value?.name}`
    default:
      return ''
  }
})
</script>

<template>
  <div>
    <Button
      class="text-4xl"
      icon="pi pi-plus"
      severity="secondary"
      size="small"
      rounded
      @click="toggleCreateNodeDialog"
    />

    <Dialog
      v-model:visible="visible"
      dismissable-mask
      modal
      :draggable="false"
      :header="getDialogHeader"
      :style="{ width: '60rem' }"
      :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
      @hide="selectedNode = null"
    >
      <div class="mb-6 sticky top-0 z-10 pb-2 stepper">
        <Stepper :value="currentStep" class="w-full">
          <StepList>
            <Step
              :value="steps.chooseNode"
              :class="{ 'cursor-pointer': true }"
              @click="handleStepClick(steps.chooseNode)"
            >
              <span class="hidden sm:inline">Selecionar tipo</span>
            </Step>
            <Step
              :value="steps.setupTitle"
              :disabled="!hasNodeTypeSelected"
              :class="{
                'cursor-pointer': hasNodeTypeSelected,
              }"
              @click="hasNodeTypeSelected ? handleStepClick(steps.setupTitle) : null"
            >
              <span class="hidden sm:inline">
                {{ shouldShowConfigStep ? 'Configurar nó' : 'Configurar nó' }}
              </span>
            </Step>
            <Step
              :value="steps.setupNode"
              :disabled="!hasNodeTypeSelected || !hasNodeLabelFilled"
              :class="{ 'cursor-pointer': hasNodeTypeSelected && hasNodeLabelFilled }"
              @click="
                hasNodeTypeSelected && hasNodeLabelFilled ? handleStepClick(steps.setupNode) : null
              "
            >
              <span class="hidden sm:inline">Revisar</span>
            </Step>
          </StepList>
        </Stepper>
      </div>
      <div v-if="currentStep === steps.chooseNode" class="space-y-6">
        <div class="grid auto-rows-auto grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <Card
            v-for="node in availableNodeTypes"
            :key="node.type"
            class="border-[#e2e8f0] border-1 dark:border-neutral-800 !shadow-none h-40 cursor-pointer hover:shadow-lg transition-shadow duration-200 hover:border-blue-300 dark:hover:border-emerald-600"
            @click="handleNodeSelect(node)"
          >
            <template #content>
              <div class="h-full flex flex-col justify-between gap-4 text-center">
                <i
                  v-if="node.icon"
                  :class="[node.icon, node.iconColor]"
                  class="pi p-4 rounded-sm w-full h-20 content-center"
                  style="font-size: 1.5em"
                />
                <div class="overflow-auto">
                  <h4 class="text-lg font-semibold">
                    {{ node.name }}
                  </h4>
                </div>
              </div>
            </template>
          </Card>
        </div>
      </div>
      <div v-if="currentStep === steps.setupTitle" class="space-y-6">
        <div class="space-y-4">
          <div class="space-y-2">
            <label
              for="nodeLabel"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Label do nó <span class="text-red-700">*</span>
            </label>
            <InputText
              id="nodeLabel"
              v-model="nodeData.title"
              placeholder="Digite um nome para o nó"
              required
              class="w-full"
              :class="{ 'p-invalid': !nodeData.title.trim() && currentStep >= steps.setupNode }"
            />
            <Message size="small" severity="secondary" variant="simple">
              Este será o nome exibido no nó.
            </Message>
          </div>
          <div class="space-y-2">
            <label
              for="nodeDescription"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300"
            >
              Descrição
            </label>
            <Textarea
              id="nodeDescription"
              v-model="nodeData.description"
              placeholder="Digite uma descrição para o nó (opcional)"
              rows="3"
              class="w-full"
            />
            <Message size="small" severity="secondary" variant="simple">
              Descrição opcional para documentar o propósito do nó.
            </Message>
          </div>
        </div>
        <component
          :is="selectedNode?.configComponent"
          v-if="shouldShowConfigStep"
          @updated:config="handleConfigData"
          class="w-full"
        />
      </div>
      <div v-if="currentStep === steps.setupNode" class="space-y-6">
        <div class="p-6">
          <h3 class="text-lg font-semibold mb-4">Resumo do Nó</h3>
          <div class="space-y-4">
            <div
              class="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-600"
            >
              <span class="text-gray-600 dark:text-gray-400">Tipo:</span>
              <span class="font-medium truncate">{{ selectedNode?.name }}</span>
            </div>
            <div
              class="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-600"
            >
              <span class="text-gray-600 dark:text-gray-400">Title:</span>
              <span class="font-medium truncate">{{ nodeData.title }}</span>
            </div>
            <div
              v-if="nodeData.description"
              class="flex items-start justify-between py-2 border-b border-gray-200 dark:border-gray-600"
            >
              <span class="text-gray-600 dark:text-gray-400">Descrição:</span>
              <span class="font-medium text-right max-w-xs truncate">{{
                nodeData.description
              }}</span>
            </div>
          </div>
        </div>
        <div v-if="shouldShowConfigStep" class="px-6">
          <component :is="selectedNode?.configComponent" :config="nodeData.config" class="w-full" />
        </div>
      </div>
      <template #footer>
        <div class="flex justify-between items-center w-full pt-5">
          <Button
            v-if="currentStep > steps.chooseNode"
            label="Anterior"
            class="self-start"
            size="small"
            icon="pi pi-chevron-left"
            severity="secondary"
            outlined
            @click="handlePreviousStep"
          />
          <div class="flex gap-2 w-full">
            <Button
              v-if="currentStep < steps.setupNode"
              class="ml-auto"
              icon="pi pi-chevron-right"
              size="small"
              icon-pos="right"
              label="Próximo"
              :disabled="
                (currentStep === 1 && !hasNodeTypeSelected) ||
                (currentStep === 2 && !hasNodeLabelFilled)
              "
              @click="handleNextStep"
            />
            <Button
              v-if="currentStep === steps.setupNode"
              label="Criar nó"
              class="ml-auto"
              size="small"
              icon="pi pi-check"
              :disabled="!hasNodeLabelFilled"
              @click="handleCreateNode"
            />
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.stepper {
  background: var(--p-dialog-background);
}
</style>
