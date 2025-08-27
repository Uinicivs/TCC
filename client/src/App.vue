<template>
  <Toast />
  <Menubar v-if="showMenu" :model="items" class="fixed w-full z-10" />
  <div class="h-screen">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Menubar, Toast } from 'primevue'

const route = useRoute()

const items = ref([
  {
    label: 'Home',
    icon: 'pi pi-home',
  },
])

const showMenu = computed<boolean>(() => route.name !== 'flow-show')
</script>
