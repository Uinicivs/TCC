import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Node, Edge } from '@vue-flow/core'

export const useFlowStore = defineStore('flow', () => {
  const nodes = ref<Node[]>([])

  const edges = ref<Edge[]>([])

  const getNodeById = (node: Node) => {
    return nodes.value.find(({ id }) => id === node.id)
  }

  const getEdgeById = (edge: Edge) => {
    return edges.value.find(({ id }) => id === edge.id)
  }

  const addNodes = (newNode: Node) => {
    if (!getNodeById(newNode)) {
      nodes.value.push(newNode)
    }
  }

  const addEdges = (newEdge: Edge) => {
    if (!getEdgeById(newEdge)) {
      edges.value.push(newEdge)
    }
  }

  const removeNode = (node: Node) => {
    const nodeIndex = nodes.value.findIndex(({ id }) => id === node.id)
    if (nodeIndex === -1) return

    nodes.value.splice(nodeIndex, 1)
    edges.value = edges.value.filter((edge) => edge.source !== node.id && edge.target !== node.id)
  }

  return { nodes, edges, addNodes, addEdges, removeNode }
})
