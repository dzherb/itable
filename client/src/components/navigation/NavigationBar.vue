<template>
  <nav
    class="fixed flex w-full items-center justify-start gap-6 bg-primary px-5 py-6 dark:bg-primary-900"
  >
    <NavigationLink :to="{ name: 'portfolios' }"> Мои портфели </NavigationLink>
    <NavigationLink :to="{ name: 'tables' }"> Таблицы </NavigationLink>
    <span class="grow"></span>
    <button class="flex items-center gap-4" @click="toggleThemeWithTransition">
      <SettingsIcon class="fill-white dark:fill-primary-300" />
      <span
        v-show="mdOrGreater"
        class="text-xs font-bold text-white lg:text-sm dark:text-primary-300"
        >Настройки</span
      >
    </button>
  </nav>
</template>

<script setup lang="ts">
import SettingsIcon from '@/components/icons/SettingsIcon.vue'
import { useTheme } from '@/composables/useTheme.ts'
import NavigationLink from '@/components/navigation/NavigationLink.vue'
import { useTailwindBreakpoints } from '@/composables/useTailwindBreakpoints.ts'

const { toggleThemeWithTransition } = useTheme()
const { breakpoints } = useTailwindBreakpoints()
const mdOrGreater = breakpoints.greaterOrEqual('md')
</script>

<style scoped></style>
