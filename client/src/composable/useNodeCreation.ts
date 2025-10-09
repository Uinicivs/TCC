import { ref, reactive, computed } from 'vue'
import type { Edge, Node } from '@vue-flow/core'
import { v4 as uuidv4 } from 'uuid'

import type { INode, IMappedNodes } from '@/interfaces/node'

import { useFlowStore } from '@/stores/flow'

import { nodes } from '@/constants/nodes'
import { getDefaultNodeTitle, EXCLUDED_NODE_TYPES } from '@/constants/nodeConfig'
import { HORIZONTAL_SPACING, VERTICAL_SPACING } from '@/constants/nodeLayout'

export function useNodeCreation(parentId: INode['parent'], handleId?: string) {
  const flowStore = useFlowStore()

  const initialNodeState = {
    title: '',
    parent: null,
    children: [],
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

    let positionX: number = window.innerWidth / 2
    let positionY: number = 0
    let isFalseCase: boolean | undefined = undefined
    const formattedNodeData = JSON.parse(JSON.stringify(nodeData))
    const parentNode = parentId && flowStore.getNodeById(parentId)

    if (parentNode) {
      const siblings = parentNode.data.children || []
      const hasNoChildren = siblings.length === 0

      if (hasNoChildren) {
        positionX = parentNode.position.x
      }

      if (!hasNoChildren) {
        const offsetX = HORIZONTAL_SPACING

        if (handleId && (handleId === 'conditional-left' || handleId === 'conditional-right')) {
          const isRightPath = handleId === 'conditional-right'
          const existingChildInPath = parentNode.data.children?.find((childId: string) => {
            const childNode = flowStore.getNodeById(childId)
            return childNode && childNode.data.isFalseCase === isRightPath
          })

          if (existingChildInPath) {
            formattedNodeData.children = [existingChildInPath]
            const updatedParentChildren = parentNode.data.children.filter(
              (childId: string) => childId !== existingChildInPath,
            )

            flowStore.updateNode(parentId, {
              ...parentNode,
              data: {
                ...parentNode.data,
                children: updatedParentChildren,
              },
            })

            const childNode = flowStore.getNodeById(existingChildInPath)
            if (childNode) {
              flowStore.updateNode(existingChildInPath, {
                ...childNode,
                data: {
                  ...childNode.data,
                  parent: null,
                },
              })
            }
          }
        } else {
          formattedNodeData.children = [...parentNode.data.children]
          flowStore.updateNode(parentId, {
            ...parentNode,
            data: {
              ...parentNode.data,
              children: [],
            },
          })

          parentNode.data.children.forEach((childId: string) => {
            const childNode = flowStore.getNodeById(childId)
            if (childNode) {
              flowStore.updateNode(childId, {
                ...childNode,
                data: {
                  ...childNode.data,
                  parent: null,
                },
              })
            }
          })
        }

        positionX = parentNode.position.x + offsetX
      }

      positionY = parentNode.position.y + VERTICAL_SPACING

      if (handleId) {
        if (handleId === 'conditional-left') {
          positionX = parentNode.position.x - HORIZONTAL_SPACING
          isFalseCase = false
        }

        if (handleId === 'conditional-right') {
          positionX = parentNode.position.x + HORIZONTAL_SPACING
          isFalseCase = true
        }
      }
    }

    if (!parentNode) {
      const [{ position: lastNodePosition } = {}] = flowStore.nodes.slice(-1)
      positionY = (lastNodePosition?.y ?? 0) + VERTICAL_SPACING
    }

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

    const updateDescendantPositions = (
      childrenIds: string[],
      baseX: number,
      baseY: number,
      level: number = 0,
    ) => {
      childrenIds.forEach((childId: string) => {
        const childNode = flowStore.getNodeById(childId)
        if (childNode) {
          const childPositionY = baseY + VERTICAL_SPACING
          let childOffsetX = baseX

          if (childNode.type === 'conditional' && 'isFalseCase' in childNode.data) {
            childOffsetX += !childNode.data.isFalseCase
              ? HORIZONTAL_SPACING * -1
              : HORIZONTAL_SPACING
          }

          flowStore.updateNode(childId, {
            ...childNode,
            position: { x: childOffsetX, y: childPositionY },
            data: {
              ...childNode.data,
              parent: level === 0 ? formatNode.id : childNode.data.parent,
            },
          })

          if (childNode.data.children?.length > 0) {
            updateDescendantPositions(
              childNode.data.children,
              childOffsetX,
              childPositionY,
              level + 1,
            )
          }
        }
      })
    }

    if (formattedNodeData.children && formattedNodeData.children.length > 0) {
      updateDescendantPositions(
        formattedNodeData.children,
        formatNode.position.x,
        formatNode.position.y,
      )
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

    flowStore.setEdges()
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
