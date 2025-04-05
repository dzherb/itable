<template>
  <div class="h-24 flex justify-center items-center rounded-soft text-white opacity-50 text-lg gap-3">
    Создать <PlusIcon/>
  </div>
</template>

<script setup lang="ts">

import PlusIcon from "@/components/icons/PlusIcon.vue";
</script>

<style scoped>
  div {
    background-image: url("data:image/svg+xml,%3csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3e%3crect width='100%25' height='100%25' fill='none' rx='12' ry='12' stroke='white' stroke-width='1' stroke-dasharray='12' stroke-dashoffset='12' stroke-linecap='square'/%3e%3c/svg%3e");
    border-radius: 12px;
  }
</style>
