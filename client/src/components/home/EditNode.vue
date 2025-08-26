<script setup lang="ts">
import { Button, Dialog, Stepper, StepList, Step } from 'primevue'

import type { INode } from '@/interfaces/node'

import NodeConfigForm from '@/components/home/NodeConfigForm.vue'
import NodeSummary from '@/components/home/NodeSummary.vue'

import { useNodeEditing } from '@/composable/useNodeEditing'

const props = defineProps<{ nodeId: string }>()

const {
  steps,
  visible,
  currentStep,
  selectedNode,
  nodeData,
  hasNodeLabelFilled,
  getDialogHeader,
  toggleEditNodeDialog,
  handleStepNavigation,
  handleUpdateNode,
  handleConfigData,
} = useNodeEditing(props.nodeId)
</script>

<template>
  <div>
    <Button
      class="text-sm"
      icon="pi pi-pencil"
      severity="secondary"
      size="small"
      rounded
      @click="toggleEditNodeDialog"
      title="Editar nó"
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
        @updated:settings="handleConfigData"
      />

      <NodeSummary
        v-if="currentStep === steps.setupNode"
        :node-data="nodeData"
        :selected-node="selectedNode"
      />

      <template #footer>
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
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.stepper {
  background: var(--p-dialog-background);
}
</style>
