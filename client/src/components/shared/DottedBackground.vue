<template>
  <div class="w-full h-full dot-background">
    <slot />
  </div>
</template>

<style scoped>
.dot-background {
  background-image: radial-gradient(circle, var(--color-background-mute) 1px, transparent 1px);
  background-size: 1.5em 1.5em;
}
</style>
