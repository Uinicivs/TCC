<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { Position, Handle, type Node } from '@vue-flow/core'
import type { ButtonProps } from 'primevue'

import type { INode } from '@/interfaces/node'

import { useFlowStore } from '@/stores/flow'

import AddNode from '@/components/home/AddNode.vue'

type NodeTemplateProps = { id?: string; data?: INode } & {
  icon?: string
  iconColor?: string
  actions?: ButtonProps[]
  containerClass?: string
}

const nodeWrapperRef = useTemplateRef('node-wrapper')

const { getLastNodes, getNodeById } = useFlowStore()

const { actions, data, id } = defineProps<NodeTemplateProps>()

const isVisibleActions = ref(false)

const handleClick = (): void => {
  if (!actions?.length) return
  isVisibleActions.value = !isVisibleActions.value
}

const canAddNewNode = computed<boolean>(() => {
  let currentNode: Node | null = null
  const lastNodes = getLastNodes()

  if (id) {
    currentNode = getNodeById(id) ?? null
  }

  const isLastNode = lastNodes.some(node => node.id === id)
  const currentNodeType = currentNode?.type || ''
  const couldHaveMoreWays = ['conditional'].includes(currentNodeType)

  return isLastNode || couldHaveMoreWays
})

const getCurrentNodeWrapperWidth = computed<number>(() => {
  return nodeWrapperRef.value?.clientWidth || 250
})
</script>

<template>
  <div ref="node-wrapper" class="cursor-pointer relative w-[250px]" @click="handleClick">
    <Handle type="target" :position="Position.Top" />
    <div
      class="bg-neutral-50 p-4 border border-[#e2e8f0] rounded-lg dark:bg-neutral-950 dark:border-neutral-900 flex gap-4 max-w-[300px]"
      :class="containerClass"
    >
      <i
        v-if="icon"
        :class="[icon, iconColor]"
        class="pi bg-neutral-50 p-4 border rounded-sm border-gray-300 dark:bg-neutral-900 dark:border-neutral-800"
        style="font-size: 1.3em"
      />

      <div class="overflow-auto">
        <h4 v-if="data?.title" class="font-semibold truncate">
          {{ data.title }}
        </h4>

        <p v-if="data?.description" class="truncate">
          {{ data.description }}
        </p>
      </div>

      <!-- <NodeActions v-if="actions?.length" :actions :is-visible="isVisibleActions" /> -->
    </div>
    <Handle type="source" :position="Position.Bottom" />

    <AddNode
      v-if="canAddNewNode"
      class="absolute -bottom-12"
      :style="{ left: `${getCurrentNodeWrapperWidth / 2 - 16}px` }"
      :parentId="id || null"
    />
  </div>
</template>
