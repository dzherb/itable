<template>
  <BaseNavigationBar>
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
  </BaseNavigationBar>
</template>

<script setup lang="ts">
import SettingsIcon from '@/components/icons/SettingsIcon.vue'
import { useTheme } from '@/composables/useTheme.ts'
import NavigationLink from '@/components/navigation/NavigationLink.vue'
import { useTailwindBreakpoints } from '@/composables/useTailwindBreakpoints.ts'
import BaseNavigationBar from '@/components/navigation/BaseNavigationBar.vue'

const { toggleThemeWithTransition } = useTheme()
const { breakpoints } = useTailwindBreakpoints()
const mdOrGreater = breakpoints.greaterOrEqual('md')
</script>

<style scoped></style>
