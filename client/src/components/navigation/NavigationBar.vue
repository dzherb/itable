<template>
  <nav
    class="fixed flex w-full items-center justify-start gap-6 bg-primary px-5 py-6 dark:bg-primary-900"
  >
    <NavigationLink :to="{ name: 'portfolios' }"> Мои портфели </NavigationLink>
    <NavigationLink :to="{ name: 'tables' }"> Таблицы </NavigationLink>
    <span class="grow"></span>
    <button @click="toggleThemeWithTransition">
      <SettingsIcon class="fill-white dark:fill-primary-300" />
    </button>
  </nav>
</template>

<script setup lang="ts">
import SettingsIcon from '@/components/icons/SettingsIcon.vue'
import { useTheme } from '@/composables/useTheme.ts'
import NavigationLink from '@/components/navigation/NavigationLink.vue'

const { toggleThemeWithTransition } = useTheme()
</script>

<style scoped></style>
