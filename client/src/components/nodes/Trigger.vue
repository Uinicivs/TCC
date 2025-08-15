<script setup lang="ts">
import { ref } from 'vue'

import type { INode } from '@/interfaces/node'

import NodeTemplate from '@/components/nodes/NodeTemplate.vue'

defineProps<{ data: INode }>()

const actions = ref([
  {
    icon: 'pi pi-plus',
    rounded: true,
    variant: 'outlined',
    size: 'small',
    severity: 'secondary',
  },
  {
    icon: 'pi pi-refresh',
    rounded: true,
    variant: 'outlined',
    size: 'small',
    severity: 'secondary',
  },
  {
    icon: 'pi pi-trash',
    rounded: true,
    variant: 'outlined',
    size: 'small',
    severity: 'danger',
  },
])
</script>

<template>
  <NodeTemplate icon="pi-bolt" icon-color="text-emerald-500" :data :actions />
</template>
