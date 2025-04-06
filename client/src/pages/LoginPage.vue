<template>
  <main
    class="flex min-h-screen flex-col items-center justify-center px-5"
    :class="{ dark: isDark }"
  >
    <LogoWithTitle @click="toggleThemeWithTransition" class="fixed top-8 left-5" />
    <div class="relative w-full max-w-96">
      <h1
        class="absolute -top-12 w-full text-start text-2xl font-semibold tracking-wide text-white"
      >
        Вход в систему
      </h1>
      <LoginForm />
    </div>
  </main>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme.ts'
import LogoWithTitle from '@/components/pages/login/LogoWithTitle.vue'
import LoginForm from '@/components/pages/login/LoginForm.vue'

const { isDark, toggleThemeWithTransition } = useTheme()
</script>

<style scoped>
@import '@/assets/main.css';

main {
  @apply bg-linear-[-21deg,var(--color-other-diamond)_0%,var(--color-primary-500)_30%,var(--color-primary-500)_70%,var(--color-other-diamond)] dark:bg-linear-[-21deg,var(--color-primary)_0%,var(--color-primary-800)_30%,var(--color-primary-800)_70%,var(--color-primary)];
}
</style>
