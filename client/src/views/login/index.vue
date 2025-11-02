<template>
  <div class="w-full h-screen">
    <DottedBackground class="flex flex-col">
      <div class="w-full max-w-[500px] m-auto p-6 bg-white rounded-2xl shadow-lg">
        <div class="text-center mb-7">
          <img src="@/assets/svg/almostThere.svg" class="mx-auto mb-8" />
          <h2 class="text-3xl mb-4">Bem-vindo!</h2>
          <p>Faça login para acessar sua conta</p>
        </div>

        <form class="flex flex-col gap-2" @submit.prevent="handleSubmit">
          <InputText
            v-model="user.email"
            placeholder="E-mail"
            size="small"
            :disabled="isLoading.value"
          />
          <InputText
            v-model="user.password"
            placeholder="Senha"
            type="password"
            size="small"
            :disabled="isLoading.value"
          />
          <Button label="Entrar" type="submit" size="small" :loading="isLoading.value" />
        </form>
      </div>
    </DottedBackground>
  </div>
</template>

<script lang="ts" setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { Button, InputText } from 'primevue'
import { useToast } from 'primevue/usetoast'

import DottedBackground from '@/components/shared/DottedBackground.vue'

import { login } from '@/services/authService'
import type { IUser } from '@/interfaces/user'

const router = useRouter()
const toast = useToast()

const user = reactive<IUser>({
  name: '',
  email: '',
  password: '',
})

const isLoading = reactive({ value: false })

const handleSubmit = async () => {
  if (!user.email || !user.password) {
    toast.add({
      severity: 'warn',
      summary: 'Atenção',
      detail: 'Por favor, preencha todos os campos',
      life: 3000,
    })
    return
  }

  isLoading.value = true

  try {
    await login({
      email: user.email,
      password: user.password,
    })

    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Login realizado com sucesso',
      life: 3000,
    })

    router.push('/')
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: error instanceof Error ? error.message : 'Erro ao fazer login',
      life: 3000,
    })
  } finally {
    isLoading.value = false
  }
}
</script>
