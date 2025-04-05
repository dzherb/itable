<template>
  <div class="flex items-center justify-between rounded-soft bg-white p-4 shadow-sm">
    <div class="flex flex-col gap-2">
      <span class="text-primary">Портфель 1</span>
      <span class="text-2xl font-bold text-primary-500">500 000 Р</span>
    </div>
    <button class="flex h-10 w-10 items-center justify-center rounded-full bg-primary shadow-sm">
      <ArrowIcon />
    </button>
  </div>
</template>

<script setup lang="ts">
import ArrowIcon from '@/components/icons/ArrowIcon.vue'
</script>

<style scoped></style>
