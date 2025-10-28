import { ref, computed, watch } from 'vue'
import { defineStore } from 'pinia'
import type { Node, Edge } from '@vue-flow/core'
import type { Variable } from '@/interfaces/variables'
import { useFlowSync } from '@/composable/useFlowSync'

type TStrokeColor = 'success' | 'error' | 'warning' | 'info'

const strokeColorMap: Record<TStrokeColor, string> = {
  success: 'var(--p-emerald-500)',
  error: 'var(--p-red-500)',
  warning: 'var(--p-amber-500)',
  info: 'var(--p-blue-500)',
}

export const useFlowStore = defineStore('flow', () => {
  let flowSyncInstance: ReturnType<typeof useFlowSync> | null = null
  const nodes = ref<Node[]>([])
  const edges = ref<Edge[]>([])
  const currentFlowId = ref<string | null>(null)

  const initializeDebounce = (flowId: string) => {
    flowSyncInstance = useFlowSync(flowId)
  }

  watch(
    nodes,
    async (newNodes) => {
      if (currentFlowId.value && flowSyncInstance) {
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
  }

  const highlightPathFromNode = (nodeId: string, strokeType: TStrokeColor = 'success') => {
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

    const strokeColor = strokeColorMap[strokeType] ?? strokeColorMap.success

    for (let index = 0; index < pathNodes.length - 1; index++) {
      const sourceId = pathNodes[index]
      const targetId = pathNodes[index + 1]
      const edge = edges.value.find(
        ({ target, source }) => source === sourceId && target === targetId,
      )

      if (edge) {
        edge.animated = true
        edge.style = {
          stroke: strokeColor,
          strokeWidth: 2,
        }
      }
    }
  }

  return {
    nodes,
    edges,
    currentFlowId,
    getNodeById,
    getLastNodes,
    getFirstNode,
    getStartNodeVariables,
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
  }
})
