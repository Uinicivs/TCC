<script setup lang="ts">
import { ref, useTemplateRef, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { DataTable, Column, Button, Popover } from 'primevue'
import { useToast } from 'primevue/usetoast'

import type { IFlow } from '@/interfaces/flow'

import CreateFlowModal from '@/components/home/CreateFlowModal.vue'

import { createFlow, getFlows, type TCreateFlowPayload } from '@/services/flowService'

const router = useRouter()
const popoverRef = useTemplateRef('flow-options')

const flows = ref<IFlow[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)

const toast = useToast()

onMounted(async () => {
  await loadFlows()
})

const loadFlows = async () => {
  loading.value = true
  try {
    flows.value = await getFlows()
  } catch (error) {
    toast.add({
      severity: 'error',
      detail: error instanceof Error && error.message,
      life: 3000,
      closable: false,
    })
  } finally {
    loading.value = false
  }
}

const viewFlow = (flowId: string) => {
  router.push(`/show/${flowId}`)
}

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date)
}

const toggleOptions = (event: MouseEvent) => {
  popoverRef.value?.toggle(event)
}

const createNewFlow = () => {
  showCreateDialog.value = true
}

const handleCreateFlow = async (payload: TCreateFlowPayload) => {
  loading.value = true
  try {
    const createdFlow = await createFlow(payload)
    flows.value.unshift(createdFlow)

    toast.add({
      severity: 'success',
      detail: 'Fluxo criado com sucesso!',
      life: 3000,
      closable: false,
    })
  } catch (error) {
    toast.add({
      severity: 'error',
      detail: error instanceof Error && error.message,
      life: 3000,
      closable: false,
    })
  } finally {
    loading.value = false
    showCreateDialog.value = false
  }
}
</script>

<template>
  <div class="mx-auto h-full flex flex-col items-center lg:max-w-[1280px] pt-[100px] gap-8">
    <div class="grid grid-cols-2 gap-4 w-full items-center">
      <div class="col-span-1 flex flex-col gap-1">
        <h2 class="font-semibold text-2xl text-neutral-800">Meus Fluxos</h2>
        <p class="font-light text-neutral-500">
          Aqui você pode visualizar, editar ou remover qualquer fluxo rapidamente.
        </p>
      </div>

      <div class="col-start-2 col-span-1 justify-self-end">
        <Button label="Cria novo fluxo" size="small" @click="createNewFlow" />
      </div>
    </div>
    <div class="flex flex-col items-center gap-4 h-full">
      <DataTable
        :value="flows"
        :loading
        paginator
        :rows="12"
        paginator-position="bottom"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        currentPageReportTemplate="Mostrando {last} de {totalRecords}"
        responsiveLayout="scroll"
        class="rounded-lg w-7xl h-full flex flex-col"
        size="small"
      >
        <Column field="name" header="Nome" class="min-w-[200px]">
          <template #body="{ data }">
            {{ data.flowName }}
          </template>
        </Column>
        <Column
          field="description"
          header="Descrição"
          class="lg:max-w-[500px] md:max-w-200px truncate"
        >
          <template #body="{ data }">
            {{ data.flowDescription ? data.flowDescription : '-' }}
          </template>
        </Column>
        <Column field="updatedAt" header="Última Atualização" class="min-w-[150px]">
          <template #body="{ data }">
            {{ formatDate(data.updatedAt) }}
          </template>
        </Column>

        <Column class="w-[50px]">
          <template #body="{ data }">
            <Button
              icon="pi pi-ellipsis-h"
              variant="text"
              severity="secondary"
              rounded
              @click="toggleOptions"
            />

            <Popover ref="flow-options">
              <div class="flex flex-col gap-2 min-w-[160px]">
                <Button
                  severity="secondary"
                  variant="text"
                  label="Ver"
                  size="small"
                  @click="viewFlow(data.flowId)"
                />
                <Button
                  variant="text"
                  severity="secondary"
                  label="Editar"
                  size="small"
                  @click="viewFlow(data.flowId)"
                />
                <Button
                  icon="pi pi-trash"
                  severity="danger"
                  variant="text"
                  label="Excluir"
                  size="small"
                  @click="viewFlow(data.flowId)"
                />
              </div>
            </Popover>
          </template>
        </Column>

        <template #empty>
          <div v-if="!loading" class="font-light text-neutral-500 text-center h-full">
            Você ainda não possui nenhum fluxo.
          </div>
        </template>
      </DataTable>
    </div>

    <CreateFlowModal
      v-model:visible="showCreateDialog"
      @create="handleCreateFlow"
      @loading="(value) => (loading = value)"
    />
  </div>
</template>

<style scoped>
:deep(.p-datatable-table-container) {
  flex: 1;
}

:deep(.p-datatable-empty-message td) {
  border: none;
}

:deep(.p-overlay-mask) {
  background: none;
}
</style>
