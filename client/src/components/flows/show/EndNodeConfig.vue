<template>
  <div class="space-y-4">
    <div class="space-y-3">
      <h4 class="font-semibold text-md">Resposta esperada</h4>
      <div class="space-y-4">
        <div class="flex items-center gap-3 p-3 response-wrapper rounded-lg">
          <RadioButton
            v-model="responseType"
            input-id="default-response"
            value="default"
            @change="updateResponse"
          />
          <label for="default-response" class="cursor-pointer">
            <div>
              <p class="font-medium">Usar resposta padrão</p>
              <p class="text-sm">
                Retorna automaticamente:
                <code class="bg-gray-100 dark:bg-gray-800 px-1 rounded text-xs">
                  {{ defaultResponseValue }}
                </code>
              </p>
            </div>
          </label>
        </div>

        <div class="flex flex-col gap-3 p-3 response-wrapper rounded-lg">
          <div class="flex items-center gap-3">
            <RadioButton
              v-model="responseType"
              input-id="custom-response"
              value="custom"
              @change="updateResponse"
            />
            <label for="custom-response" class="cursor-pointer">
              <p class="font-medium">Resposta customizada</p>
              <p class="text-sm">Configure uma resposta customizada</p>
            </label>
          </div>

          <transition name="fade">
            <div v-if="responseType === 'custom'" class="space-y-3">
              <div>
                <label class="block text-sm font-medium mb-2"> Valor da resposta </label>
                <Textarea
                  v-model="customResponseText"
                  placeholder='{"status": "success", "reason": "Operação concluída"}'
                  rows="4"
                  class="w-full font-mono text-sm"
                  @input="updateResponse"
                />
              </div>
              <Message v-if="parseError" severity="error" :closable="false" size="small">
                <div class="flex items-center gap-2">
                  <i class="pi pi-exclamation-triangle" />
                  <span class="text-sm">{{ parseError }}</span>
                </div>
              </Message>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, inject, onMounted, type Ref } from 'vue'
import { RadioButton, Textarea, Message } from 'primevue'

import type { INode } from '@/interfaces/node'
import type { SchemaNode } from '@/utils/flowFormatters'

type TEndNodeResponse = SchemaNode['metadata']['response']

const settings = defineModel<SchemaNode['metadata']>({ required: true })

const nodeData = inject<Ref<INode>>('nodeData', {} as Ref<INode>)

const responseType = ref<'default' | 'custom'>('default')
const customResponseText = ref<string>('')
const parseError = ref<string>('')

const defaultResponseValue = computed(() => nodeData.value.isFalseCase ?? false)

const validateAndParseCustomResponse = (): TEndNodeResponse => {
  parseError.value = ''

  if (!customResponseText.value.trim()) {
    return undefined
  }

  try {
    const parsed = JSON.parse(customResponseText.value)
    return parsed
  } catch {
    parseError.value = 'JSON inválido. Verifique a sintaxe.'
    return undefined
  }
}

const updateResponse = () => {
  if (!settings.value) {
    settings.value = {}
  }

  let responseValue: TEndNodeResponse

  if (responseType.value === 'default') {
    responseValue = defaultResponseValue.value
  } else {
    responseValue = validateAndParseCustomResponse()
  }

  settings.value = {
    ...settings.value,
    response: responseValue,
  }
}

watch(
  () => nodeData.value.isFalseCase,
  () => {
    if (responseType.value === 'default') {
      updateResponse()
    }
  },
  { immediate: true },
)

const initializeComponent = () => {
  const currentResponse = settings.value.response
  if (!settings.value || currentResponse === undefined) {
    responseType.value = 'default'
    updateResponse()
    return
  }

  if (currentResponse === defaultResponseValue.value) {
    responseType.value = 'default'
    return
  }

  responseType.value = 'custom'
  customResponseText.value = JSON.stringify(currentResponse, null, 2)
  return
}

onMounted(() => {
  initializeComponent()
})
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-break: break-word;
}

.response-wrapper {
  border: 1px solid var(--p-surface-300);
}
</style>
