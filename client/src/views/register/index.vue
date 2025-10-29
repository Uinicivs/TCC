<template>
  <div class="w-full h-screen">
    <DottedBackground class="flex flex-col">
      <div class="w-full max-w-[500px] m-auto p-6 bg-white rounded-2xl shadow-lg">
        <div class="text-center mb-7">
          <img src="@/assets/svg/almostThere.svg" class="mx-auto mb-8" />
          <h2 class="text-3xl mb-4">Criar conta</h2>
          <p>Preencha os dados para criar sua conta</p>
        </div>

        <form class="flex flex-col gap-2" @submit.prevent="handleSubmit">
          <InputText
            v-model="formData.name"
            placeholder="Nome"
            size="small"
            :disabled="isLoading.value"
          />
          <InputText
            v-model="formData.email"
            placeholder="E-mail"
            size="small"
            :disabled="isLoading.value"
          />
          <InputText
            v-model="formData.password"
            placeholder="Senha"
            type="password"
            size="small"
            :disabled="isLoading.value"
          />
          <Button label="Criar conta" type="submit" size="small" :loading="isLoading.value" />
          <div class="text-center mt-2">
            <a href="/login" class="text-sm text-blue-600 hover:text-blue-800">
              Já tem uma conta? Faça login
            </a>
          </div>
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

import { register } from '@/services/authService'

const router = useRouter()
const toast = useToast()

const formData = reactive({
  name: '',
  email: '',
  password: '',
})

const isLoading = reactive({ value: false })

const handleSubmit = async () => {
  if (!formData.name || !formData.email || !formData.password) {
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
    await register({
      name: formData.name,
      email: formData.email,
      password: formData.password,
      role: 'admin',
    })

    toast.add({
      severity: 'success',
      summary: 'Sucesso',
      detail: 'Conta criada com sucesso! Faça login para continuar',
      life: 3000,
    })

    router.push('/login')
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Erro',
      detail: error instanceof Error ? error.message : 'Erro ao criar conta',
      life: 3000,
    })
  } finally {
    isLoading.value = false
  }
}
</script>
