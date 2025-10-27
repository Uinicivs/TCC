<template>
  <Dialog
    :visible="visible"
    :draggable="false"
    :style="{ width: '24rem' }"
    :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    header="Testar Fluxo"
    closable
    modal
    dismissableMask
    @update:visible="visible = false"
  >
    <div class="flex flex-col h-full justify-center">
      <div v-if="isLoading" class="flex flex-col items-center justify-center">
        <ProgressSpinner />
        <span class="mt-4">Testando fluxo...</span>
      </div>
      <div v-else>
        <p class="mb-4">Você está prestes a testar a fluxo. Deseja continuar?</p>
        <div class="flex justify-end gap-2 mt-8">
          <Button label="Cancelar" @click="visible = false" size="small" severity="secondary" />
          <Button label="Testar" @click="testFlowAction" size="small" severity="primary" />
        </div>
      </div>
    </div>
  </Dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { Dialog, Button, ProgressSpinner } from 'primevue'

import { testFlow } from '@/services/flowService'

const { params } = useRoute()

const visible = defineModel<boolean>('visible', {
  type: Boolean,
  required: true,
  default: false,
})

const emit = defineEmits(['tested'])

const isLoading = ref(false)

const testFlowAction = async () => {
  isLoading.value = true
  try {
    await testFlow(params.id as string)
    emit('tested')
  } finally {
    isLoading.value = false
    visible.value = false
  }
}
</script>
