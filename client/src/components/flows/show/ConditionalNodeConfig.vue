<template>
  <div class="space-y-2">
    <p class="block text-sm font-medium text-gray-700 dark:text-gray-300">
      Expressão <span class="text-red-700">*</span>
    </p>

    <div ref="editorRef" class="rounded-md" />

    <Message v-if="errors.expression" severity="error" size="small" variant="simple">
      {{ errors.expression }}
    </Message>

    <div class="rounded-lg">
      <div v-for="section in tagSections" :key="section.label" class="mb-3">
        <p
          v-if="section.items && section.items.length"
          class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
        >
          {{ section.label }}
        </p>

        <div class="flex flex-wrap gap-1">
          <template v-for="item in section.items" :key="item.key">
            <div class="relative">
              <Tag class="cursor-pointer" severity="secondary" @click="item.onClick">
                {{ item.label }}
              </Tag>
              <span v-if="item.required" class="text-red-700 absolute -top-1 -right-1">*</span>
            </div>
          </template>
        </div>
      </div>
    </div>

    <Message severity="info" size="small" :closable="false" class="mt-6">
      <div class="space-y-2">
        <p class="font-semibold text-sm">💡 Como usar as funções:</p>
        <ul class="space-y-1 text-xs ml-6">
          <li class="mb-4">
            <code class="font-semibold bg-surface-100 dark:bg-surface-800">
              contains(texto, valor)
            </code>
            <div>Verifica se um valor está presente em um texto</div>
          </li>
          <li class="mb-4">
            <code class="font-semibold bg-surface-100 dark:bg-surface-800"> length(texto) </code>
            <div>Retorna o número de elementos de um texto</div>
          </li>
          <li class="mb-4">
            <code class="font-semibold bg-surface-100 dark:bg-surface-800">
              startsWith(texto, valor)
            </code>
            <div>Verifica se um texto começa com o valor especificado</div>
          </li>
          <li>
            <code class="font-semibold bg-surface-100 dark:bg-surface-800">
              endsWith(texto, valor)
            </code>
            <div>Verifica se um texto termina com o valor especificado</div>
          </li>
        </ul>
      </div>
    </Message>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { Tag, Message } from 'primevue'
import { EditorView } from 'codemirror'
import { placeholder } from '@codemirror/view'
import { EditorState } from '@codemirror/state'
import { javascript } from '@codemirror/lang-javascript'
import { autocompletion, CompletionContext } from '@codemirror/autocomplete'
import { z } from 'zod'

import { useFlowStore } from '@/stores/flow'

import type { Variable } from '@/interfaces/variables'

import { MFEELFunctions, MFEELOperators } from '@/constants/MFEEL'

const expressionSchema = z.object({
  expression: z.string().min(1, 'A expressão é obrigatória'),
})

interface ITagSectionItem {
  key: string
  label: string
  required?: boolean
  onClick: () => void
}

interface TagSection {
  label: string
  items: ITagSectionItem[]
}

let editorView: EditorView | null = null

const model = defineModel<{ expression: string }>({ default: { expression: '' }, required: true })

const flowStore = useFlowStore()

const editorRef = ref<HTMLElement>()
const errors = ref<Record<string, string>>({})

const availableVariables = computed(() => flowStore.getStartNodeVariables)

const validateExpression = (): boolean => {
  try {
    expressionSchema.parse(model.value)
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

const tagSections = computed<TagSection[]>(() => [
  {
    label: 'Variáveis disponíveis:',
    items: availableVariables.value.map((variable: Variable) => ({
      key: variable.displayName,
      label: `${variable.displayName} (${variable.type})`,
      required: variable.required,
      onClick: () => insertVariable(variable.displayName),
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
  {
    label: 'Funções:',
    items: MFEELFunctions.map((MFEELFunction) => ({
      key: MFEELFunction,
      label: `${MFEELFunction}()`,
      onClick: () => insertFunction(MFEELFunction),
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
  const formattedAvailableVariables = availableVariables.value.map((variable: Variable) => ({
    label: variable.displayName,
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
    editorView.dispatch({
      changes: { from: pos, insert: varName },
      selection: { anchor: pos + varName.length },
    })
    editorView.focus()
  }
}

function insertFunction(funcName: string) {
  if (editorView) {
    const pos = editorView.state.selection.main.head
    editorView.dispatch({
      changes: { from: pos, insert: `${funcName}()` },
      selection: { anchor: pos + funcName.length + 1 },
    })
    editorView.focus()
  }
}

function insertOperator(operator: string) {
  if (editorView) {
    const pos = editorView.state.selection.main.head
    const operatorWithSpaces = ` ${operator} `
    editorView.dispatch({
      changes: { from: pos, insert: operatorWithSpaces },
      selection: { anchor: pos + operatorWithSpaces.length },
    })
    editorView.focus()
  }
}

onMounted(() => {
  if (editorRef.value) {
    const startState = EditorState.create({
      doc: model.value.expression || '',
      extensions: [
        javascript(),
        placeholder('Ex: age >= 18 and contains(skills, "python")'),
        autocompletion({
          override: [MFEELCompletions],
          maxRenderedOptions: 20,
        }),
        EditorView.updateListener.of((update) => {
          if (update.docChanged) {
            model.value.expression = update.state.doc.toString()
          }
        }),
        EditorView.domEventHandlers({
          blur: () => {
            validateExpression()
          },
        }),
        EditorView.theme({
          '&': {
            fontSize: '14px',
          },
          '.cm-placeholder': {
            color: 'var(--placeholder-color,#64748b) !important',
            'font-size': '16px',
            'letter-spacing': '0.03em',
            'font-family': 'ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji"',
          },
          '.cm-tooltip-autocomplete': {
            'font-size': '16px',
            border: '1px solid var(--p-surface-300)',
            color: 'var(--p-text-color)',
            background: 'var(--tooltip-autocomplete-bg)',
            padding: '0.375em',
            'box-shadow': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
            'border-radius': '0.375rem',
            'letter-spacing': '0.03em',
            'font-family': 'ui-sans-serif, system-ui, sans-serif, "Apple Color Emoji"',
          },
          '.cm-content': {
            padding: '8px',
            minHeight: '95px',
          },
          '.cm-line span': {
            color: 'var(--cm-line-color,#334155)',
          },
          '.cm-focused': {
            outline: '1px solid #3b82f6',
          },
          '.cm-tooltip-autocomplete ul li[aria-selected]': {
            background: 'var(--cm-ac-selected-bg, #6fd4b3)',
            'border-radius': '0.2rem',
            color: 'var(--cm-ac-selected-color, #1e293b)',
          },
          '.cm-tooltip-autocomplete ul li div:first-child': {
            display: 'none',
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
  () => model.value.expression,
  (newValue) => {
    if (editorView && newValue !== editorView.state.doc.toString()) {
      const currentPos = editorView.state.selection.main.head
      const currentLength = editorView.state.doc.length
      const newLength = newValue?.length || 0

      const newPos = newLength > 0 ? Math.min(currentPos, newLength) : 0

      editorView.dispatch({
        changes: {
          from: 0,
          to: currentLength,
          insert: newValue || '',
        },
        selection: { anchor: newPos },
      })
    }
  },
)

defineExpose({
  validateExpression,
})
</script>

<style scoped>
:deep(.cm-editor) {
  border: 1px solid var(--p-surface-300);
  border-radius: 0.375rem;
  outline: none;

  &:focus-within {
    border-color: var(--p-emerald-500) !important;
  }

  &:hover {
    border-color: var(--p-emerald-500);
  }
}

:deep(.p-tag) {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
}

:deep(.dark .cm-tooltip-autocomplete) {
  border: 1px solid var(--p-surface-600);
  color: var(--p-surface-0);
  box-shadow:
    0 4px 6px -1px rgba(0 0 0 / 0.4),
    0 2px 4px -2px rgba(0 0 0 / 0.4);
}

:deep(.dark .cm-tooltip-autocomplete ul) {
  background: var(--p-neutral-800);
}

:deep(.dark .cm-tooltip-autocomplete ul li[aria-selected]) {
  background: var(--p-emerald-500);
  color: var(--p-surface-0);
}

:deep(.dark .cm-line span) {
  color: var(--p-surface-100);
}

:deep(.dark .cm-placeholder) {
  color: #94a3b8 !important; /* Tailwind slate-400 for better contrast */
}
</style>
