<template>
  <NavigatableListItem>
    <template #name>
      <span class="text-sm text-primary-800 dark:text-primary-200">Таблица</span>
    </template>
    <template #additional>
      <span class="text-xs text-gray-500 dark:text-primary-300">MOEX</span>
    </template>
  </NavigatableListItem>
</template>

<script setup lang="ts">
import NavigatableListItem from '@/components/reusable/lists/NavigatableListItem.vue'
</script>

<style scoped></style>
