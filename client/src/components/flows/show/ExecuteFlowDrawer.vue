<template>
  <Drawer
    :visible="visible"
    position="right"
    header="Executar Fluxo"
    :style="{ width: '30rem' }"
    :breakpoints="{ '1199px': '75vw', '575px': '90vw' }"
    @update:visible="emit('update:visible', $event)"
  >
    <div class="flex flex-col gap-4 h-full">
      <div v-if="!startVariables.length" class="text-center m-auto">
        <i class="pi pi-info-circle text-4xl" />
        <p class="text-lg font-medium mb-2">Nenhuma variável de entrada</p>
        <p class="text-sm">
          Este fluxo não possui variáveis de entrada configuradas no nó de início.
        </p>
      </div>

      <div v-else class="space-y-4">
        <p class="text-sm">Preencha os valores das variáveis para executar o fluxo.</p>

        <div
          v-for="variable in startVariables"
          :key="variable.displayName"
          class="flex flex-col gap-2"
        >
          <label :for="`var-${variable.displayName}`" class="font-medium">
            {{ variable.displayName }}
            <span v-if="variable.required" class="text-red-500">*</span>
            <span class="text-sm font-normal ml-1">({{ getTypeLabel(variable.type) }})</span>
          </label>

          <InputText
            v-if="variable.type === 'text'"
            :id="`var-${variable.displayName}`"
            v-model="formData[variable.displayName] as string"
            :placeholder="`Digite o valor para ${variable.displayName}`"
            :disabled="loading"
            :required="variable.required"
            size="small"
            class="w-full"
          />

          <InputNumber
            v-else-if="variable.type === 'number'"
            :id="`var-${variable.displayName}`"
            v-model="formData[variable.displayName] as number"
            :placeholder="`Digite o valor para ${variable.displayName}`"
            :disabled="loading"
            :required="variable.required"
            size="small"
            class="w-full"
          />

          <div v-else-if="variable.type === 'bool'" class="flex items-center gap-2">
            <ToggleSwitch
              :id="`var-${variable.displayName}`"
              v-model="formData[variable.displayName] as boolean"
              :disabled="loading"
            />
            <span class="text-sm">
              {{ formData[variable.displayName] ? 'Sim' : 'Não' }}
            </span>
          </div>

          <div v-else-if="variable.type === 'list'">
            <Textarea
              :id="`var-${variable.displayName}`"
              v-model="formData[variable.displayName] as string"
              :placeholder="getPlaceholder(variable.type)"
              :disabled="loading"
              :required="variable.required"
              rows="3"
              class="w-full text-sm"
            />
          </div>
        </div>

        <div v-if="executionResult" class="mt-4 p-3 rounded-lg result-wrapper">
          <h4 class="font-semibold mb-2 flex items-center gap-2">
            <i class="pi pi-check-circle text-emerald-600" />
            Resultado da Execução
          </h4>
          <div class="p-3 font-mono text-sm">
            <pre>{{ JSON.stringify(executionResult, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="flex justify-end gap-2">
        <Button
          label="Cancelar"
          severity="secondary"
          variant="outlined"
          size="small"
          :disabled="loading"
          @click="emit('update:visible', false)"
        />

        <Button
          label="Executar"
          size="small"
          :loading="loading"
          :disabled="!isFormValid || !startVariables.length"
          @click="handleExecute"
        />
      </div>
    </template>
  </Drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Drawer, InputText, InputNumber, ToggleSwitch, Textarea, Button } from 'primevue'
import { useToast } from 'primevue/usetoast'

import type { Variable } from '@/interfaces/variables'
import { evaluateFlow } from '@/services/flowService'

interface Props {
  visible: boolean
  flowId: string
  startVariables: Variable[]
}

interface Emits {
  (event: 'update:visible', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const toast = useToast()

const loading = ref(false)
const formData = ref<Record<string, string | number | boolean>>({})
const executionResult = ref<unknown>(null)
const executionError = ref<string | null>(null)

const getTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    text: 'Texto',
    number: 'Número',
    bool: 'Booleano',
    list: 'Lista',
  }
  return labels[type] || type
}

const getPlaceholder = (type: string): string => {
  if (type === 'list') {
    return '["item1", "item2", "item3"]'
  }
  return ''
}

const isFormValid = computed(() => {
  return props.startVariables.every((variable) => {
    if (!variable.required) return true

    const value = formData.value[variable.displayName]

    if (variable.type === 'bool') {
      return value !== undefined && value !== null
    }

    if (variable.type === 'number') {
      return value !== undefined && value !== null && value !== ''
    }

    return value !== undefined && value !== null && value !== ''
  })
})

const resetForm = () => {
  formData.value = {}
  executionResult.value = null
  executionError.value = null

  props.startVariables.forEach((variable) => {
    if (variable.type === 'bool') {
      formData.value[variable.displayName] = false
    } else if (variable.type === 'number') {
      formData.value[variable.displayName] = 0
    } else {
      formData.value[variable.displayName] = ''
    }
  })
}

const validateAndParseInput = (variable: Variable, value: unknown): unknown => {
  if (variable.type === 'list') {
    if (typeof value === 'string' && value.trim()) {
      try {
        return JSON.parse(value)
      } catch {
        throw new Error(`Formato inválido para ${variable.displayName}. Use JSON válido.`)
      }
    }
  }

  if (variable.type === 'number' && typeof value === 'string') {
    const num = Number(value)
    if (isNaN(num)) {
      throw new Error(`${variable.displayName} deve ser um número válido.`)
    }
    return num
  }

  return value
}

const handleExecute = async () => {
  try {
    loading.value = true
    executionResult.value = null
    executionError.value = null

    const payload: Record<string, unknown> = {}

    for (const variable of props.startVariables) {
      const rawValue = formData.value[variable.displayName]
      payload[variable.displayName] = validateAndParseInput(variable, rawValue)
    }

    const result = await evaluateFlow(props.flowId, payload)
    executionResult.value = result

    toast.add({
      severity: 'success',
      summary: 'Sucesso!',
      detail: 'Fluxo executado com sucesso',
      life: 3000,
    })
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Erro desconhecido'
    executionError.value = errorMessage

    toast.add({
      severity: 'error',
      summary: 'Erro na Execução',
      detail: errorMessage,
      life: 5000,
    })
  } finally {
    loading.value = false
  }
}

watch(
  () => props.visible,
  (newValue) => {
    if (newValue) {
      resetForm()
    }
  },
  { immediate: true },
)
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-break: break-word;
}

.result-wrapper {
  border: 1px solid var(--p-focus-ring-color);
}
</style>
