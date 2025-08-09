<script setup lang="ts">
import { ref } from 'vue'
import type { NodeProps } from '@vue-flow/core'

import NodeTemplate from '@/components/shared/NodeTemplate.vue'
import NodeActions from '@/components/shared/NodeActions.vue'
import type { NodeActionItem } from '@/components/shared/NodeActions.vue'

defineProps<NodeProps>()

const menuActions = ref<NodeActionItem[]>([
  { label: 'Add', icon: 'pi pi-plus' },
  { label: 'Update', icon: 'pi pi-refresh' },
  { label: 'Delete', icon: 'pi pi-trash', severity: 'danger' },
])

function onAction({ action, index }: { action: NodeActionItem; index: number }) {}
</script>

<template>
  <NodeTemplate
    icon="pi-bolt"
    icon-color="text-emerald-500"
    title="Trigger"
    description="Lorem ipsum dolor sit asdasdasd."
  >
    <template #actions>
      <NodeActions :actions="menuActions" @action="onAction" />
    </template>
  </NodeTemplate>
</template>
