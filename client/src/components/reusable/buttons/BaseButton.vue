<template>
  <button
    class="rounded-xl px-8 py-4 text-sm leading-3 transition-colors select-none"
    :class="
      inverted
        ? 'text-primary-400 disabled:text-gray-300 dark:text-primary-200 dark:disabled:text-gray-500 [&:not(:disabled)]:hover:bg-primary-200/20 [&:not(:disabled)]:active:bg-primary-200/20'
        : 'bg-primary-400 text-white disabled:bg-gray-300 dark:text-primary-200 dark:disabled:bg-primary-900 dark:disabled:text-gray-500 [&:not(:disabled)]:hover:bg-primary-500 [&:not(:disabled)]:active:bg-primary-500'
    "
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
const { inverted = false } = defineProps<{
  inverted?: boolean
}>()
</script>
