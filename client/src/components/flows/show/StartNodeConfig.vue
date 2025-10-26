<template>
  <div class="space-y-4">
    <div class="space-y-3">
      <h4 class="font-semibold text-md">Variáveis de entrada</h4>
      <div
        v-for="(variable, index) in variables"
        :key="`variable-${index}`"
        class="rounded-lg variables-wrapper p-4 relative"
      >
        <div class="flex-1 flex flex-col gap-4">
          <div class="w-full">
            <label
              :for="`name-${index}-${variable.displayName}`"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Nome da Variável
            </label>
            <InputText
              v-model="variable.displayName"
              :id="`name-${index}-${variable.displayName}`"
              placeholder="Ex.: full_name"
              class="w-full !bg-transparent"
              @input="updateVariables"
            />
          </div>

          <div class="w-full">
            <label
              :for="`type-${index}-${variable.displayName}`"
              class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
            >
              Tipo
            </label>
            <Select
              v-model="variable.type"
              :id="`type-${index}-${variable.displayName}`"
              :options="variableTypes"
              option-label="label"
              option-value="value"
              placeholder="Selecione o tipo"
              class="w-full !bg-transparent"
              @change="updateVariables"
            />
          </div>

          <div class="flex items-center w-full">
            <div class="flex items-center gap-2">
              <Checkbox
                v-model="variable.required"
                :id="`required-${index}-${variable.displayName}`"
                binary
                @change="updateVariables"
              />
              <label
                :for="`required-${index}-${variable.displayName}`"
                class="text-sm font-medium text-gray-700 dark:text-gray-300"
              >
                Variável obrigatória
              </label>
            </div>
          </div>
        </div>

        <Button
          icon="pi pi-times"
          class="!absolute top-0 right-0"
          severity="secondary"
          size="small"
          text
          rounded
          @click="removeVariable(index)"
        />
      </div>
    </div>

    <Button
      icon="pi pi-plus"
      label="Adicionar variável"
      severity="secondary"
      outlined
      size="small"
      @click="addVariable"
    />

    <div v-if="shouldShowAvailableVariablesLabel" class="mt-4 rounded-lg">
      <p class="text-sm font-medium mb-2">Variáveis Disponíveis:</p>
      <div class="flex flex-wrap gap-1">
        <template v-for="(variable, variableIndex) in variables" :key="`tag-${variableIndex}`">
          <div class="relative">
            <Tag v-if="variable.displayName" severity="secondary">
              {{ variable.displayName }} ({{ variable.type }})
            </Tag>
            <span v-if="variable.required" class="text-red-700 absolute -top-1 -right-1">*</span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { InputText, Select, Checkbox, Button, Tag } from 'primevue'

import type { Variable, VariableType } from '@/interfaces/variables'

interface StartNodeSettings {
  inputs?: Variable[]
}

const settings = defineModel<StartNodeSettings>({ required: true })

const variableTypes: Array<{ label: string; value: VariableType }> = [
  { label: 'Texto', value: 'text' },
  { label: 'Número', value: 'number' },
  { label: 'Booleano', value: 'bool' },
]

const variables = ref<Variable[]>([])

const shouldShowAvailableVariablesLabel = computed(() => {
  return variables.value.some((variable) => variable.displayName)
})

const updateVariables = () => {
  if (!settings.value) {
    settings.value = {}
  }

  settings.value = {
    ...settings.value,
    inputs: [...variables.value],
  }
}

const addVariable = async () => {
  const newVariable: Variable = {
    displayName: '',
    type: 'text',
    required: true,
  }

  variables.value.push(newVariable)
  updateVariables()
}

const removeVariable = (index: number) => {
  variables.value.splice(index, 1)
  updateVariables()
}

onMounted(() => {
  if (settings.value?.inputs && Array.isArray(settings.value.inputs)) {
    variables.value = [...settings.value.inputs]
    return
  }

  variables.value = []
})
</script>

<style scoped>
.variables-wrapper {
  border: 1px solid var(--p-surface-300);
}

:deep(.p-tag) {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}
</style>
