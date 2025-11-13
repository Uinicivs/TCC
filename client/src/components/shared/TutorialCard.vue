<template>
  <div class="tutorial-card p-4 flex flex-col gap-4 max-w-md rounded-lg shadow-xl">
    <div class="flex justify-between items-start">
      <div class="flex-1">
        <h3 v-if="title" class="text-neutral-600 dark:text-neutral-300 text-lg font-medium mb-2">
          {{ title }}
        </h3>

        <p class="text-sm text-neutral-600 dark:text-neutral-300">
          {{ description }}
        </p>
      </div>
    </div>

    <div v-if="imagePath" class="flex justify-center">
      <img :src="imagePath" :alt="title || 'Tutorial step'" class="max-w-full rounded-lg" />
    </div>

    <div class="flex items-center justify-between gap-3 mt-2">
      <div class="flex gap-2">
        <Button
          v-if="!isFirstStep"
          label="Anterior"
          severity="secondary"
          size="small"
          outlined
          @click="onPreviousStep"
        />
        <Button v-if="!isLastStep" label="Próximo" size="small" @click="onNextStep" />
        <Button v-else label="Concluir" size="small" @click="onFinish(false)" />
      </div>

      <div class="flex items-center gap-3">
        <span class="text-xs text-neutral-500 dark:text-neutral-400">
          {{ stepIndex }} / {{ steps.length }}
        </span>

        <Button label="Pular" severity="secondary" size="small" text @click="onFinish(true)" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from 'primevue'
import type { ITutorialCard } from '@/interfaces/tutorial'

defineProps<ITutorialCard>()
</script>

<style scoped>
.tutorial-card {
  background: var(--p-content-background);
}
</style>
