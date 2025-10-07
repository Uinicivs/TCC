import { computed } from 'vue'
import type { Node } from '@vue-flow/core'

import { useFlowStore } from '@/stores/flow'

export const useNodeActions = (id?: string) => {
  const { getNodeById } = useFlowStore()

  const canAddNewNode = computed<boolean>(() => {
    if (!id) return false

    let currentNode: Node | null = null

    if (id) {
      currentNode = getNodeById(id) ?? null
    }

    const currentNodeType = currentNode?.type || ''
    const isEndNode = ['end'].includes(currentNodeType)

    return !isEndNode
  })

  return { canAddNewNode }
}
