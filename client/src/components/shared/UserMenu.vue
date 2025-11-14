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
      <div class="flex flex-col gap-3 min-w-[200px]">
        <div class="flex flex-col gap-2">
          <div class="flex items-center gap-2">
            <Avatar :label="userInitials" shape="circle" size="normal" />
            <div class="flex flex-col">
              <p class="text-sm font-medium truncate">{{ userName }}</p>
              <p class="text-xs text-neutral-500 dark:text-neutral-400 truncate">{{ userEmail }}</p>
            </div>
          </div>
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
const { userEmail, userName, userInitials } = storeToRefs(authStore)
const menuRef = useTemplateRef('menu')

const handleLogout = () => {
  authStore.clearTokens()
  router.push('/login')
}
</script>
