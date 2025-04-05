<template>
  <div class="bg-white p-4 flex justify-between items-center rounded-soft shadow-sm">
    <div class="flex flex-col gap-2">
      <span class="text-primary">Портфель 1</span>
      <span class="text-primary-500 font-bold text-2xl">500 000 Р</span>
    </div>
    <button class="bg-primary h-10 w-10 rounded-full flex justify-center items-center shadow-sm">
      <ArrowIcon />
    </button>
  </div>
</template>

<script setup lang="ts">

import ArrowIcon from "@/components/icons/ArrowIcon.vue";
</script>

<style scoped>

</style>
