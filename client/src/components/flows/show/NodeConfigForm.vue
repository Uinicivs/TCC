<script setup lang="ts">
import { provide, ref } from 'vue'
import { InputText, Message } from 'primevue'
import { z } from 'zod'

import type { INode, IMappedNodes } from '@/interfaces/node'

const nodeTitleSchema = z.object({
  title: z.string().min(1, 'O nome do nó é obrigatório'),
})

const nodeData = defineModel<INode>('nodeData', { required: true })

defineProps<{ selectedNode: IMappedNodes | null }>()

const errors = ref<Record<string, string>>({})

const validateTitle = (): boolean => {
  try {
    nodeTitleSchema.parse({ title: nodeData.value.title })
    errors.value = {}
    return true
  } catch (error) {
    if (error instanceof z.ZodError) {
      const newErrors: Record<string, string> = {}
      error.issues.forEach((issue) => {
        const field = issue.path[0] as string
        newErrors[field] = issue.message
      })
      errors.value = newErrors
    }
    return false
  }
}

provide('nodeData', nodeData)

defineExpose({
  validateTitle,
})
</script>

<template>
  <div class="space-y-2">
    <div class="space-y-2">
      <label for="nodeTitle" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Nome <span class="text-red-700">*</span>
      </label>
      <InputText
        id="nodeTitle"
        v-model="nodeData.title"
        :invalid="!!errors.title"
        placeholder="Digite um nome para o nó"
        autofocus
        required
        class="w-full !bg-transparent"
        size="small"
        @blur="validateTitle"
      />
      <Message v-if="errors.title" severity="error" size="small" variant="simple">
        {{ errors.title }}
      </Message>
      <Message v-else size="small" severity="secondary" variant="simple">
        Este será o nome exibido no nó.
      </Message>
    </div>

    <component
      :is="selectedNode?.configComponent"
      v-if="selectedNode?.configComponent"
      v-model="nodeData.settings"
      class="w-full"
    />
  </div>
</template>
