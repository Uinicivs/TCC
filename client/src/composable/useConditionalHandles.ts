import { computed } from 'vue'
import type { Edge } from '@vue-flow/core'
import { useFlowStore } from '@/stores/flow'

export const useConditionalHandles = (id?: string) => {
  const isConditionalNode = computed<boolean>(() => {
    if (!id) return false

    const flowStore = useFlowStore()
    const currentNode = flowStore.getNodeById(id)
    return currentNode?.type === 'conditional'
  })

  const checkHandleConnection = (handleId: string) => {
    if (!id || !isConditionalNode.value) return false

    const flowStore = useFlowStore()
    const { edges } = flowStore

    return edges.some((edge: Edge) => edge.source === id && edge.sourceHandle === handleId)
  }

  const hasLeftConnection = computed(() => checkHandleConnection('conditional-left'))
  const hasRightConnection = computed(() => checkHandleConnection('conditional-right'))
  const canAddToLeftPath = computed(() => isConditionalNode.value && !hasLeftConnection.value)
  const canAddToRightPath = computed(() => isConditionalNode.value && !hasRightConnection.value)

  return {
    isConditionalNode,
    hasLeftConnection,
    hasRightConnection,
    canAddToLeftPath,
    canAddToRightPath,
  }
}
