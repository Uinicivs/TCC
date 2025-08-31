<template>
  <div class="space-y-2">
    <p class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      Expressão <span class="text-red-700">*</span>
    </p>

    <div ref="editorRef" class="rounded-md" />

    <div class="p-3 rounded-lg">
      <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        Variáveis disponíveis:
      </p>
      <div class="flex flex-wrap gap-1 mb-3">
        <Tag
          v-for="variable in availableVariables"
          :key="variable.name"
          :class="getVariableTagClass(variable.type)"
          @click="insertVariable(variable.name)"
        >
          {{ variable.name }} ({{ variable.type }})
        </Tag>
      </div>

      <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Funções:</p>
      <div class="flex flex-wrap gap-1 mb-3 w-1/2">
        <Tag
          v-for="func in MFEELFunctions"
          :key="func"
          class="cursor-pointer"
          @click="insertFunction(func)"
        >
          {{ func }}()
        </Tag>
      </div>

      <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Operadores:</p>
      <div class="flex flex-wrap gap-1 w-1/2">
        <Tag
          v-for="operator in MFEELOperators"
          :key="operator"
          class="cursor-pointer"
          @click="insertOperator(operator)"
        >
          {{ operator }}
        </Tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { Tag } from 'primevue'
import { EditorView } from 'codemirror'
import { placeholder } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { javascript } from '@codemirror/lang-javascript'
import { autocompletion, CompletionContext } from '@codemirror/autocomplete'

import { MFEELFunctions, MFEELOperators } from '@/constants/MFEEL'

interface Variable {
  name: string
  type: 'text' | 'number' | 'bool' | 'list' | 'object'
  required: boolean
}

const props = defineProps<{
  variables?: Variable[]
}>()

const expression = defineModel<string>('expression', { required: true })
const editorRef = ref<HTMLElement>()
let editorView: EditorView | null = null

const availableVariables = computed(() => props.variables || [])

function MFEELCompletions(context: CompletionContext) {
  const word = context.matchBefore(/\w*/)
  if (!word) return null

  const formattedFunctions = MFEELFunctions.map((func) => ({ label: func, type: 'function' }))
  const formattedOperators = MFEELOperators.filter((operator) => /^\w/.test(operator)).map(
    (operator) => ({ label: operator, type: 'keyword' }),
  )
  const formattedAvailableVariables = availableVariables.value.map((variable) => ({
    label: variable.name,
    type: 'variable',
  }))

  const completions = [
    ...formattedFunctions,
    ...formattedOperators,
    ...formattedAvailableVariables,
    { label: 'true', type: 'constant' },
    { label: 'false', type: 'constant' },
  ]

  return {
    from: word.from,
    options: completions,
  }
}

function getVariableTagClass(type: string): string {
  const baseClass = 'cursor-pointer '
  switch (type) {
    case 'text':
      return baseClass + 'bg-green-100 text-green-800'
    case 'number':
      return baseClass + 'bg-blue-100 text-blue-800'
    case 'bool':
      return baseClass + 'bg-red-100 text-red-800'
    case 'list':
      return baseClass + 'bg-yellow-100 text-yellow-800'
    case 'object':
      return baseClass + 'bg-indigo-100 text-indigo-800'
    default:
      return baseClass + 'bg-gray-100 text-gray-800'
  }
}

function insertVariable(varName: string) {
  if (editorView) {
    const pos = editorView.state.selection.main.head
    editorView.dispatch({ changes: { from: pos, insert: varName } })
    editorView.focus()
  }
}

function insertFunction(funcName: string) {
  if (editorView) {
    const pos = editorView.state.selection.main.head
    editorView.dispatch({ changes: { from: pos, insert: `${funcName}()` } })
    editorView.dispatch({ selection: { anchor: pos + funcName.length + 1 } })
    editorView.focus()
  }
}

function insertOperator(operator: string) {
  if (editorView) {
    const pos = editorView.state.selection.main.head
    editorView.dispatch({ changes: { from: pos, insert: ` ${operator} ` } })
    editorView.focus()
  }
}

onMounted(() => {
  if (editorRef.value) {
    const startState = EditorState.create({
      doc: expression.value || '',
      extensions: [
        javascript(),
        placeholder('Digite sua expressão MFEEL... Ex: age >= 18 and contains(skills, "python")'),
        autocompletion({
          override: [MFEELCompletions],
          maxRenderedOptions: 20,
        }),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            expression.value = update.state.doc.toString()
          }
        }),
        EditorView.theme({
          '&': {
            fontSize: '14px',
          },
          '.cm-placeholder': {
            color: '#64748b',
          },
          '.cm-content': {
            padding: '8px',
            minHeight: '95px',
          },
          '.cm-line span': {
            color: '#334155',
          },
          '.cm-focused': {
            outline: '1px solid #3b82f6',
          },
        }),
      ],
    })

    editorView = new EditorView({
      state: startState,
      parent: editorRef.value,
    })
  }
})

watch(
  () => expression.value,
  (newValue) => {
    if (editorView && newValue !== editorView.state.doc.toString()) {
      editorView.dispatch({
        changes: {
          from: 0,
          to: editorView.state.doc.length,
          insert: newValue || '',
        },
      })
    }
  },
)
</script>

<style scoped>
:deep(.cm-editor) {
  border: 1px solid var(--p-textarea-border-color);
  border-radius: 0.375rem;
  outline: none;
}

:deep(.cm-editor.cm-focused) {
  border-color: var(--p-textarea-focus-border-color);
  box-shadow: none;
}

:deep(.p-tag) {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}
</style>
