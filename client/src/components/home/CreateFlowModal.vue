<script setup lang="ts">
import { ref, watch } from 'vue'
import { Dialog, InputText, Textarea, Button } from 'primevue'

import type { TCreateFlowPayload } from '@/services/flowService'

interface Props {
  visible: boolean
}

interface Emits {
  (event: 'update:visible', value: boolean): void
  (event: 'create', payload: TCreateFlowPayload): void
  (event: 'loading', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const loading = ref(false)
const newFlow = ref<TCreateFlowPayload>({
  flowName: '',
  flowDescription: '',
})

watch(
  () => props.visible,
  (newValue) => {
    if (!newValue) {
      resetForm()
    }
  },
)

const resetForm = () => {
  newFlow.value = {
    flowName: '',
    flowDescription: '',
  }
}

const handleCreateFlow = async () => {
  if (!newFlow.value.flowName.trim()) {
    return
  }

  loading.value = true
  emit('loading', true)
  emit('create', { ...newFlow.value })
}

const cancelCreateFlow = () => {
  resetForm()
  emit('update:visible', false)
}

const closeModal = () => {
  emit('update:visible', false)
}
</script>

<template>
  <Dialog
    :visible
    :draggable="false"
    :closable="false"
    :style="{ width: '40rem' }"
    modal
    header="Criar Novo Fluxo"
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
          placeholder="Digite o nome do fluxo"
          :disabled="loading"
          autofocus
          required
          class="w-full"
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
          class="w-full"
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
          @click="cancelCreateFlow"
        />

        <Button label="Criar Fluxo" size="small" :loading @click="handleCreateFlow" />
      </div>
    </template>
  </Dialog>
</template>
