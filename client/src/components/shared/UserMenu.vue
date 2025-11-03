<template>
  <div class="flex items-center gap-3">
    <Avatar
      :label="userInitials"
      shape="circle"
      size="normal"
      class="cursor-pointer bg-primary text-primary-contrast"
      @click="(event: Event) => menuRef?.toggle(event)"
    />

    <Popover ref="menu" class="!rounded-tl-xl !rounded-bl-xl !rounded-br-xl !shadow-lg">
      <div class="flex flex-col gap-2 min-w-[160px]">
        <div class="flex items-center gap-2">
          <Avatar :label="userInitials" shape="circle" size="normal" />

          <p class="text-sm truncate">{{ userEmail }}</p>
        </div>
        <Button
          severity="danger"
          variant="text"
          label="Sair"
          icon="pi pi-sign-out"
          size="small"
          @click="handleLogout"
        />
      </div>
    </Popover>
  </div>
</template>

<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useRouter } from 'vue-router'
import { Avatar, Popover, Button } from 'primevue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const { userEmail, userInitials } = storeToRefs(authStore)
const menuRef = useTemplateRef('menu')

const handleLogout = () => {
  authStore.clearTokens()
  router.push('/login')
}
</script>
