<script setup lang="ts">
import { ref, reactive, computed, inject, onMounted, type Ref } from 'vue'
import { Button, Stepper, StepList, Step, Message } from 'primevue'
import type { DynamicDialogInstance } from 'primevue/dynamicdialogoptions'

import NodeConfigForm from '@/components/flows/show/NodeConfigForm.vue'
import NodeSummary from '@/components/flows/show/NodeSummary.vue'

import type { INode, IMappedNodes } from '@/interfaces/node'

import { useFlowStore } from '@/stores/flow'

import { nodes } from '@/constants/nodes'
import type { Variable } from '@/interfaces/variables'

const dialogRef = inject<Ref<DynamicDialogInstance>>('dialogRef')
const nodeId = ref('')

const { getStartNodeVariables, getNodeById, updateNode } = useFlowStore()

const steps = {
  setupTitle: 1,
  setupNode: 2,
}

const currentStep = ref<number>(steps.setupTitle)
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
  return currentStep.value === 1 && !hasNodeLabelFilled
})

const getDisabledMessage = computed(() => {
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

const reset = () => {
  currentStep.value = steps.setupTitle

  const currentNode = getNodeById(nodeId.value)

  if (currentNode) {
    const node = currentNode
    const nodeType = node.type as keyof typeof nodes

    selectedNode.value = nodes[nodeType]

    Object.assign(nodeData, {
      title: node.data.title || '',
      description: node.data.description || '',
      settings: node.data.settings || {},
      parent: node.data.parent || null,
      children: node.data.children || [],
    })
  }
}

const handleStepNavigation = {
  next: () => {
    if (currentStep.value >= steps.setupNode) return
    currentStep.value++
  },
  previous: () => {
    if (currentStep.value <= steps.setupTitle) return
    currentStep.value--
  },
  goTo: (stepNumber: number) => {
    if (stepNumber === steps.setupTitle) {
      currentStep.value = steps.setupTitle
      return
    }

    if (stepNumber === steps.setupNode && !hasNodeLabelFilled.value) {
      return
    }

    currentStep.value = stepNumber
  },
}

const handleUpdateNode = () => {
  if (!selectedNode.value || !nodeData.title.trim()) return

  const formattedNodeData = JSON.parse(JSON.stringify(nodeData))
  updateNode(nodeId.value, { data: formattedNodeData })
  dialogRef?.value?.close()
}

const hasNodeLabelFilled = computed(() => nodeData.title?.trim().length > 0)
onMounted(() => {
  nodeId.value = dialogRef?.value?.data?.nodeId || ''

  if (nodeId.value) {
    reset()
  }
})
</script>

<template>
  <div>
    <div class="mb-6 sticky top-0 z-10 pb-2 stepper">
      <Stepper :value="currentStep" class="w-full">
        <StepList>
          <Step
            :value="steps.setupTitle"
            class="cursor-pointer"
            @click="handleStepNavigation.goTo(steps.setupTitle)"
          >
            <span class="hidden sm:inline">Configurar nó</span>
          </Step>
          <Step
            :value="steps.setupNode"
            :disabled="!hasNodeLabelFilled"
            :class="{ 'cursor-pointer': hasNodeLabelFilled }"
            @click="hasNodeLabelFilled ? handleStepNavigation.goTo(steps.setupNode) : null"
          >
            <span class="hidden sm:inline">Revisar</span>
          </Step>
        </StepList>
      </Stepper>
    </div>

    <NodeConfigForm
      v-if="currentStep === steps.setupTitle"
      v-model:nodeData="nodeData"
      :selected-node="selectedNode"
    />

    <NodeSummary
      v-if="currentStep === steps.setupNode"
      :node-data="nodeData"
      :selected-node="selectedNode"
    />

    <div class="flex flex-col gap-5 w-full">
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
          v-if="currentStep > steps.setupTitle"
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
            v-if="currentStep < steps.setupNode"
            class="ml-auto"
            icon="pi pi-chevron-right"
            size="small"
            icon-pos="right"
            label="Próximo"
            :disabled="shouldDisableNextButton"
            @click="handleStepNavigation.next"
          />
          <Button
            v-if="currentStep === steps.setupNode"
            label="Atualizar nó"
            class="ml-auto"
            size="small"
            icon="pi pi-check"
            :disabled="!hasNodeLabelFilled"
            @click="handleUpdateNode"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stepper {
  background: var(--p-dialog-background);
}
</style>
