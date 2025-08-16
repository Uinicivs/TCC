import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Node, Edge } from '@vue-flow/core'

export const useFlowStore = defineStore('flow', () => {
  const nodes = ref<Node[]>([])
  const edges = ref<Edge[]>([])

  const getNodeById = (nodeId: Node['id']) => {
    return nodes.value.find(({ id }) => id === nodeId)
  }

  const getEdgeById = (edgeId: Edge['id']) => {
    return edges.value.find(({ id }) => id === edgeId)
  }

  const addNodes = (newNode: Node) => {
    if (getNodeById(newNode.id)) return
    nodes.value.push(newNode)
    const {
      data: { parent: parentId },
    } = newNode

    if (parentId) {
      addEdges({
        id: buildEdgeId(newNode),
        source: parentId,
        target: newNode.id,
      })
    }
  }

  const updateNode = (nodeId: Node['id'], override: Partial<Node>) => {
    const nodeIndex = nodes.value.findIndex(({ id }) => id === nodeId)
    if (nodeIndex === -1) return

    nodes.value[nodeIndex] = { ...nodes.value[nodeIndex], ...override }
  }

  const setNodes = (newNodes: Node[]) => {
    nodes.value = newNodes
    setEdges()
  }

  const setEdges = () => {
    nodes.value.forEach((node) => {
      if (node.data.parent) {
        addEdges({
          id: buildEdgeId(node),
          source: node.data.parent,
          target: node.id,
        })
      }
    })
  }

  const getLastNode = (): Node => {
    const [lastNode] = nodes.value.slice(-1)

    return lastNode
  }

  const buildEdgeId = (node: Node): string => {
    return `${node.data.parent}-${node.id}`
  }

  const addEdges = (newEdge: Edge) => {
    if (!getEdgeById(newEdge.id)) {
      edges.value.push(newEdge)

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

  return {
    nodes,
    edges,
    getLastNode,
    addNodes,
    removeNode,
    updateNode,
    setNodes,
  }
})
