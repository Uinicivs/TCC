<template>
  <div class="w-full h-screen">
    <DottedBackground class="flex flex-col">
      <div class="w-full max-w-[500px] m-auto p-6 bg-white rounded-2xl shadow-lg">
        <div class="text-center mb-7">
          <img src="@/assets/svg/almostThere.svg" class="mx-auto mb-8" />
          <h2 class="text-3xl mb-4">Bem-vindo!</h2>
          <p>Faça login para acessar sua conta</p>
        </div>

        <form class="flex flex-col gap-2" @submit="handleSubmit">
          <InputText v-model="user.email" placeholder="E-mail" size="small" />
          <InputText v-model="user.password" placeholder="Senha" type="password" size="small" />
          <Button label="Entrar" type="submit" size="small" />
        </form>
      </div>
    </DottedBackground>
  </div>
</template>

<script lang="ts" setup>
import { reactive } from 'vue'
import { Button, InputText } from 'primevue'

import DottedBackground from '@/components/shared/DottedBackground.vue'

import type { IUser } from '@/interfaces/user'

const user = reactive<IUser>({
  name: '',
  email: '',
  password: '',
})

const handleSubmit = () => {}
</script>
