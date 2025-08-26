<template>
  <div class="w-full h-screen">
    <DottedBackground class="flex flex-col">
      <div class="w-full max-w-[400px] m-auto">
        <div class="text-center mb-7">
          <img src="@/assets/svg/almostThere.svg" alt="almost there icon" class="mx-auto mb-8" />
          <h2 class="text-3xl mb-8">Almost there...</h2>
          <p>We just need a few details to get you started</p>
        </div>

        <form class="flex flex-col gap-2" @submit="handleSubmit">
          <InputText v-model="user.name" placeholder="Your first name" />
          <InputText v-model="user.email" placeholder="Your best e-mail" />
          <InputText v-model="user.password" placeholder="Your password" type="password" />
          <Button label="Submit" type="submit" severity="contrast" />
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
