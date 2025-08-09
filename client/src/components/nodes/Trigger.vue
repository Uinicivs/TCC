<script setup lang="ts">
import type { NodeProps } from '@vue-flow/core'
import { Position } from '@vue-flow/core'

defineProps<NodeProps>()
</script>

<template>
  <div>
    <Handle type="target" :position="Position.Top" />
    <div
      class="bg-white p-4 border rounded-md border-gray-300 dark:bg-neutral-950 dark:border-neutral-900 flex gap-4"
    >
      <i
        class="pi pi-bolt bg-white p-4 border rounded-sm border-gray-300 text-emerald-500 dark:bg-neutral-900 dark:border-neutral-800"
        style="font-size: 1.3em"
      />

      <div class="w-[200px]">
        <h4 class="text-lg font-semibold">Trigger</h4>
        <p class="truncate">Lorem ipsum dolor sit asdasdasd.</p>
      </div>
    </div>
    <Handle type="source" :position="Position.Bottom" />
  </div>
</template>
