<template>
  <div class="tutorial-card flex flex-col gap-4 rounded-lg">
    <div v-if="imagePath" class="flex justify-center overflow-hidden rounded-t-lg">
      <img
        :src="imagePath"
        :alt="title || 'Tutorial step'"
        class="w-full h-auto max-h-96 object-contain"
      />
    </div>

    <div class="p-4">
      <div class="flex justify-between items-start">
        <div class="flex-1">
          <h3 v-if="title" class="text-neutral-600 dark:text-neutral-300 text-lg font-medium mb-2">
            {{ title }}
          </h3>
          <p
            v-if="!Array.isArray(description)"
            class="text-sm text-neutral-600 dark:text-neutral-300"
          >
            {{ description }}
          </p>
          <p v-else class="text-sm text-neutral-600 dark:text-neutral-300 space-y-2">
            <span v-for="(line, index) in description" :key="index" class="block">
              {{ line }}
            </span>
          </p>
        </div>
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
