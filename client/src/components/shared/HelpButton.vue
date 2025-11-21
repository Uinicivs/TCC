<template>
  <Button
    icon="pi pi-question-circle"
    severity="secondary"
    size="small"
    class="w-8 h-8"
    @click="handleClick"
  />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { Button } from 'primevue'
import { useAuthStore } from '@/stores/auth'
import { useTutorial } from '@/composable/useTutorial'
import type { IStep } from '@/interfaces/tutorial'

interface Props {
  steps: IStep[]
  onFinish?: (skip?: boolean) => void
}

const props = defineProps<Props>()
const authStore = useAuthStore()

onMounted(() => {
  if (authStore.user?.firstAccess) {
    handleClick()
  }
})

const handleClick = () => {
  useTutorial({
    steps: props.steps,
    onFinish: (skip?: boolean) => {
      if (authStore.user?.firstAccess) {
        authStore.user.firstAccess = false
      }
      if (props.onFinish) props.onFinish(skip)
    },
  })
}
</script>

<style scoped>
.p-button.p-button-secondary {
  border: none;
  outline: none;
}

.p-button.p-button-secondary:hover {
  background: var(--p-surface-100);
  color: var(--p-surface-700);
}

.dark .p-button.p-button-secondary:hover {
  background: var(--p-surface-800);
  color: var(--p-surface-0);
}
</style>
