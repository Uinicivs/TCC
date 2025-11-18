<template>
  <Toast position="bottom-right" />
  <DynamicDialog />
  <div class="h-screen">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { Toast, DynamicDialog } from 'primevue'
</script>
