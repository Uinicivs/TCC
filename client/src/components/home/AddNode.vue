<script setup lang="ts">
import { computed, ref, type Component } from 'vue'
import { storeToRefs } from 'pinia'
import { Button, Dialog, Card, Stepper, StepList, Step, InputText, Textarea } from 'primevue'
import type { Node } from '@vue-flow/core'

import { useFlowStore } from '@/stores/flow'

import ConditionalNodeConfig from '@/components/home/ConditionalNodeConfig.vue'

interface IMappedNodes {
  name: string
  type: string
  icon: string
  iconColor: string
  configComponent?: Component
}

interface INodeData {
  label: string
  description: string
  config?: Record<string, any>
}

const flowStore = useFlowStore()
const { nodes } = storeToRefs(flowStore)

const steps = {
  chooseNode: 1,
  setupLabel: 2,
  setupNode: 3,
}

const visible = ref(false)
const currentStep = ref(steps.chooseNode)
const selectedNode = ref<IMappedNodes | null>(null)
const nodeData = ref<INodeData>({
  label: '',
  description: '',
})

const toggleCreateNodeDialog = () => {
  visible.value = !visible.value
  if (visible.value) {
    currentStep.value = 1
    selectedNode.value = null
    nodeData.value = { label: '', description: '' }
  }
}

const handleNodeSelect = (node: IMappedNodes) => {
  selectedNode.value = node
  currentStep.value = steps.setupLabel
}

const handleNextStep = () => {
  if (currentStep.value >= steps.setupNode) return

  if (
    currentStep.value === steps.setupLabel &&
    selectedNode.value &&
    !selectedNode.value.configComponent
  ) {
    handleCreateNode()
    return
  }

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

  if (stepNumber === steps.setupLabel && !hasNodeTypeSelected.value) return
  if (stepNumber === steps.setupNode && (!hasNodeTypeSelected.value || !hasNodeLabelFilled.value))
    return

  currentStep.value = stepNumber
}

const handleCreateNode = () => {
  if (!selectedNode.value || !nodeData.value.label.trim()) return

  const formatNode: Node = {
    id: Date.now().toString(),
    position: { x: window.innerWidth / 2 - 150, y: 200 },
    type: selectedNode.value.type,
    data: {
      label: nodeData.value.label,
      description: nodeData.value.description,
      ...(nodeData.value.config && { config: nodeData.value.config }),
    },
  }

  flowStore.addNodes(formatNode)
  toggleCreateNodeDialog()
}

const handleConfigData = (configData: Record<string, any>) => {
  nodeData.value.config = configData
}

const hasNodeTypeSelected = computed(() => selectedNode.value !== null)
const hasNodeLabelFilled = computed(() => nodeData.value.label.trim().length > 0)
const shouldShowConfigStep = computed(() => !!selectedNode.value?.configComponent)
const getDialogHeader = computed<string>(() => {
  switch (currentStep.value) {
    case steps.chooseNode:
      return 'Escolha o tipo do nó'
    case steps.setupLabel:
      return `Configurar ${selectedNode.value?.name}`
    case steps.setupNode:
      return `Configurar ${selectedNode.value?.name}`
    default:
      return ''
  }
})

const mappedNodes = computed<Array<IMappedNodes>>(() => {
  const nodes: Record<string, IMappedNodes> = {
    trigger: {
      name: 'Trigger',
      type: 'trigger',
      icon: 'pi-bolt',
      iconColor: 'text-emerald-500',
    },
    conditional: {
      name: 'Conditional',
      type: 'conditional',
      icon: 'pi-question-circle',
      iconColor: 'text-amber-500',
      configComponent: ConditionalNodeConfig,
    },
  }

  return Object.values(nodes)
})
</script>

<template>
  <Button
    v-if="!nodes.length"
    class="mx-auto text-4xl z-10 absolute top-20 left-1/2"
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
  >
    <div class="mb-6">
      <Stepper :value="currentStep" class="w-full">
        <StepList>
          <Step
            :value="steps.chooseNode"
            :class="{ 'cursor-pointer': true }"
            @click="handleStepClick(steps.chooseNode)"
          >
            <span class="hidden sm:inline">Selecionar tipo</span>
            <span class="sm:hidden">Tipo</span>
          </Step>
          <Step
            :value="steps.setupLabel"
            :disabled="!hasNodeTypeSelected"
            :class="{ 'cursor-pointer': hasNodeTypeSelected }"
            @click="hasNodeTypeSelected ? handleStepClick(steps.setupLabel) : null"
          >
            <span class="hidden sm:inline">Configurar nó</span>
            <span class="sm:hidden">Config</span>
          </Step>
          <transition name="fade">
            <Step
              v-show="shouldShowConfigStep"
              :value="steps.setupNode"
              :disabled="!hasNodeTypeSelected || !hasNodeLabelFilled"
              :class="{ 'cursor-pointer': hasNodeTypeSelected && hasNodeLabelFilled }"
              @click="
                hasNodeTypeSelected && hasNodeLabelFilled ? handleStepClick(steps.setupNode) : null
              "
            >
              <span class="hidden sm:inline">Configurar</span>
              <span class="sm:hidden">Config</span>
            </Step>
          </transition>
        </StepList>
      </Stepper>
    </div>

    <div v-if="currentStep === steps.chooseNode" class="space-y-6">
      <div class="grid auto-rows-auto grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
        <Card
          v-for="node in mappedNodes"
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

    <div v-if="currentStep === steps.setupLabel" class="space-y-6">
      <div class="space-y-4">
        <div class="space-y-2">
          <label for="nodeLabel" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
            Label do nó *
          </label>

          <InputText
            id="nodeLabel"
            v-model="nodeData.label"
            placeholder="Digite um nome para o nó"
            class="w-full"
            :class="{ 'p-invalid': !nodeData.label.trim() && currentStep >= steps.setupNode }"
          />
          <small class="text-gray-500 dark:text-gray-400"> Este será o nome exibido no nó </small>
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
          <small class="text-gray-500 dark:text-gray-400">
            Descrição opcional para documentar o propósito do nó
          </small>
        </div>
      </div>
    </div>

    <div v-if="currentStep === steps.setupNode && shouldShowConfigStep" class="space-y-6">
      <component
        :is="selectedNode.configComponent"
        v-if="!!selectedNode?.configComponent"
        @updated:config="handleConfigData"
        class="w-full"
      />
    </div>

    <div
      class="flex justify-between items-center mt-8 pt-4 border-t border-gray-200 dark:border-gray-700"
    >
      <Button
        v-if="currentStep > steps.chooseNode"
        label="Anterior"
        class="self-start"
        icon="pi pi-chevron-left"
        severity="secondary"
        outlined
        @click="handlePreviousStep"
      />

      <div class="flex gap-2">
        <Button
          v-if="currentStep < steps.setupNode"
          :label="!shouldShowConfigStep ? 'Criar nó' : 'Próximo'"
          class="self-end"
          icon="pi pi-chevron-right"
          icon-pos="right"
          :disabled="
            (currentStep === 1 && !hasNodeTypeSelected) ||
            (currentStep === 2 && !hasNodeLabelFilled)
          "
          @click="handleNextStep"
        />

        <Button
          v-if="currentStep === steps.setupNode"
          label="Criar nó"
          class="self-end"
          icon="pi pi-check"
          :disabled="!hasNodeLabelFilled"
          @click="handleCreateNode"
        />
      </div>
    </div>
  </Dialog>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease-in-out;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
