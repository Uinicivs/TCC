import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Node, Edge } from '@vue-flow/core'

export const useFlowStore = defineStore('flow', () => {
  const nodes = ref<Node[]>([
    {
      id: '1755980546232',
      position: {
        x: 302.5,
        y: 200,
      },
      type: 'start',
      data: { title: 'teste', parent: null, children: ['1755980553131'] },
    },

    {
      id: '1755980553131',
      position: {
        x: 302.5,
        y: 400,
      },
      type: 'conditional',
      data: { title: 'teste', parent: '1755980546232' },
    },
  ])
  const edges = ref<Edge[]>([
    {
      id: '1755980546232-1755980553131',
      source: '1755980546232',
      target: '1755980553131',
    },
  ])

  const getNodeById = (nodeId: Node['id']): Node | undefined => {
    return nodes.value.find(({ id }) => id === nodeId)
  }

  const getEdgeById = (edgeId: Edge['id']) => {
    return edges.value.find(({ id }) => id === edgeId)
  }

  const addNodes = (newNode: Node, skipEdgeCreation = false) => {
    if (getNodeById(newNode.id)) return

    const {
      data: { parent: parentId },
    } = newNode

    if (!parentId) {
      nodes.value.push(newNode)
      return
    }

    const parentIndex = nodes.value.findIndex((node) => node.id === parentId)

    if (parentIndex !== -1) {
      nodes.value.splice(parentIndex + 1, 0, newNode)
    }

    if (parentIndex === -1) {
      nodes.value.push(newNode)
    }

    if (!skipEdgeCreation) {
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

  const getLastNodes = (): Array<Node> => {
    return nodes.value.filter(({ data }) => !data.children)
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

  const addEdgeWithHandle = (newEdge: Edge & { sourceHandle?: string }) => {
    const existingEdgeWithHandle = edges.value.find(
      (edge) => edge.source === newEdge.source && edge.sourceHandle === newEdge.sourceHandle,
    )

    if (existingEdgeWithHandle) return

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
    getNodeById,
    getLastNodes,
    addNodes,
    removeNode,
    updateNode,
    setNodes,
    addEdgeWithHandle,
  }
})
