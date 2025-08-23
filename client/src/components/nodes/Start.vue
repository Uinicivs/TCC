<script setup lang="ts">
import { ref } from 'vue'

import type { INode } from '@/interfaces/node'

import NodeTemplate from '@/components/nodes/NodeTemplate.vue'

defineProps<{ data: INode; id: string }>()

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
  <NodeTemplate
    class="!w-20"
    container-class="!rounded-full h-20 text-center !w-full outline-emerald-400 outline-4"
    :id
    :data
    :actions
  />
</template>
