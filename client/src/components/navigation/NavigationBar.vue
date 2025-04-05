<template>
  <nav class="flex items-center justify-start gap-6 bg-primary px-5 py-6 dark:bg-primary-900">
    <RouterLink :to="{ name: 'portfolios' }" v-slot="{ isActive }">
      <a
        class="text-xs font-bold text-white dark:text-primary-300"
        :class="{ 'opacity-50': !isActive }"
      >
        Мои портфели
      </a>
    </RouterLink>
    <RouterLink :to="{ name: 'tables' }" v-slot="{ isActive }">
      <a
        class="text-xs font-bold text-white dark:text-primary-300"
        :class="{ 'opacity-50': !isActive }"
      >
        Таблицы
      </a>
    </RouterLink>
    <span class="grow"></span>
    <button @click="toggleThemeWithTransition">
      <SettingsIcon class="fill-white dark:fill-primary-300" />
    </button>
  </nav>
</template>

<script setup lang="ts">
import SettingsIcon from '@/components/icons/SettingsIcon.vue'
import { useTheme } from '@/composables/useTheme.ts'

const { toggleThemeWithTransition } = useTheme()
</script>

<style scoped></style>
