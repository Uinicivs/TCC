<script setup lang="ts">
import { Button, Stepper, StepList, Step, DynamicDialog } from 'primevue'
import { ref, reactive, computed, inject, onMounted } from 'vue'

import NodeConfigForm from '@/components/flows/show/NodeConfigForm.vue'
import NodeSummary from '@/components/flows/show/NodeSummary.vue'

import type { INode, IMappedNodes } from '@/interfaces/node.ts'
import { useFlowStore } from '@/stores/flow.ts'
import { nodes } from '@/constants/nodes.ts'

const dialogRef = inject<typeof DynamicDialog>('dialogRef')
const nodeId = ref('')

const flowStore = useFlowStore()

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

const reset = () => {
  currentStep.value = steps.setupTitle

  const currentNode = flowStore.getNodeById(nodeId.value)

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
  flowStore.updateNode(nodeId.value, { data: formattedNodeData })
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

    <div class="flex justify-between items-center w-full pt-5">
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
          :disabled="!hasNodeLabelFilled"
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
</template>

<style scoped>
.stepper {
  background: var(--p-dialog-background);
}
</style>
