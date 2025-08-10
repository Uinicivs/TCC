<script setup lang="ts">
import { ref } from 'vue'

import NodeTemplate from '@/components/shared/NodeTemplate.vue'

const menuActions = ref([
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
    icon="pi-bolt"
    icon-color="text-emerald-500"
    title="Trigger"
    description="Lorem ipsum dolor sit asdasdasd."
    :actions="menuActions"
  />
</template>
