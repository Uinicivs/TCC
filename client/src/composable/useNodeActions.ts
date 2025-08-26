import { computed } from 'vue'
import type { Node } from '@vue-flow/core'

import { useFlowStore } from '@/stores/flow'

export const useNodeActions = (id?: string) => {
  const flowStore = useFlowStore()
  const { getLastNodes, getNodeById } = flowStore

  const canAddNewNode = computed<boolean>(() => {
    if (!id) return false

    let currentNode: Node | null = null
    const lastNodes = getLastNodes()

    if (id) {
      currentNode = getNodeById(id) ?? null
    }

    const isLastNode = lastNodes.some((node: Node) => node.id === id)
    const currentNodeType = currentNode?.type || ''
    const isEndNode = ['end'].includes(currentNodeType)
    const couldHaveMoreWays = ['conditional'].includes(currentNodeType)

    return !isEndNode && (isLastNode || couldHaveMoreWays)
  })

  return { canAddNewNode }
}
