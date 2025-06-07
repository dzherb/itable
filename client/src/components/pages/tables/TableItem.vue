<template>
  <ListItem>
    <template #name>
      <span class="text-sm leading-none text-primary-800 dark:text-primary-200">Таблица</span>
    </template>
    <template #additional>
      <span class="text-xs leading-none text-gray-500 dark:text-primary-300">MOEX</span>
    </template>
    <template #append>
      <NavigateButton />
    </template>
  </ListItem>
</template>

<script setup lang="ts">
import ListItem from '@/components/reusable/lists/ListItem.vue'
import NavigateButton from '@/components/reusable/buttons/NavigateButton.vue'
</script>
