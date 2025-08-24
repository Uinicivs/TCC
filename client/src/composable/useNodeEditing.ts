import { ref, reactive, computed } from 'vue'

import type { INode, IMappedNodes } from '@/interfaces/node'

import { useFlowStore } from '@/stores/flow'

import { nodes } from '@/constants/nodes'

export function useNodeEditing(nodeId: string) {
  const flowStore = useFlowStore()

  const steps = {
    setupTitle: 1,
    setupNode: 2,
  }

  const visible = ref(false)
  const currentStep = ref<number>(steps.setupTitle)
  const selectedNode = ref<IMappedNodes | null>(null)

  const currentNode = computed(() => flowStore.getNodeById(nodeId))

  const nodeData = reactive<INode>({
    title: '',
    description: '',
    settings: {},
    parent: null,
    children: [],
  })

  const reset = () => {
    currentStep.value = steps.setupTitle

    if (currentNode.value) {
      const node = currentNode.value
      const nodeType = node.type as keyof typeof nodes

      selectedNode.value = nodes[nodeType]

      Object.assign(nodeData, {
        title: node.data.title || '',
        description: node.data.description || '',
        settings: node.data.settings || {},
        parent: node.data.parent || null,
        children: node.data.children || [],
      })
    }
  }

  const toggleEditNodeDialog = () => {
    visible.value = !visible.value
    if (visible.value) reset()
  }

  const openEditDialog = () => {
    visible.value = true
    reset()
  }

  const handleStepNavigation = {
    next: () => {
      if (currentStep.value >= steps.setupNode) return
      currentStep.value++
    },
    previous: () => {
      if (currentStep.value <= steps.setupTitle) return
      currentStep.value--
    },
    goTo: (stepNumber: number) => {
      if (stepNumber === steps.setupTitle) {
        currentStep.value = steps.setupTitle
        return
      }

      if (stepNumber === steps.setupNode && !hasNodeLabelFilled.value) {
        return
      }

      currentStep.value = stepNumber
    },
  }

  const handleUpdateNode = () => {
    if (!selectedNode.value || !nodeData.title.trim()) return

    const formattedNodeData = JSON.parse(JSON.stringify(nodeData))
    flowStore.updateNode(nodeId, { data: formattedNodeData })
    toggleEditNodeDialog()
  }

  const handleConfigData = (settingsData: INode['settings']) => {
    nodeData.settings = settingsData
  }

  const hasNodeLabelFilled = computed(() => nodeData.title?.trim().length > 0)
  const shouldShowConfigStep = computed(() => !!selectedNode.value?.configComponent)
  const getDialogHeader = computed<string>(() => {
    switch (currentStep.value) {
      case steps.setupTitle:
        return `Editar ${selectedNode.value?.name}`
      case steps.setupNode:
        return `Revisar ${selectedNode.value?.name}`
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
    hasNodeLabelFilled,
    shouldShowConfigStep,
    getDialogHeader,
    toggleEditNodeDialog,
    openEditDialog,
    handleStepNavigation,
    handleUpdateNode,
    handleConfigData,
    reset,
  }
}
