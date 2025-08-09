<script setup lang="ts">
import { Position } from '@vue-flow/core'
import { NodeToolbar } from '@vue-flow/node-toolbar'
import Button from 'primevue/button'

export interface NodeActionItem {
  label: string
  icon?: string
  severity?: 'secondary' | 'primary' | 'success' | 'info' | 'warn' | 'danger' | undefined
  rounded?: boolean
  variant?: 'text' | 'outlined' | 'tonal' | 'filled' | undefined
  size?: 'small' | 'large' | undefined
}

const props = defineProps<{
  actions: NodeActionItem[]
  position?: Position
  offset?: number
}>()

const emit = defineEmits<{
  (event: 'action', payload: { action: NodeActionItem; index: number }): void
}>()

const toolbarPosition = props.position ?? Position.Right
const toolbarOffset = props.offset ?? 15
</script>

<template>
  <NodeToolbar :offset="toolbarOffset" :position="toolbarPosition" class="flex flex-col gap-2">
    <template v-for="(action, index) in actions" :key="index">
      <Button
        :icon="action.icon"
        :rounded="action.rounded ?? true"
        :variant="action.variant ?? 'outlined'"
        :size="action.size ?? 'small'"
        :severity="action.severity ?? 'secondary'"
        @click="emit('action', { action, index })"
      />
    </template>
  </NodeToolbar>
</template>
