<script setup lang="ts">
import { computed } from 'vue'
import { Button, Dialog, Stepper, StepList, Step } from 'primevue'

import type { INode } from '@/interfaces/node.ts'

import NodeTypeSelector from '@/components/flows/show/NodeTypeSelector.vue'
import NodeConfigForm from '@/components/flows/show/NodeConfigForm.vue'
import NodeSummary from '@/components/flows/show/NodeSummary.vue'

import { useNodeCreation } from '@/composable/useNodeCreation.ts'

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
</script>

<template>
  <div>
    <div class="flex flex-col items-center gap-2 cursor-pointer" @click="toggleCreateNodeDialog">
      <Button class="text-4xl" icon="pi pi-plus" severity="secondary" size="small" rounded />

      <span>
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
            <Step
              :value="steps.setupNode"
              :disabled="!hasNodeTypeSelected || !hasNodeLabelFilled"
              :class="{ 'cursor-pointer': hasNodeTypeSelected && hasNodeLabelFilled }"
              @click="
                hasNodeTypeSelected && hasNodeLabelFilled
                  ? handleStepNavigation.goTo(steps.setupNode)
                  : null
              "
            >
              <span class="hidden sm:inline">Revisar</span>
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

      <NodeSummary
        v-if="currentStep === steps.setupNode"
        :node-data="nodeData"
        :selected-node="selectedNode"
      />

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
              :disabled="
                (currentStep === 1 && !hasNodeTypeSelected) ||
                (currentStep === 2 && !hasNodeLabelFilled)
              "
              @click="handleStepNavigation.next"
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
