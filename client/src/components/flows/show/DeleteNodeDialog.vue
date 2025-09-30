<template>
  <Card class="w-full max-w-md !shadow-none">
    <template #header>
      <div class="flex flex-col gap-1">
        <p class="text-sm">
          Tem certeza que deseja deletar este fluxo? Esta ação não pode ser desfeita.
        </p>
      </div>
    </template>

    <template #content>
      <Message severity="error">
        <div class="flex items-center gap-2">
          <i class="pi pi-info-circle" />
          <span class="text-sm font-medium">
            Atenção: Todos os nós e configurações serão perdidos permanentemente.
          </span>
        </div>
      </Message>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          label="Cancelar"
          severity="secondary"
          variant="outlined"
          size="small"
          @click="handleCancel"
        />

        <Button label="Deletar Fluxo" severity="danger" size="small" @click="handleConfirm" />
      </div>
    </template>
  </Card>
</template>

<script setup lang="ts">
import { Card, Button, Message } from 'primevue'
import type { DynamicDialogInstance } from 'primevue/dynamicdialogoptions'
import { inject, type Ref } from 'vue'

interface Emits {
  (event: 'cancel'): void
  (event: 'confirm'): void
}

const dialogRef = inject<Ref<DynamicDialogInstance>>('dialogRef') as
  | Ref<DynamicDialogInstance>
  | undefined

const emit = defineEmits<Emits>()

const handleCancel = () => {
  emit('cancel')
  dialogRef?.value?.close()
}

const handleConfirm = () => {
  emit('confirm')
  dialogRef?.value?.close()
}
</script>

<style scoped>
:deep(.p-card-header) {
  padding: 0;
}

:deep(.p-card-body) {
  padding: 0;
}

:deep(.p-card-content) {
  margin-top: 1.5rem;
}

:deep(.p-card-footer) {
  margin-top: 1.5rem;
}
</style>
