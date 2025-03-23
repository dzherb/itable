<template>
  <div
    class="relative min-h-screen w-screen bg-white transition duration-300 dark:bg-black"
    :class="{ dark: isDark }"
  >
    <button
      @click="toggleThemeWithTransition"
      class="mt-4 ml-4 rounded-md bg-black p-2 text-white transition duration-300 dark:bg-white dark:text-black"
    >
      Toggle Theme
    </button>
    <RouterView />
    <div class="flex flex-col items-center gap-4 pt-20">
      <p v-for="i in 30" :key="i" class="w-fit text-black dark:text-white">
        some text to test theme transition, hope it turns out great
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme.ts'

const { isDark, toggleThemeWithTransition } = useTheme()
</script>
