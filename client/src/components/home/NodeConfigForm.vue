<script setup lang="ts">
import { InputText, Textarea, Message } from 'primevue'

import type { INode, IMappedNodes } from '@/interfaces/node'

const nodeData = defineModel<INode>('nodeData', { required: true })

defineProps<{ selectedNode: IMappedNodes | null }>()

const emit = defineEmits<{ 'updated:settings': [settings: INode['settings']] }>()
</script>

<template>
  <div class="space-y-4">
    <div class="space-y-2">
      <label for="nodeTitle" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Nome <span class="text-red-700">*</span>
      </label>
      <InputText
        id="nodeTitle"
        v-model="nodeData.title"
        placeholder="Digite um nome para o nó"
        autofocus
        required
        class="w-full"
      />
      <Message size="small" severity="secondary" variant="simple">
        Este será o nome exibido no nó.
      </Message>
    </div>
    <div class="space-y-2">
      <label for="nodeDescription" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
        Descrição
      </label>
      <Textarea
        id="nodeDescription"
        v-model="nodeData.description"
        placeholder="Digite uma descrição para o nó (opcional)"
        rows="3"
        class="w-full"
      />
      <Message size="small" severity="secondary" variant="simple">
        Descrição opcional para documentar o propósito do nó.
      </Message>
    </div>

    <component
      :is="selectedNode?.configComponent"
      v-if="selectedNode?.configComponent"
      @updated:settings="emit('updated:settings', $event)"
      class="w-full"
    />
  </div>
</template>
