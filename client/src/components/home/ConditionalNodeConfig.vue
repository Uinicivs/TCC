<template>
  <div class="space-y-2">
    <p class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      Expressão <span class="text-red-700">*</span>
    </p>

    <div ref="editorRef" class="rounded-md" />

    <div class="p-3 rounded-lg">
      <div v-for="section in tagSections" :key="section.label" class="mb-3">
        <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {{ section.label }}
        </p>

        <div class="flex flex-wrap gap-1">
          <Tag
            v-for="item in section.items"
            :key="item.key"
            class="cursor-pointer"
            severity="secondary"
            @click="item.onClick"
          >
            {{ item.label }}
          </Tag>
        </div>
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

interface ITagSectionItem {
  key: string
  label: string
  onClick: () => void
}

interface TagSection {
  label: string
  items: ITagSectionItem[]
}

interface Variable {
  name: string
  type: 'text' | 'number' | 'bool' | 'list' | 'object'
  required: boolean
}

let editorView: EditorView | null = null

const props = defineProps<{ variables?: Variable[] }>()
const expression = defineModel<string>('expression', { required: true })

const editorRef = ref<HTMLElement>()

const availableVariables = computed(() => props.variables || [])
const tagSections = computed<TagSection[]>(() => [
  {
    label: 'Variáveis disponíveis:',
    items: availableVariables.value.map((variable) => ({
      key: variable.name,
      label: `${variable.name} (${variable.type})`,
      onClick: () => insertVariable(variable.name),
    })),
  },
  {
    label: 'Funções:',
    items: MFEELFunctions.map((MFEELFunction) => ({
      key: MFEELFunction,
      label: `${MFEELFunction}()`,
      onClick: () => insertFunction(MFEELFunction),
    })),
  },
  {
    label: 'Operadores:',
    items: MFEELOperators.map((MFEELOperator) => ({
      key: MFEELOperator,
      label: MFEELOperator,
      onClick: () => insertOperator(MFEELOperator),
    })),
  },
])

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
            color: '#64748b !important',
            'font-size': '16px',
            'letter-spacing': '0.03em',
            'font-family': 'ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji"',
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
