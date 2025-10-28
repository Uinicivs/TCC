<script setup lang="ts">
import { ref, watch } from 'vue'
import { Dialog, InputText, Textarea, Button } from 'primevue'

import type { TCreateFlowPayload } from '@/services/flowService'

import type { IFlow } from '@/interfaces/flow'

interface Props {
  visible: boolean
  flow?: IFlow | null
  mode?: 'create' | 'edit'
}

interface Emits {
  (event: 'update:visible', value: boolean): void
  (event: 'create', payload: TCreateFlowPayload): void
  (event: 'update', id: string, payload: Partial<TCreateFlowPayload>): void
  (event: 'loading', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const loading = ref(false)
const newFlow = ref<TCreateFlowPayload>({
  flowName: '',
  flowDescription: '',
})

const resetForm = () => {
  newFlow.value = {
    flowName: '',
    flowDescription: '',
  }
  loading.value = false
  emit('loading', false)
}

const handleAction = async () => {
  if (!newFlow.value.flowName.trim()) {
    return
  }

  loading.value = true
  emit('loading', true)

  if (props.mode === 'edit' && props.flow) {
    const changedFields: Partial<TCreateFlowPayload> = {}

    if (newFlow.value.flowName !== props.flow.flowName) {
      changedFields.flowName = newFlow.value.flowName
    }

    if (newFlow.value.flowDescription !== props.flow.flowDescription) {
      changedFields.flowDescription = newFlow.value.flowDescription
    }

    if (Object.keys(changedFields).length > 0) {
      emit('update', props.flow.flowId, changedFields)
      return
    }

    cancelAction()
    return
  }

  emit('create', { ...newFlow.value })
}

const cancelAction = () => {
  resetForm()
  emit('update:visible', false)
}

const closeModal = () => {
  emit('update:visible', false)
}

watch(
  () => props.visible,
  (newValue) => {
    if (newValue && props.mode === 'edit') {
      newFlow.value = {
        flowName: props.flow?.flowName || '',
        flowDescription: props.flow?.flowDescription || '',
      }
    }

    if (!newValue) {
      resetForm()
    }
  },
  { immediate: true },
)
</script>

<template>
  <Dialog
    :visible
    :draggable="false"
    :closable="false"
    :style="{ width: '40rem' }"
    modal
    :header="props.mode === 'edit' ? 'Editar Fluxo' : 'Criar Novo Fluxo'"
    @update:visible="closeModal"
  >
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <label for="flowName" class="font-medium text-neutral-700">
          Nome do Fluxo <span class="text-red-700">*</span>
        </label>
        <InputText
          id="flowName"
          v-model="newFlow.flowName"
          :disabled="loading"
          autofocus
          required
          size="small"
          placeholder="Digite o nome do fluxo"
          class="w-full !bg-transparent"
        />
      </div>

      <div class="flex flex-col gap-2">
        <label for="flowDescription" class="font-medium text-neutral-700">
          Descrição (opcional)
        </label>
        <Textarea
          id="flowDescription"
          v-model="newFlow.flowDescription"
          placeholder="Digite uma descrição para o fluxo"
          :disabled="loading"
          :rows="3"
          class="w-full !bg-transparent"
        />
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          label="Cancelar"
          severity="secondary"
          variant="outlined"
          size="small"
          :disabled="loading"
          @click="cancelAction"
        />

        <Button
          :label="props.mode === 'edit' ? 'Salvar Alterações' : 'Criar Fluxo'"
          size="small"
          :loading
          @click="handleAction"
        />
      </div>
    </template>
  </Dialog>
</template>
