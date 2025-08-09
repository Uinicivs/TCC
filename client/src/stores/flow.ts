import { ref } from 'vue'
import { defineStore } from 'pinia'
import type { Node, Edge } from '@vue-flow/core'

export const useFlowStore = defineStore('flow', () => {
  const nodes = ref<Node[]>([])
  const edges = ref<Edge[]>([])

  function setGraph(newNodes: Node[], newEdges: Edge[]) {
    nodes.value = newNodes
    edges.value = newEdges
  }

  return { nodes, edges, setGraph }
})
