import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import type { Node, Edge } from '@vue-flow/core'
import type { Variable } from '@/interfaces/variables'
import { useFlowSync } from '@/composable/useFlowSync'
import type { TestFlowReduction, TestFlowCase } from '@/interfaces/testFlow'

type TStrokeColor = 'success' | 'error' | 'warning' | 'info' | 'none'

const strokeColorMap: Record<Exclude<TStrokeColor, 'none'>, string> = {
  success: 'var(--p-emerald-500)',
  error: 'var(--p-red-500)',
  warning: 'var(--p-amber-500)',
  info: 'var(--p-blue-500)',
}

export const useFlowStore = defineStore('flow', () => {
  let flowSyncInstance: ReturnType<typeof useFlowSync> | null = null
  let testResetCallback: (() => void) | null = null

  const nodes = ref<Node[]>([])
  const edges = ref<Edge[]>([])
  const currentFlowId = ref<string | null>(null)
  const reductionWarningsByNodeId = ref<Record<string, string>>({})
  const edgeHighlightFlags = ref<Record<string, { reachable?: boolean; unreachable?: boolean }>>({})
  const testCases = ref<TestFlowCase[]>([])
  const isInitialLoad = ref(true)

  const initializeDebounce = (flowId: string) => {
    flowSyncInstance = useFlowSync(flowId)
  }

  watch(
    nodes,
    async (newNodes) => {
      if (isInitialLoad.value) {
        isInitialLoad.value = false
        return
      }

      if (currentFlowId.value && flowSyncInstance) {
        resetTestState()
        await flowSyncInstance.updateNodes(newNodes)
      }
    },
    { deep: true },
  )

  const getNodeById = (nodeId: Node['id']): Node | undefined => {
    return nodes.value.find(({ id }) => id === nodeId)
  }

  const getEdgeById = (edgeId: Edge['id']) => {
    return edges.value.find(({ id }) => id === edgeId)
  }

  const addNodes = (newNode: Node) => {
    if (getNodeById(newNode.id)) return

    const {
      data: { parent: parentId },
    } = newNode

    if (!parentId) {
      nodes.value.push(newNode)
    } else {
      const parentIndex = nodes.value.findIndex((node) => node.id === parentId)

      if (parentIndex !== -1) {
        nodes.value.splice(parentIndex + 1, 0, newNode)
      } else {
        nodes.value.push(newNode)
      }
    }
  }

  const updateNode = (nodeId: Node['id'], override: Partial<Node>) => {
    const nodeIndex = nodes.value.findIndex(({ id }) => id === nodeId)
    if (nodeIndex === -1) return
    const currentNode = nodes.value[nodeIndex]
    const updatedNode = { ...currentNode, ...override }
    nodes.value.splice(nodeIndex, 1, updatedNode)
    nodes.value = [...nodes.value]
  }

  const setNodes = (newNodes: Node[]) => {
    nodes.value = newNodes
    setEdges()

    if (currentFlowId.value && flowSyncInstance) {
      flowSyncInstance.setInitialNodes(newNodes)
    }
  }

  const setEdges = () => {
    edges.value = []
    nodes.value.forEach((node) => {
      if (node.data.parent) {
        const parentNode = getNodeById(node.data.parent)
        const source = node.data.parent
        const target = node.id
        const id = buildEdgeId(node)

        if (getEdgeById(id)) {
          return
        }

        const existingEdgeWithTarget = edges.value.find((edge) => edge.target === target)
        if (existingEdgeWithTarget) {
          return
        }

        if (parentNode && parentNode.type === 'conditional') {
          const sourceHandle =
            node.data.isFalseCase === true ? 'conditional-right' : 'conditional-left'

          addEdgeWithHandle({
            id,
            source,
            target,
            sourceHandle,
          })
          return
        }

        addEdges({
          id,
          source,
          target,
        })
      }
    })
  }

  const getLastNodes = (): Array<Node> => {
    return nodes.value.filter(({ data }) => !data.children?.length)
  }

  const getFirstNode = computed((): Node | undefined => {
    return nodes.value.find(({ data }) => data.parent === null)
  })

  const getStartNodeVariables = computed((): Variable[] => {
    const startNode = getFirstNode.value
    return startNode?.data.settings.inputs || []
  })

  const getCaseCountByNodeId = computed((): Record<string, number> => {
    const counts: Record<string, number> = {}
    testCases.value.forEach((testCase) => {
      const nodeId = testCase.endNodeId
      counts[nodeId] = (counts[nodeId] || 0) + 1
    })
    return counts
  })

  const getCasesByNodeId = (nodeId: string): TestFlowCase[] => {
    return testCases.value.filter((testCase) => testCase.endNodeId === nodeId)
  }

  const buildEdgeId = (node: Node): string => {
    return `${node.data.parent}-${node.id}`
  }

  const addEdges = (newEdge: Edge) => {
    if (!getEdgeById(newEdge.id)) {
      edges.value.push({ ...newEdge, type: 'smoothstep' })

      const parentNode = getNodeById(newEdge.source)
      if (parentNode) {
        const currentChildren = parentNode.data.children || []
        if (!currentChildren.includes(newEdge.target)) {
          updateNode(newEdge.source, {
            data: {
              ...parentNode.data,
              children: [...currentChildren, newEdge.target],
            },
          })
        }
      }
    }
  }

  const addEdgeWithHandle = (newEdge: Edge & { sourceHandle?: string }) => {
    const existingEdgeWithHandle = edges.value.find(
      (edge) => edge.source === newEdge.source && edge.sourceHandle === newEdge.sourceHandle,
    )

    if (existingEdgeWithHandle) return

    if (!getEdgeById(newEdge.id)) {
      edges.value.push({ ...newEdge, type: 'smoothstep' })

      const parentNode = getNodeById(newEdge.source)
      if (parentNode) {
        const currentChildren = parentNode.data.children || []

        if (!currentChildren.includes(newEdge.target)) {
          updateNode(newEdge.source, {
            data: {
              ...parentNode.data,
              children: [...currentChildren, newEdge.target],
            },
          })
        }
      }
    }
  }

  const removeNode = (node: Node) => {
    const nodeIndex = nodes.value.findIndex(({ id }) => id === node.id)
    if (nodeIndex === -1) return

    if (node.data.children?.length) {
      node.data.children.forEach((childId: string) => {
        const childNode = getNodeById(childId)
        if (childNode) {
          removeNode(childNode)
        }
      })
    }

    const parentNode = getNodeById(node.data.parent)
    if (parentNode && parentNode.data.children) {
      const updatedChildren = parentNode.data.children.filter(
        (childId: string) => childId !== node.id,
      )
      updateNode(node.data.parent, {
        data: {
          ...parentNode.data,
          children: updatedChildren,
        },
      })
    }

    nodes.value.splice(nodeIndex, 1)
    edges.value = edges.value.filter((edge) => edge.source !== node.id && edge.target !== node.id)
  }

  const setFlowId = (flowId: string | null) => {
    currentFlowId.value = flowId
    if (!flowId) {
      flowSyncInstance = null
      return
    }

    initializeDebounce(flowId)
  }

  const clearFlow = () => {
    if (flowSyncInstance) {
      flowSyncInstance.cancelPendingUpdates()
    }
    nodes.value = []
    edges.value = []
    currentFlowId.value = null
    reductionWarningsByNodeId.value = {}
    testCases.value = []
    isInitialLoad.value = true
  }

  const highlightPathFromNode = (
    nodeId: string,
    strokeType: TStrokeColor = 'success',
    source?: 'reachable' | 'unreachable',
  ) => {
    const node = getNodeById(nodeId)
    if (!node) return

    const pathNodes: string[] = [nodeId]
    let currentNode = node

    while (currentNode.data.parent !== null) {
      const parentId = currentNode.data.parent
      pathNodes.unshift(parentId)
      const parentNode = getNodeById(parentId)

      if (!parentNode) break

      currentNode = parentNode
    }

    const updatedEdges: Edge[] = edges.value.map((currentEdge) => {
      for (let index = 0; index < pathNodes.length - 1; index++) {
        const sourceId = pathNodes[index]
        const targetId = pathNodes[index + 1]
        const isMatching = currentEdge.source === sourceId && currentEdge.target === targetId
        if (isMatching) {
          const edgeId = currentEdge.id
          const flags = edgeHighlightFlags.value[edgeId] || {}

          if (strokeType === 'none' && source) {
            if (source === 'reachable') flags.reachable = false
            if (source === 'unreachable') flags.unreachable = false
          } else {
            const inferredSource: 'reachable' | 'unreachable' | undefined = source
              ? source
              : strokeType === 'error'
                ? 'unreachable'
                : 'reachable'
            if (inferredSource === 'reachable') flags.reachable = true
            if (inferredSource === 'unreachable') flags.unreachable = true
          }

          edgeHighlightFlags.value[edgeId] = flags

          const hasUnreachable = flags.unreachable === true
          const hasReachable = flags.reachable === true

          if (!hasUnreachable && !hasReachable) {
            return {
              ...currentEdge,
              animated: false,
              style: undefined,
            }
          }

          const finalStroke = hasUnreachable ? strokeColorMap.error : strokeColorMap.success

          return {
            ...currentEdge,
            animated: true,
            style: {
              ...currentEdge.style,
              stroke: finalStroke,
              strokeWidth: 2,
            },
          }
        }
      }
      return currentEdge
    })

    edges.value = updatedEdges
  }

  const getWarningForNodeId = (nodeId: string): string | null => {
    return reductionWarningsByNodeId.value[nodeId] ?? null
  }

  const setReductionWarnings = (reductions: TestFlowReduction[]) => {
    const messagesByNode: Record<string, string> = {}

    reductions?.forEach((reduction) => {
      const { nodeId, original, simplified, removedParts } = reduction

      let message = ''

      if ((simplified === 'true' || simplified === 'false') && removedParts?.length) {
        message = `A expressão "${removedParts.join(', ')}" é redundante.`
      }

      if (simplified && simplified.length && simplified !== 'true' && simplified !== 'false') {
        message = `A expressão "${original}" pode ser simplificada apenas por "${simplified}".`
      }

      if (removedParts?.length) {
        message += `\nPartes sugeridas para remoção: ${removedParts.join(', ')}.`
      }

      messagesByNode[nodeId] = message
    })

    reductionWarningsByNodeId.value = messagesByNode
  }

  const setTestCases = (cases: TestFlowCase[]) => {
    testCases.value = cases || []
  }

  const resetTestState = () => {
    testCases.value = []
    reductionWarningsByNodeId.value = {}
    edgeHighlightFlags.value = {}
    edges.value = edges.value.map((edge) => ({
      ...edge,
      animated: false,
      style: undefined,
    }))

    if (testResetCallback) {
      testResetCallback()
    }
  }

  const setTestResetHandler = (callback: () => void) => {
    testResetCallback = callback
  }

  return {
    nodes,
    edges,
    currentFlowId,
    getNodeById,
    getLastNodes,
    getFirstNode,
    getStartNodeVariables,
    getCaseCountByNodeId,
    getCasesByNodeId,
    addNodes,
    removeNode,
    updateNode,
    setNodes,
    setEdges,
    addEdges,
    addEdgeWithHandle,
    setFlowId,
    clearFlow,
    highlightPathFromNode,
    setReductionWarnings,
    setTestCases,
    getWarningForNodeId,
    resetTestState,
    setTestResetHandler,
  }
})
