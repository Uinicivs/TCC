<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { Button, Dialog } from 'primevue'

import { useFlowStore } from '@/stores/flow'

const { nodes } = storeToRefs(useFlowStore())

const visible = ref(false)
const toggleCreateNodeDialog = () => {
  visible.value = !visible.value
}
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
    header="Criar nó"
    :style="{ width: '50rem' }"
    :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
  >
    card
  </Dialog>
</template>
