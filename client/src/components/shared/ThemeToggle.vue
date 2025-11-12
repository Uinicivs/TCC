<template>
  <ToggleButton
    v-model="isDarkMode"
    onIcon="pi pi-moon"
    offIcon="pi pi-sun"
    onLabel=""
    offLabel=""
    class="!p-0 !border-none w-8 h-8"
    @change="toggleTheme"
  />
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ToggleButton } from 'primevue'

const isDarkMode = ref(false)

const applyTheme = (dark: boolean) => {
  const root = document.documentElement
  if (dark) {
    root.classList.add('dark')
  } else {
    root.classList.remove('dark')
  }
}

const toggleTheme = () => {
  applyTheme(isDarkMode.value)
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
}

onMounted(() => {
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme === 'dark') {
    isDarkMode.value = true
    applyTheme(true)
    return
  }

  if (savedTheme === 'light') {
    isDarkMode.value = false
    applyTheme(false)
    return
  }

  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  isDarkMode.value = prefersDark
  applyTheme(prefersDark)
})
</script>

<style scoped>
:deep(.p-togglebutton-label) {
  display: none;
}

:deep(.p-togglebutton-content) {
  padding: 4px;
}
</style>
