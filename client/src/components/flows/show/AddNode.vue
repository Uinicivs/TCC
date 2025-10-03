<script setup lang="ts">
import { computed } from 'vue'
import { Button, Dialog, Stepper, StepList, Step, Message } from 'primevue'

import type { INode } from '@/interfaces/node'
import type { Variable } from '@/interfaces/variables'

import NodeTypeSelector from '@/components/flows/show/NodeTypeSelector.vue'
import NodeConfigForm from '@/components/flows/show/NodeConfigForm.vue'

import { useNodeCreation } from '@/composable/useNodeCreation'
import { useFlowStore } from '@/stores/flow'

const props = defineProps<{
  parentId: INode['parent']
  handleId?: string
}>()

const {
  availableNodeTypes,
  steps,
  visible,
  currentStep,
  selectedNode,
  nodeData,
  hasNodeTypeSelected,
  hasNodeLabelFilled,
  shouldShowConfigStep,
  getDialogHeader,
  toggleCreateNodeDialog,
  handleNodeSelect,
  handleStepNavigation,
  handleCreateNode,
} = useNodeCreation(props.parentId, props.handleId)
const { getStartNodeVariables } = useFlowStore()

const getCreateNodeButtonLabel = computed(() => {
  const handleId = props.handleId || ''
  if (handleId.includes('right')) {
    return 'Verdadeiro'
  }

  if (handleId.includes('left')) {
    return 'Falso'
  }

  return ''
})

const shouldDisableNextButton = computed(() => {
  if (selectedNode.value?.type === 'start') {
    const inputs = (nodeData.settings as Record<string, unknown>)?.inputs as Array<Variable>
    return !inputs?.length || !inputs?.every(({ displayName }: Variable) => Boolean(displayName))
  }

  if (selectedNode.value?.type === 'conditional') {
    const expression = nodeData.settings as string

    if (!expression || !expression.trim()) return true
    if (!getStartNodeVariables.length) return false

    const requiredVariables = getStartNodeVariables.filter(({ required }: Variable) => required)

    if (requiredVariables.length > 0) {
      return !requiredVariables.every(({ displayName }: Variable) =>
        expression.includes(displayName),
      )
    }
  }
  return (
    (currentStep.value === 1 && !hasNodeTypeSelected) ||
    (currentStep.value === 2 && !hasNodeLabelFilled)
  )
})

const getDisabledMessage = computed(() => {
  if (currentStep.value === 1) return
  if (currentStep.value === 2 && !hasNodeLabelFilled) {
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
    const expression = nodeData.settings as string
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
})
</script>

<template>
  <div>
    <div class="flex flex-col items-center gap-2 cursor-pointer" @click="toggleCreateNodeDialog">
      <Button class="text-4xl" icon="pi pi-plus" severity="secondary" size="small" rounded />

      <span class="text-sm text-gray-500 dark:text-gray-400 select-none">
        {{ getCreateNodeButtonLabel }}
      </span>
    </div>

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
              class="cursor-pointer"
              @click="handleStepNavigation.goTo(steps.chooseNode)"
            >
              <span class="hidden sm:inline">Selecionar tipo</span>
            </Step>
            <Step
              :value="steps.setupTitle"
              :disabled="!hasNodeTypeSelected"
              :class="{ 'cursor-pointer': hasNodeTypeSelected }"
              @click="hasNodeTypeSelected ? handleStepNavigation.goTo(steps.setupTitle) : null"
            >
              <span class="hidden sm:inline">
                {{ shouldShowConfigStep ? 'Configurar nó' : 'Configurar nó' }}
              </span>
            </Step>
          </StepList>
        </Stepper>
      </div>

      <NodeTypeSelector
        v-if="currentStep === steps.chooseNode"
        :available-node-types="availableNodeTypes"
        @select="handleNodeSelect"
      />

      <NodeConfigForm
        v-if="currentStep === steps.setupTitle"
        v-model:nodeData="nodeData"
        :selected-node="selectedNode"
      />

      <template #footer>
        <div class="flex flex-col w-full gap-5">
          <transition
            enter-active-class="transition-all duration-300 ease-out"
            enter-from-class="opacity-0 transform -translate-y-2"
            enter-to-class="opacity-100 transform translate-y-0"
            leave-active-class="transition-all duration-200 ease-in"
            leave-from-class="opacity-100 transform translate-y-0"
            leave-to-class="opacity-0 transform -translate-y-2"
          >
            <Message
              v-if="shouldDisableNextButton && getDisabledMessage"
              severity="warn"
              :closable="false"
              size="small"
              class="mt-5"
            >
              <div class="flex gap-2 items-center">
                <i class="pi pi-exclamation-triangle text-amber-500" />
                <span>
                  {{ getDisabledMessage }}
                </span>
              </div>
            </Message>
          </transition>
          <div class="flex justify-between items-center w-full">
            <Button
              v-if="currentStep > steps.chooseNode"
              label="Anterior"
              class="self-start"
              size="small"
              icon="pi pi-chevron-left"
              severity="secondary"
              outlined
              @click="handleStepNavigation.previous"
            />
            <div class="flex gap-2 w-full">
              <Button
                v-if="currentStep < steps.setupTitle"
                class="ml-auto"
                icon="pi pi-chevron-right"
                size="small"
                icon-pos="right"
                label="Próximo"
                :disabled="shouldDisableNextButton"
                @click="handleStepNavigation.next"
              />
              <Button
                v-if="currentStep === steps.setupTitle"
                label="Criar nó"
                class="ml-auto"
                size="small"
                icon="pi pi-check"
                :disabled="shouldDisableNextButton"
                @click="handleCreateNode"
              />
            </div>
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
