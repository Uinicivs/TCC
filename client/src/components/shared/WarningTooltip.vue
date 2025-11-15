<script setup lang="ts">
import { computed } from 'vue'

interface IProps {
  type: 'info' | 'warning' | 'error'
  message: string
}

const { type } = defineProps<IProps>()

const getColorClass = computed(() => {
  switch (type) {
    case 'info':
      return 'blue-500'
    case 'warning':
      return 'amber-500'
    case 'error':
      return 'red-500'
    default:
      return 'amber-500'
  }
})

const getIconClass = computed(() => {
  switch (type) {
    case 'info':
      return 'pi-info-circle'
    case 'warning':
      return 'pi-exclamation-triangle'
    case 'error':
      return 'pi-times-circle'
    default:
      return 'pi-exclamation-triangle'
  }
})
</script>

<template>
  <div
    class="absolute -right-6 -top-2 z-10 flex items-center justify-center cursor-default"
    v-tooltip="{
      value: message,
      pt: {
        root: { style: { maxWidth: '30rem' } },
        arrow: { style: { borderRightColor: `var(--p-${getColorClass})` } },
        text: `!bg-${getColorClass} !font-medium`,
      },
    }"
  >
    <i :class="`pi ${getIconClass} text-${getColorClass}`" />
  </div>
</template>
