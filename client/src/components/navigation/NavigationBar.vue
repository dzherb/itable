<template>
  <nav class="flex items-center justify-start gap-6 bg-primary px-5 py-6">
    <RouterLink :to="{ name: 'portfolios' }" v-slot="{ isActive }">
      <a class="text-xs font-bold text-white" :class="{ 'opacity-50': !isActive }">
        Мои портфели
      </a>
    </RouterLink>
    <RouterLink :to="{ name: 'tables' }" v-slot="{ isActive }">
      <a class="text-xs font-bold text-white" :class="{ 'opacity-50': !isActive }"> Таблицы </a>
    </RouterLink>
    <span class="grow"></span>
    <button>
      <SettingsIcon />
    </button>
  </nav>
</template>

<script setup lang="ts">
import SettingsIcon from '@/components/icons/SettingsIcon.vue'
</script>

<style scoped></style>
