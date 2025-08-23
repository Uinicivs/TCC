<script setup lang="ts">
import { reactive } from 'vue'
import { Position } from '@vue-flow/core'
import { NodeToolbar } from '@vue-flow/node-toolbar'
import { Button, type ButtonProps } from 'primevue'

import { useFlowStore } from '@/stores/flow'

const props = defineProps<{
  position?: Position
  offset?: number
  isVisible?: boolean
  nodeId: string
}>()

const flowStore = useFlowStore()

const toolbarPosition = props.position ?? Position.Right
const toolbarOffset = props.offset ?? 35

const getButtonPosition = (index: number, total: number) => {
  const angleStep = 180
  const angle = (index * angleStep - 90) * (Math.PI / 180)
  const radius = 40

  return {
    x: Math.cos(angle) * radius,
    y: Math.sin(angle) * radius,
    delay: index * 100,
  }
}

const actions = reactive<Array<{ callAction?: VoidFunction } & ButtonProps>>([
  {
    icon: 'pi pi-trash',
    rounded: true,
    variant: 'outlined',
    size: 'small',
    severity: 'danger',
    callAction: () => {
      const currentNode = flowStore.getNodeById(props.nodeId)
      if (!currentNode) return

      flowStore.removeNode(currentNode)
    },
  },
])
</script>

<template>
  <NodeToolbar
    :offset="toolbarOffset"
    :position="toolbarPosition"
    class="radial-toolbar"
    :is-visible="isVisible"
  >
    <div class="radial-container">
      <template v-for="(action, index) in actions" :key="index">
        <div
          class="radial-button-wrapper"
          :style="{
            '--delay': `${getButtonPosition(index, actions.length).delay}ms`,
            '--x': `${getButtonPosition(index, actions.length).x}px`,
            '--y': `${getButtonPosition(index, actions.length).y}px`,
          }"
        >
          <Button v-bind="action" class="radial-button" @click="action.callAction" />
        </div>
      </template>
    </div>
  </NodeToolbar>
</template>

<style scoped>
.radial-toolbar {
  position: relative;
}

.radial-container {
  position: relative;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.radial-button-wrapper {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation: slideIn 0.2s ease-out forwards;
  animation-delay: var(--delay);
  opacity: 0;
}

.radial-button {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  transform: scale(1);
}

.radial-button:hover {
  transform: scale(1.1);
}

@keyframes slideIn {
  0% {
    opacity: 0;
    transform: translate(-50%, -50%) scale(0.5);
  }
  100% {
    opacity: 1;
    transform: translate(calc(-50% + var(--x)), calc(-50% + var(--y))) scale(1);
  }
}

.radial-button-wrapper {
  transform: translate(calc(-50% + var(--x)), calc(-50% + var(--y)));
}
</style>
