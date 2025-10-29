<script setup lang="ts">
defineProps<{ message: string }>()
</script>

<template>
  <div
    class="absolute -right-6 -top-2 z-10 flex items-center justify-center cursor-default"
    v-tooltip="{
      value: message,
      pt: {
        root: { style: { maxWidth: '30rem' } },
        arrow: { style: { borderRightColor: 'var(--p-amber-500)' } },
        text: '!bg-amber-500 !font-medium',
      },
    }"
  >
    <i class="pi pi-exclamation-triangle text-amber-500" />
  </div>
</template>
