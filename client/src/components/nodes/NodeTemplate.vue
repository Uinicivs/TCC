<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { Position, Handle } from '@vue-flow/core'
import type { ButtonProps } from 'primevue'

import type { INode } from '@/interfaces/node'

import { useConditionalHandles } from '@/composable/useConditionalHandles'
import { useNodeActions } from '@/composable/useNodeActions'

import AddNode from '@/components/home/AddNode.vue'

type NodeTemplateProps = { id?: string; data?: INode } & {
  icon?: string
  iconColor?: string
  actions?: ButtonProps[]
  containerClass?: string
  handleSourcePosition?: Position
}

const nodeWrapperRef = useTemplateRef('node-wrapper')

const { actions, data, id } = defineProps<NodeTemplateProps>()

const isVisibleActions = ref(false)

const { canAddNewNode } = useNodeActions(id)
const { isConditionalNode, canAddToLeftPath, canAddToRightPath } = useConditionalHandles(id)

const handleClick = (): void => {
  if (!actions?.length) return
  isVisibleActions.value = !isVisibleActions.value
}

const getCurrentNodeWrapperWidth = computed<number>(() => {
  return nodeWrapperRef.value?.clientWidth || 250
})
</script>

<template>
  <div ref="node-wrapper" class="cursor-pointer relative w-[250px]" @click="handleClick">
    <Handle type="target" :position="Position.Top" />

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
          <h4 v-if="data?.title" class="font-semibold truncate">
            {{ data.title }}
          </h4>

          <p v-if="data?.description" class="truncate">
            {{ data.description }}
          </p>
        </div>
      </div>
    </div>

    <Handle v-if="!isConditionalNode" type="source" :position="Position.Bottom" />

    <template v-if="isConditionalNode">
      <Handle
        type="source"
        :position="Position.Left"
        id="conditional-left"
        class="conditional-handle-left"
      />

      <Handle
        type="source"
        :position="Position.Right"
        id="conditional-right"
        class="conditional-handle-right"
      />
    </template>

    <template v-if="isConditionalNode">
      <AddNode
        v-if="canAddToLeftPath"
        class="absolute -left-20 top-1/3 add-node-button"
        :parentId="id || null"
        handleId="conditional-left"
      />

      <AddNode
        v-if="canAddToRightPath"
        class="absolute -right-20 top-1/3 add-node-button"
        :parentId="id || null"
        handleId="conditional-right"
      />
    </template>

    <AddNode
      v-if="canAddNewNode && !isConditionalNode"
      class="absolute -bottom-12 add-node-button"
      :style="{ left: `${getCurrentNodeWrapperWidth / 2 - 16}px` }"
      :parentId="id || null"
    />
  </div>
</template>
