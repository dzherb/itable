<template>
  <form @submit.prevent class="w-full flex flex-col gap-5 rounded-soft bg-white px-6 py-6 dark:bg-primary-800">
    <AnnotatedInput v-model="login" label="Почта" name="email"/>
    <AnnotatedInput v-model="password" label="Пароль" name="password" type="password"/>
    <div class="flex items-center gap-2 mt-5">
      <span class="basis-1/2">
        <a class="text-xs text-primary-400 dark:text-primary-300">Забыли пароль?</a>
      </span>
      <BaseButton :disabled="isLoginButtonDisabled" class="basis-1/2">Войти</BaseButton>
    </div>
  </form>
</template>

<script setup lang="ts">
import BaseButton from "@/components/reusable/buttons/BaseButton.vue";
import AnnotatedInput from "@/components/reusable/forms/inputs/AnnotatedInput.vue";
import {computed, ref} from "vue";

const login = ref('')
const password = ref('')

const isLoginButtonDisabled = computed(() => {
  return !(login.value && password.value)
})
</script>
