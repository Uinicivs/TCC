<script setup lang="ts">
import { ref, useTemplateRef, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { DataTable, Column, Button, Popover, Card, SelectButton } from 'primevue'
import { useToast } from 'primevue/usetoast'

import type { IFlow } from '@/interfaces/flow'

import FlowFormModal from '@/components/home/FlowFormModal.vue'

import {
  createFlow,
  getFlows,
  deleteFlow,
  updateFlow,
  type TCreateFlowPayload,
} from '@/services/flowService'

const router = useRouter()
const popoverRef = useTemplateRef('flow-options')
const toast = useToast()

const flows = ref<IFlow[]>([])
const loading = ref(false)
const showFlowFormModal = ref(false)
const selectedFlow = ref<IFlow | null>(null)
const modalMode = ref<'create' | 'edit'>('create')
const activeMode = ref<'Tabela' | 'Cards'>('Tabela')
const modeOptions = ['Tabela', 'Cards']

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

const viewFlow = () => {
  router.push(`/show/${selectedFlow.value?.flowId}`)
}

const formatDate = (date: Date) => {
  return new Intl.DateTimeFormat('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  }).format(date)
}

const toggleOptions = (event: MouseEvent, flow: IFlow) => {
  selectedFlow.value = flow
  popoverRef.value?.toggle(event)
}

const createNewFlow = () => {
  selectedFlow.value = null
  modalMode.value = 'create'
  showFlowFormModal.value = true
}

const editFlow = () => {
  modalMode.value = 'edit'
  showFlowFormModal.value = true
  popoverRef.value?.hide()
}

const handleCreateFlow = async (payload: TCreateFlowPayload) => {
  let createdFlow
  loading.value = true
  try {
    createdFlow = await createFlow(payload)
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
    showFlowFormModal.value = false

    if (createdFlow) {
      router.push({ name: 'flow-show', params: { id: createdFlow.flowId } })
    }
  }
}

const handleUpdateFlow = async (flowId: string, payload: Partial<TCreateFlowPayload>) => {
  loading.value = true
  try {
    await updateFlow(flowId, payload)
    const index = flows.value.findIndex((flow) => flow.flowId === flowId)

    if (index !== -1) {
      flows.value[index] = {
        ...flows.value[index],
        ...payload,
      }
    }

    toast.add({
      severity: 'success',
      detail: 'Fluxo atualizado com sucesso!',
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
    showFlowFormModal.value = false
    selectedFlow.value = null
  }
}

const handleDeleteFlow = async () => {
  loading.value = true
  try {
    if (!selectedFlow.value?.flowId) return
    await deleteFlow(selectedFlow.value?.flowId)
    flows.value = flows.value.filter((flow) => flow.flowId !== selectedFlow.value?.flowId)

    toast.add({
      severity: 'success',
      detail: 'Fluxo excluído com sucesso!',
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
  }
}

watch(
  () => showFlowFormModal.value,
  (newValue) => {
    if (!newValue) {
      selectedFlow.value = null
    }
  },
)
</script>

<template>
  <div class="mx-auto h-full w-full flex flex-col items-center lg:max-w-[1280px] pt-[100px] gap-8">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 w-full items-center">
      <div class="flex flex-col gap-1 text-center md:text-left">
        <h2 class="font-medium text-xl text-neutral-800 dark:text-white">Meus Fluxos</h2>
        <p class="font-light text-sm text-neutral-500 dark:text-white">
          Aqui você pode visualizar, editar ou remover qualquer fluxo rapidamente.
        </p>
      </div>

      <div class="justify-self-center lg:justify-self-end flex gap-4">
        <Button label="Cria novo fluxo" size="small" @click="createNewFlow" />
        <SelectButton
          v-model="activeMode"
          :options="modeOptions"
          class="!hidden md:block lg:!block"
        />
      </div>
    </div>
    <div class="flex flex-col items-center gap-4 h-full w-full justify-self-start">
      <transition name="fade" mode="out-in">
        <div
          v-if="activeMode === 'Cards'"
          class="flex flex-col items-center gap-4 h-full w-full justify-self-start bg-neutral-50 dark:bg-neutral-950 p-4 rounded-lg mb-8"
        >
          <div v-if="loading" class="flex justify-center items-center h-full">
            <i class="pi pi-spinner pi-spin !text-3xl text-neutral-200" />
          </div>

          <div
            v-else-if="flows.length"
            class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 w-full"
          >
            <Card v-for="flow in flows" :key="flow.flowId" class="w-full">
              <template #title>
                <div class="flex justify-between items-start">
                  <h3 class="text-lg truncate pr-2">
                    {{ flow.flowName }}
                  </h3>

                  <Button
                    icon="pi pi-ellipsis-h"
                    variant="text"
                    severity="secondary"
                    rounded
                    size="small"
                    :disabled="loading"
                    class="justify-self-start"
                    @click="toggleOptions($event, flow)"
                  />
                </div>
              </template>
              <template #content>
                <div class="space-y-3 w-full flex flex-col">
                  <p class="text-sm break-words h-20 overflow-y-scroll">
                    {{ flow.flowDescription || '-' }}
                  </p>
                  <div class="text-xs text-neutral-500 dark:text-neutral-400">
                    Última atualização: {{ formatDate(flow.updatedAt) }}
                  </div>
                </div>
              </template>
            </Card>

            <Popover ref="flow-options">
              <div class="flex flex-col gap-2 min-w-[160px]">
                <Button
                  severity="secondary"
                  variant="text"
                  label="Ver"
                  size="small"
                  :disabled="loading"
                  @click="viewFlow"
                />

                <Button
                  variant="text"
                  severity="secondary"
                  label="Editar"
                  size="small"
                  :disabled="loading"
                  @click="editFlow"
                />

                <Button
                  severity="danger"
                  variant="text"
                  label="Excluir"
                  size="small"
                  :loading
                  @click="handleDeleteFlow"
                />
              </div>
            </Popover>
          </div>

          <div
            v-else-if="!flows.length"
            class="font-light text-neutral-500 mt-11 text-center flex items-center"
          >
            Você ainda não possui nenhum fluxo.
          </div>
        </div>

        <DataTable
          v-else
          :value="flows"
          :loading
          paginator
          :rows="12"
          paginator-position="bottom"
          paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
          currentPageReportTemplate="Mostrando {last} de {totalRecords}"
          responsiveLayout="scroll"
          class="rounded-lg w-7xl h-full flex flex-col dark:bg-transparent"
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
              {{ data.flowDescription || '-' }}
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
                :disabled="loading"
                @click="toggleOptions($event, data)"
              />

              <Popover ref="flow-options">
                <div class="flex flex-col gap-2 min-w-[160px]">
                  <Button
                    severity="secondary"
                    variant="text"
                    label="Ver"
                    size="small"
                    :disabled="loading"
                    @click="viewFlow"
                  />

                  <Button
                    variant="text"
                    severity="secondary"
                    label="Editar"
                    size="small"
                    :disabled="loading"
                    @click="editFlow"
                  />

                  <Button
                    severity="danger"
                    variant="text"
                    label="Excluir"
                    size="small"
                    :loading
                    @click="handleDeleteFlow"
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
      </transition>
    </div>

    <FlowFormModal
      v-model:visible="showFlowFormModal"
      :mode="modalMode"
      :flow="selectedFlow"
      @create="handleCreateFlow"
      @update="handleUpdateFlow"
      @loading="(value) => (loading = value)"
    />
  </div>
</template>

<style scoped>
:deep(.p-datatable-table-container) {
  flex: 1;
}

:deep(.p-datatable-empty-message td),
:deep(.p-datatable-paginator-bottom) {
  border: none;
}

:deep(.p-overlay-mask),
:deep(.p-datatable-header-cell),
:deep(.p-datatable-tbody > tr),
:deep(.p-paginator) {
  background: transparent;
}

.loading {
  display: inline-block;
  width: 2rem;
  height: 2rem;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
