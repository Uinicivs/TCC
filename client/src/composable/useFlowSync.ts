import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import { debounce, isEqual, cloneDeep } from 'lodash'
import type { Node } from '@vue-flow/core'

import { updateFlowNodes } from '@/services/flowService'

import { mapFlowToSchema } from '@/utils/flowFormatters'

export function useFlowSync(flowId: string, delay = 3000) {
  const previousNodes = ref<Node[]>([])
  const isUpdating = ref(false)
  const toast = useToast()
  const TOAST_GROUP = 'flow-saving'

  const applyUpdate = debounce(async (nodes: Node[]) => {
    if (!flowId) {
      toast.removeGroup(TOAST_GROUP)
      isUpdating.value = false
      return
    }

    if (isEqual(previousNodes.value, nodes)) {
      toast.removeGroup(TOAST_GROUP)
      isUpdating.value = false
      return
    }

    try {
      setInitialNodes(nodes)
      await updateFlowNodes(flowId, mapFlowToSchema(nodes))
    } finally {
      toast.removeGroup(TOAST_GROUP)
      toast.add({ severity: 'success', summary: 'Salvo!', life: 1200, closable: false })
      isUpdating.value = false
    }
  }, delay)

  const updateNodes = async (nodes: Node[]) => {
    isUpdating.value = true
    await applyUpdate(nodes)
  }

  const saveNow = async (nodes: Node[]): Promise<boolean> => {
    if (!flowId) return false
    if (isEqual(previousNodes.value, nodes)) return false

    applyUpdate.cancel()
    isUpdating.value = true

    try {
      setInitialNodes(nodes)
      await updateFlowNodes(flowId, mapFlowToSchema(nodes))
      toast.removeGroup(TOAST_GROUP)
      toast.add({ severity: 'success', summary: 'Salvo!', life: 1200, closable: false })
      return true
    } catch (error) {
      toast.add({
        severity: 'error',
        summary: 'Erro ao salvar',
        detail: error instanceof Error ? error.message : 'Erro desconhecido',
        life: 3000,
      })
      return false
    } finally {
      isUpdating.value = false
    }
  }

  const cancelPendingUpdates = () => {
    applyUpdate.cancel()
  }

  const setInitialNodes = (nodes: Node[]) => {
    previousNodes.value = cloneDeep(nodes)
  }

  return {
    updateNodes,
    saveNow,
    cancelPendingUpdates,
    setInitialNodes,
    isUpdating,
  }
}
