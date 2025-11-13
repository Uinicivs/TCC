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
import { Button } from 'primevue'
import { useTutorial } from '@/composable/useTutorial'
import type { IStep } from '@/interfaces/tutorial'

interface Props {
  steps: IStep[]
  onFinish?: (skip?: boolean) => void
}

const props = defineProps<Props>()

const handleClick = () => {
  useTutorial({
    steps: props.steps,
    onFinish: props.onFinish,
  })
}
</script>
