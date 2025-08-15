<script setup lang="ts">
import { ref } from 'vue'
import { Position, Handle } from '@vue-flow/core'
import type { ButtonProps } from 'primevue'

import type { INode } from '@/interfaces/node'

import NodeActions from '@/components/nodes/NodeActions.vue'

type NodeTemplateProps = { data: INode } & {
  icon?: string
  iconColor?: string
  actions?: ButtonProps[]
}

const { actions, data } = defineProps<NodeTemplateProps>()

const isVisibleActions = ref(false)

const handleClick = (): void => {
  if (!actions?.length) return
  isVisibleActions.value = !isVisibleActions.value
}
</script>

<template>
  <div @click="handleClick" class="cursor-pointer min-w-[250px]">
    <Handle type="target" :position="Position.Top" />
    <div
      class="bg-white p-4 border rounded-lg border-[#e2e8f0] dark:bg-neutral-950 dark:border-neutral-900 flex gap-4 max-w-[300px]"
    >
      <i
        v-if="icon"
        :class="[icon, iconColor]"
        class="pi bg-neutral-50 p-4 border rounded-sm border-gray-300 dark:bg-neutral-900 dark:border-neutral-800"
        style="font-size: 1.3em"
      />

      <div class="overflow-auto">
        <h4 v-if="data.title" class="text-lg font-semibold truncate">
          {{ data.title }}
        </h4>

        <p v-if="data.description" class="truncate">
          {{ data.description }}
        </p>
      </div>

      <NodeActions v-if="actions?.length" :actions :is-visible="isVisibleActions" />
    </div>
    <Handle type="source" :position="Position.Bottom" />
  </div>
</template>
