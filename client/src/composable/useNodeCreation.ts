import { ref, reactive, computed } from 'vue'
import type { Edge, Node } from '@vue-flow/core'
import { v4 as uuidv4 } from 'uuid'

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
      if (currentStep.value >= steps.setupTitle) return
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

      currentStep.value = stepNumber
    },
  }

  const handleCreateNode = () => {
    if (!selectedNode.value || !nodeData.title.trim()) return

    let positionX: number = window.innerWidth / 2 - 150
    let positionY: number = 0
    let isFalseCase: boolean | undefined = undefined

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
          isFalseCase = false
        }

        if (handleId === 'conditional-right') {
          positionX = parentNode.position.x + 300
          isFalseCase = true
        }
      }
    }

    if (!parentNode) {
      const [{ position: lastNodePosition } = {}] = flowStore.nodes.slice(-1)
      positionY = (lastNodePosition?.y ?? 0) + 200
    }

    const formattedNodeData = JSON.parse(JSON.stringify(nodeData))
    formattedNodeData.parent = parentId ?? null

    if (typeof isFalseCase === 'boolean') {
      formattedNodeData.isFalseCase = isFalseCase
    }

    const formatNode: Node = {
      id: uuidv4(),
      position: { x: positionX, y: positionY },
      type: selectedNode.value.type,
      data: formattedNodeData,
    }

    if (!(handleId && parentId)) {
      flowStore.addNodes({ ...formatNode })
    }

    if (handleId && parentId) {
      const edgePayload: Edge & { sourceHandle?: string } = {
        id: `${parentId}-${formatNode.id}-${handleId}`,
        source: parentId,
        target: formatNode.id,
        sourceHandle: handleId,
      }

      if ('isFalseCase' in formattedNodeData) {
        edgePayload.label = isFalseCase ? 'Verdadeiro' : 'Falso'
      }

      flowStore.addNodes({ ...formatNode }, true)
      flowStore.addEdgeWithHandle(edgePayload)
    }

    toggleCreateNodeDialog()
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
    reset,
  }
}
