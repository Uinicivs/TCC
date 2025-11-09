import { ref, reactive, computed } from 'vue'
import type { Edge, Node } from '@vue-flow/core'
import { v4 as uuidv4 } from 'uuid'

import type { INode, IMappedNodes } from '@/interfaces/node'

import { useFlowStore } from '@/stores/flow'

import { nodes } from '@/constants/nodes'
import { getDefaultNodeTitle, EXCLUDED_NODE_TYPES } from '@/constants/nodeConfig'
import {
  HORIZONTAL_SPACING,
  VERTICAL_SPACING,
  SAFETY_MARGIN,
  NODE_WIDTH,
  NODE_HEIGHT,
} from '@/constants/nodeLayout'

export function useNodeCreation(parentId: INode['parent'], handleId?: string) {
  const flowStore = useFlowStore()

  const initialNodeState = {
    title: '',
    settings: {},
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

  const checkCollision = (x: number, y: number, excludeId?: string): boolean => {
    return flowStore.nodes.some((node) => {
      if (excludeId && node.id === excludeId) return false

      const nodeLeft = x - SAFETY_MARGIN
      const nodeRight = x + NODE_WIDTH + SAFETY_MARGIN
      const nodeTop = y - SAFETY_MARGIN
      const nodeBottom = y + NODE_HEIGHT + SAFETY_MARGIN
      const existingLeft = node.position.x - SAFETY_MARGIN
      const existingRight = node.position.x + NODE_WIDTH + SAFETY_MARGIN
      const existingTop = node.position.y - SAFETY_MARGIN
      const existingBottom = node.position.y + NODE_HEIGHT + SAFETY_MARGIN

      return !(
        nodeLeft >= existingRight ||
        nodeRight <= existingLeft ||
        nodeTop >= existingBottom ||
        nodeBottom <= existingTop
      )
    })
  }

  const findFreePosition = (
    preferredX: number,
    preferredY: number,
    excludeId?: string,
  ): { x: number; y: number } => {
    if (!checkCollision(preferredX, preferredY, excludeId)) {
      return { x: preferredX, y: preferredY }
    }

    const stepSize = SAFETY_MARGIN

    for (let radius = stepSize; radius <= stepSize; radius += stepSize) {
      const positions = [
        { x: preferredX + radius, y: preferredY + radius },
        { x: preferredX - radius, y: preferredY + radius },
        { x: preferredX + radius, y: preferredY - radius },
        { x: preferredX - radius, y: preferredY - radius },
      ]

      for (const position of positions) {
        if (!checkCollision(position.x, position.y, excludeId)) {
          return position
        }
      }
    }

    return {
      x: preferredX,
      y: preferredY,
    }
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

    switch (node.type) {
      case 'start': {
        nodeData.settings = { inputs: [] }
        break
      }
      case 'conditional': {
        nodeData.settings = { expression: '' }
        break
      }
      case 'end': {
        nodeData.settings = { response: false }
        break
      }
      default: {
        nodeData.settings = {}
      }
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

  const createEndNode = (
    parentNodeId: string,
    parentPosition: { x: number; y: number },
    isFalseCase?: boolean,
  ): Node => {
    const endNodeData: INode = {
      title: getDefaultNodeTitle('end'),
      settings: { response: isFalseCase },
      parent: parentNodeId,
      children: [],
      ...(typeof isFalseCase === 'boolean' && { isFalseCase }),
    }

    let positionX = parentPosition.x
    if (typeof isFalseCase === 'boolean') {
      positionX = isFalseCase
        ? parentPosition.x + HORIZONTAL_SPACING
        : parentPosition.x - HORIZONTAL_SPACING
    }

    const endNodePosition = findFreePosition(positionX, parentPosition.y + VERTICAL_SPACING)

    return {
      id: uuidv4(),
      position: endNodePosition,
      type: 'end',
      data: endNodeData,
    }
  }

  const createConditionalEndNodes = (formatNode: Node) => {
    const leftEndNode = createEndNode(
      formatNode.id,
      { x: formatNode.position.x, y: formatNode.position.y },
      false,
    )

    const rightEndNode = createEndNode(
      formatNode.id,
      { x: formatNode.position.x, y: formatNode.position.y },
      true,
    )

    return { leftEndNode, rightEndNode }
  }

  const createMissingConditionalEndNode = (formatNode: Node, existingChild: Node) => {
    const needsEndNodeIsFalseCase = !existingChild.data.isFalseCase

    return createEndNode(
      formatNode.id,
      { x: formatNode.position.x, y: formatNode.position.y },
      needsEndNodeIsFalseCase,
    )
  }

  const addNodesToFlow = (nodes: Node[], parentNode: Node) => {
    const childrenIds = nodes.map((node) => node.id)
    parentNode.data.children = [...(parentNode.data.children || []), ...childrenIds]

    nodes.forEach((node) => flowStore.addNodes(node))
    flowStore.updateNode(parentNode.id, parentNode)
  }

  const handleCreateNode = () => {
    if (!selectedNode.value || !nodeData.title.trim()) return
    let positionX: number = window.innerWidth / 2
    let positionY: number = 0
    let isFalseCase: boolean | undefined = false
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

        positionX =
          parentNode.type !== 'conditional'
            ? parentNode.position.x
            : parentNode.position.x + offsetX
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

    const finalPosition = findFreePosition(positionX, positionY)

    const formatNode: Node = {
      id: uuidv4(),
      position: finalPosition,
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

          childOffsetX += !childNode.data.isFalseCase ? HORIZONTAL_SPACING * -1 : HORIZONTAL_SPACING

          const freePosition = findFreePosition(childOffsetX, childPositionY, childId)

          flowStore.updateNode(childId, {
            ...childNode,
            position: freePosition,
            data: {
              ...childNode.data,
              parent: level === 0 ? formatNode.id : childNode.data.parent,
            },
          })

          if (childNode.data.children?.length > 0) {
            updateDescendantPositions(
              childNode.data.children,
              freePosition.x,
              freePosition.y,
              level + 1,
            )
          }
        }
      })
    }

    if (formattedNodeData.children.length) {
      updateDescendantPositions(
        formattedNodeData.children,
        formatNode.position.x,
        formatNode.position.y,
      )
    }

    const shouldCreateEndNode =
      selectedNode.value.type !== 'end' &&
      (formattedNodeData.children.length === 0 ||
        (selectedNode.value.type === 'conditional' && formattedNodeData.children.length === 1))

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

      flowStore.addNodes({ ...formatNode })
      flowStore.addEdgeWithHandle(edgePayload)
    }

    if (shouldCreateEndNode) {
      if (selectedNode.value.type === 'conditional') {
        if (formattedNodeData.children.length === 0) {
          const { leftEndNode, rightEndNode } = createConditionalEndNodes(formatNode)
          addNodesToFlow([leftEndNode, rightEndNode], formatNode)
        } else if (formattedNodeData.children.length === 1) {
          const existingChild = flowStore.getNodeById(formattedNodeData.children[0])
          if (existingChild) {
            const endNode = createMissingConditionalEndNode(formatNode, existingChild)
            addNodesToFlow([endNode], formatNode)
          }
        }
      } else {
        const endNode = createEndNode(formatNode.id, formatNode.position)
        addNodesToFlow([endNode], formatNode)
      }
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
