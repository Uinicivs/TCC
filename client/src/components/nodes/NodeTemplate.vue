<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import { Position, Handle } from '@vue-flow/core'
import { ContextMenu, useDialog } from 'primevue'

import type { INode } from '@/interfaces/node'

import { useNodeActions } from '@/composable/useNodeActions'
import { useFlowStore } from '@/stores/flow'

import AddNode from '@/components/flows/show/AddNode.vue'
import DeleteNodeDialog from '@/components/flows/show/DeleteNodeDialog.vue'
import EditNode from '@/components/flows/show/EditNode.vue'
import WarningTooltip from '@/components/shared/WarningTooltip.vue'

type NodeTemplateProps = { id?: string; data?: INode } & {
  icon?: string
  iconColor?: string
  containerClass?: string
  handleSourcePosition?: Position
}

const { data, id } = defineProps<NodeTemplateProps>()

const flowStore = useFlowStore()
const dialog = useDialog()
const nodeWrapperRef = useTemplateRef('node-wrapper')
const contextMenu = useTemplateRef('contextMenu')
const editNodeRef = useTemplateRef('editNode')
const { canAddNewNode } = useNodeActions(id)

const getCurrentNodeWrapperWidth = computed<number>(() => {
  return nodeWrapperRef.value?.clientWidth || 250
})

const isConditionalNode = computed<boolean>(() => {
  if (!id) return false

  const currentNode = flowStore.getNodeById(id)
  return currentNode?.type === 'conditional'
})

const isFirstNode = computed<boolean>(() => {
  return flowStore.getFirstNode?.id === id
})

const warningMessage = computed<string | null>(() => {
  if (!id) return null
  return flowStore.getWarningForNodeId(id)
})

const handleClick = (event: MouseEvent): void => {
  contextMenu.value?.show(event)
}

const openDeleteDialog = () => {
  const currentNode = flowStore.getNodeById(id || '')
  if (!currentNode) return

  dialog.open(DeleteNodeDialog, {
    props: {
      header: 'Confirmar Exclusão',
      style: { width: '30rem' },
      modal: true,
    },
    emits: {
      onConfirm: () => {
        flowStore.removeNode(currentNode)
      },
    },
  })
}

const openEditDialog = () => {
  if (id && editNodeRef.value) {
    editNodeRef.value.openDrawer()
  }
}

const menuItems = computed(() => {
  const options = [
    {
      name: 'edit',
      label: 'Editar',
      icon: 'pi pi-pencil',
      command: openEditDialog,
    },
    {
      name: 'delete',
      label: 'Excluir',
      icon: 'pi pi-trash',
      command: openDeleteDialog,
    },
  ]

  return isFirstNode.value ? options.filter(({ name }) => name !== 'delete') : options
})
</script>

<template>
  <div
    ref="node-wrapper"
    class="relative w-[250px] cursor-pointer"
    @contextmenu="handleClick($event)"
    @click.stop="openEditDialog"
  >
    <Handle type="target" :position="Position.Top" />

    <transition name="fade">
      <WarningTooltip v-if="warningMessage" :message="warningMessage" />
    </transition>

    <div
      class="bg-neutral-50 p-4 border border-[#e2e8f0] rounded-lg dark:bg-neutral-900 dark:border-neutral-900 max-w-[300px] node-content"
      :class="containerClass"
    >
      <div class="flex gap-4 h-full">
        <i
          v-if="icon"
          :class="[icon, iconColor]"
          class="pi bg-neutral-50 p-4 border rounded-sm border-gray-300 dark:bg-neutral-900 dark:border-neutral-800"
          style="font-size: 1.3em"
        />

        <div class="overflow-hidden w-full h-full flex flex-col items-center justify-center">
          <h4
            v-if="data?.title"
            v-tooltip.left="{
              value: data.title,
              pt: {
                arrow: { style: { borderLeftColor: 'var(--p-neutral-50)' } },
                text: '!bg-neutral-50 !text-black dark:text-white ',
              },
            }"
            class="font-semibold w-full text-xs text-ellipsis overflow-hidden"
          >
            {{ data.title }}
          </h4>
        </div>
      </div>
    </div>

    <Handle v-if="!isConditionalNode" type="source" :position="Position.Bottom" />

    <template v-if="isConditionalNode">
      <Handle type="source" :position="Position.Left" id="conditional-left" />

      <Handle type="source" :position="Position.Right" id="conditional-right" />
    </template>

    <template v-if="isConditionalNode">
      <AddNode
        class="absolute -left-25 top-[30%] add-node-button cursor-default"
        :parentId="id || null"
        handleId="conditional-left"
      />

      <AddNode
        class="absolute -right-20 top-[30%] add-node-button cursor-default"
        :parentId="id || null"
        handleId="conditional-right"
      />
    </template>

    <AddNode
      v-else-if="canAddNewNode"
      class="absolute -bottom-12 add-node-button"
      :style="{ left: `${getCurrentNodeWrapperWidth / 2 - 16}px` }"
      :parentId="id || null"
    />

    <ContextMenu ref="contextMenu" :model="menuItems" />

    <EditNode v-if="id" ref="editNode" :node-id="id" />
  </div>
</template>
