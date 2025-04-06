<template>
  <input v-model="model" class="h-11 px-4 text-sm text-primary-800 border border-primary-300/50 focus:border-primary-400 hover:border-primary-300/80 transition-colors rounded-md outline-0 dark:text-primary-200 dark:bg-primary-700"/>
</template>

<script setup lang="ts">
const model = defineModel()
</script>
