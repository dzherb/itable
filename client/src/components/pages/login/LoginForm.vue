<template>
  <form
    class="flex w-full flex-col gap-5 rounded-soft bg-white px-6 py-6 shadow-xl dark:bg-primary-800"
  >
    <AnnotatedInput autofocus v-model="email" label="Почта" name="email" />
    <AnnotatedInput v-model="password" label="Пароль" name="password" type="password" />
    <div class="mt-5 flex flex-col-reverse items-center gap-5 sm:flex-row sm:gap-2">
      <span class="flex justify-center sm:basis-1/2">
        <BaseLink>Забыли пароль?</BaseLink>
      </span>
      <BaseButton
        type="button"
        @click="attemptToLogin()"
        :disabled="isLoginButtonDisabled"
        class="w-full sm:basis-1/2"
        >Войти</BaseButton
      >
    </div>
  </form>
</template>

<script setup lang="ts">
import BaseButton from '@/components/reusable/buttons/BaseButton.vue'
import AnnotatedInput from '@/components/reusable/forms/inputs/AnnotatedInput.vue'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import BaseLink from '@/components/reusable/links/BaseLink.vue'
import {onKeyStroke, useAsyncState} from '@vueuse/core'
import { useAuthStore } from '@/stores/auth.ts'

const email = ref('')
const password = ref('')

const { execute: login, isLoading, isReady: isLoggedIn } = useAsyncState(
  () => useAuthStore().login(email.value, password.value),
  null,
  {
    immediate: false
  }
)

const isLoginButtonDisabled = computed(() => {
  return isLoading.value || !(email.value && password.value)
})

const router = useRouter()

const attemptToLogin = async () => {
  await login()
  if (isLoggedIn.value) {
    await router.push({ name: 'home' })
  }
}

onKeyStroke('Enter', () => {
  if (!isLoginButtonDisabled.value) {
    attemptToLogin()
  }
})
</script>
