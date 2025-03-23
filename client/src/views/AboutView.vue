<template>
  <h1 class="mx-auto my-4 w-fit">About page</h1>
  <div class="flex w-full justify-center">
    <base-button @click="$router.push({ name: 'home' })" class="mx-2 mt-4 w-40">
      To home
    </base-button>
  </div>
</template>

<script setup lang="ts">
import BaseButton from '@/components/reusable/BaseButton.vue'
</script>
