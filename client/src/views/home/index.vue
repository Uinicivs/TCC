<script setup lang="ts">
import { ref, useTemplateRef, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { DataTable, Column, Button, ContextMenu, Card, SelectButton, Toolbar } from 'primevue'
import { useToast } from 'primevue/usetoast'

import type { IFlow } from '@/interfaces/flow'

import FlowFormModal from '@/components/home/FlowFormModal.vue'
import UserMenu from '@/components/shared/UserMenu.vue'
import ThemeToggle from '@/components/shared/ThemeToggle.vue'
import HelpButton from '@/components/shared/HelpButton.vue'

import {
  createFlow,
  getFlows,
  deleteFlow,
  updateFlow,
  type TCreateFlowPayload,
} from '@/services/flowService'

import { homeTutorial } from '@/constants/tutorials'

const router = useRouter()
const contextMenuRef = useTemplateRef('contextMenu')
const toast = useToast()

const flowLimit = Number(import.meta.env.VITE_DECISION_FLOW_LIMIT) || 10

const flows = ref<IFlow[]>([])
const loading = ref(false)
const showFlowFormModal = ref(false)
const selectedFlow = ref<IFlow | null>(null)
const modalMode = ref<'create' | 'edit'>('create')
const activeMode = ref<'Tabela' | 'Cards'>(
  (localStorage.getItem('flow-view-mode') as 'Tabela' | 'Cards') || 'Cards',
)
const modeOptions = ['Tabela', 'Cards']

onMounted(async () => {
  await loadFlows()
})

watch(activeMode, (newMode) => {
  localStorage.setItem('flow-view-mode', newMode)
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

const showContextMenu = (event: MouseEvent, flow: IFlow) => {
  event.preventDefault()
  selectedFlow.value = flow
  contextMenuRef.value?.show(event)
}

const createNewFlow = () => {
  selectedFlow.value = null
  modalMode.value = 'create'
  showFlowFormModal.value = true
}

const editFlow = () => {
  modalMode.value = 'edit'
  showFlowFormModal.value = true
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

const menuItems = computed(() => [
  {
    label: 'Ver',
    icon: 'pi pi-eye',
    command: viewFlow,
  },
  {
    label: 'Editar',
    icon: 'pi pi-pencil',
    command: editFlow,
  },
  {
    label: 'Excluir',
    icon: 'pi pi-trash',
    command: handleDeleteFlow,
  },
])

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
  <div class="h-screen">
    <Toolbar class="w-full z-10 fixed dark:!border-none !rounded-none">
      <template #start>
        <img src="@/assets/svg/logo.png" class="mx-auto" alt="Rulify Logo" width="32" height="32" />
        <span class="font-medium text-md">Rulify</span>
      </template>

      <template #end>
        <div class="flex gap-2">
          <HelpButton id="help-button" :steps="homeTutorial" />
          <ThemeToggle />
          <UserMenu />
        </div>
      </template>
    </Toolbar>

    <div
      class="mx-auto h-full w-full flex flex-col items-center lg:max-w-[1280px] pt-[100px] gap-8"
    >
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 w-full items-center">
        <div id="flow-list-header" class="flex flex-col gap-1 text-center md:text-left">
          <h2 class="font-medium text-xl text-neutral-800 dark:text-white">Meus Fluxos</h2>
          <p class="font-light text-sm text-neutral-500 dark:text-white">
            Aqui você pode visualizar, editar ou remover qualquer fluxo rapidamente.
          </p>
        </div>

        <div class="justify-self-center lg:justify-self-end flex gap-4">
          <Button
            v-if="flows.length < flowLimit"
            id="create-flow-button"
            label="Criar novo fluxo"
            size="small"
            :loading="loading"
            @click="createNewFlow"
          />
          <Button
            v-else
            v-tooltip.top="`Você só pode criar até ${flowLimit} fluxos.`"
            label="Limite atingido"
            size="small"
            disabled
          />
          <SelectButton
            id="view-mode-toggle"
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
            id="flows-container"
            class="flex flex-col items-center gap-4 h-full w-full justify-self-start bg-neutral-50 dark:bg-neutral-950 p-4 rounded-lg mb-8"
          >
            <div v-if="loading" class="flex justify-center items-center h-full">
              <i class="pi pi-spinner pi-spin !text-3xl text-neutral-200" />
            </div>

            <div
              v-else-if="flows.length"
              id="flow-cards-grid"
              class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4 w-full"
            >
              <Card
                v-for="flow in flows"
                :key="flow.flowId"
                class="w-full cursor-pointer flow-card"
                @click="((selectedFlow = flow), viewFlow())"
                @contextmenu="showContextMenu($event, flow)"
              >
                <template #title>
                  <div class="flex justify-between items-start">
                    <h3 class="text-sm truncate pr-2">
                      {{ flow.flowName }}
                    </h3>
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
            id="flows-table"
            :value="flows"
            :loading
            :rows="flowLimit"
            responsiveLayout="scroll"
            class="rounded-lg w-7xl h-full flex flex-col dark:bg-transparent"
            size="large"
            @row-click="
              (event) => {
                selectedFlow = event.data
                viewFlow()
              }
            "
            @row-contextmenu="
              (event) => showContextMenu(event.originalEvent as MouseEvent, event.data)
            "
          >
            <Column field="name" header="Nome" class="min-w-[200px] text-sm">
              <template #body="{ data }">
                {{ data.flowName }}
              </template>
            </Column>

            <Column
              field="description"
              header="Descrição"
              class="lg:max-w-[500px] md:max-w-200px truncate text-sm"
            >
              <template #body="{ data }">
                {{ data.flowDescription || '-' }}
              </template>
            </Column>

            <Column field="updatedAt" header="Última Atualização" class="min-w-[150px] text-sm">
              <template #body="{ data }">
                {{ formatDate(data.updatedAt) }}
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

      <ContextMenu ref="contextMenu" :model="menuItems" />
    </div>
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

:deep(.p-datatable-tbody > tr) {
  cursor: pointer;
}

.loading {
  display: inline-block;
  width: 2rem;
  height: 2rem;
}
</style>
