import { ref, reactive, computed } from 'vue'
import type { Node } from '@vue-flow/core'

import type { INode, IMappedNodes } from '@/interfaces/node'

import { useFlowStore } from '@/stores/flow'
import { getDefaultNodeTitle, EXCLUDED_NODE_TYPES } from '@/constants/nodeConfig'
import { nodes } from '@/constants/nodes'

export function useNodeCreation(parentId: INode['parent'], handleId?: string) {
  const flowStore = useFlowStore()

  const initialNodeState = {
    title: '',
    parent: null,
  }

  const steps = {
    chooseNode: 1,
    setupTitle: 2,
    setupNode: 3,
  }

  const visible = ref(false)
  const currentStep = ref<number>(steps.chooseNode)
  const selectedNode = ref<IMappedNodes | null>(null)

  const nodeData = reactive<INode>(Object.assign({}, initialNodeState))

  const reset = () => {
    currentStep.value = steps.chooseNode
    selectedNode.value = null

    Object.keys(nodeData).forEach((key) => {
      delete nodeData[key as keyof typeof nodeData]
    })

    Object.assign(nodeData, JSON.parse(JSON.stringify(initialNodeState)))
  }

  const toggleCreateNodeDialog = () => {
    visible.value = !visible.value
    if (visible.value) reset()
  }

  const handleNodeSelect = (node: IMappedNodes) => {
    selectedNode.value = node
    currentStep.value = steps.setupTitle

    const defaultTitle = getDefaultNodeTitle(node.type)
    if (defaultTitle) {
      nodeData.title = defaultTitle
    }
  }

  const handleStepNavigation = {
    next: () => {
      if (currentStep.value >= steps.setupNode) return
      currentStep.value++
    },
    previous: () => {
      if (currentStep.value <= steps.chooseNode) return
      currentStep.value--
    },
    goTo: (stepNumber: number) => {
      if (stepNumber === steps.chooseNode) {
        currentStep.value = steps.chooseNode
        return
      }

      if (stepNumber === steps.setupTitle && !hasNodeTypeSelected.value) return
      if (
        stepNumber === steps.setupNode &&
        (!hasNodeTypeSelected.value || !hasNodeLabelFilled.value)
      ) {
        return
      }

      currentStep.value = stepNumber
    },
  }

  const handleCreateNode = () => {
    if (!selectedNode.value || !nodeData.title.trim()) return

    let positionX = window.innerWidth / 2 - 150
    let positionY = 0

    const parentNode = parentId && flowStore.getNodeById(parentId)

    if (parentNode) {
      const siblings = flowStore.nodes.filter((node) => node.data?.parent === parentId)
      const hasNoChildren = siblings.length === 0

      if (hasNoChildren) {
        positionX = parentNode.position.x
      }

      if (!hasNoChildren) {
        const minDistance = 300
        const randomVariation = Math.random() * 100
        const baseOffset = siblings.length * 100
        const offsetX = minDistance + baseOffset + randomVariation

        positionX = parentNode.position.x + offsetX
      }

      positionY = parentNode.position.y + 200

      if (handleId) {
        if (handleId === 'conditional-left') {
          positionX = parentNode.position.x - 300
        }

        if (handleId === 'conditional-right') {
          positionX = parentNode.position.x + 300
        }
      }
    }

    if (!parentNode) {
      const [{ position: lastNodePosition } = {}] = flowStore.nodes.slice(-1)
      positionY = (lastNodePosition?.y ?? 0) + 200
    }

    const formattedNodeData = JSON.parse(JSON.stringify(nodeData))
    formattedNodeData.parent = parentId ?? null

    const formatNode: Node = {
      id: Date.now().toString(),
      position: { x: positionX, y: positionY },
      type: selectedNode.value.type,
      data: formattedNodeData,
    }

    if (!(handleId && parentId)) {
      flowStore.addNodes({ ...formatNode })
    }

    if (handleId && parentId) {
      flowStore.addNodes({ ...formatNode }, true)
      flowStore.addEdgeWithHandle({
        id: `${parentId}-${formatNode.id}-${handleId}`,
        source: parentId,
        target: formatNode.id,
        sourceHandle: handleId,
      })
    }

    toggleCreateNodeDialog()
  }

  const handleConfigData = (settingsData: INode['settings']) => {
    nodeData.settings = settingsData
  }

  const hasNodeTypeSelected = computed(() => selectedNode.value !== null)
  const hasNodeLabelFilled = computed(() => nodeData.title?.trim().length > 0)
  const shouldShowConfigStep = computed(() => !!selectedNode.value?.configComponent)
  const availableNodeTypes = computed(() => {
    return Object.values(nodes).filter((node) => !EXCLUDED_NODE_TYPES.includes(node.type))
  })
  const getDialogHeader = computed<string>(() => {
    switch (currentStep.value) {
      case steps.chooseNode:
        return 'Escolha o tipo do nó'
      case steps.setupTitle:
        return `Configurar ${selectedNode.value?.name}`
      case steps.setupNode:
        return `Configurar ${selectedNode.value?.name}`
      default:
        return ''
    }
  })

  return {
    steps,
    visible,
    currentStep,
    selectedNode,
    nodeData,
    hasNodeTypeSelected,
    hasNodeLabelFilled,
    shouldShowConfigStep,
    getDialogHeader,
    availableNodeTypes,
    toggleCreateNodeDialog,
    handleNodeSelect,
    handleStepNavigation,
    handleCreateNode,
    handleConfigData,
    reset,
  }
}
