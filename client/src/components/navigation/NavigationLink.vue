<template>
  <RouterLink :to="to" v-slot="{ isActive, navigate }" custom>
    <a
      @click="navigate"
      class="text-xs font-bold text-white dark:text-primary-300"
      :class="{ 'opacity-50': !isActive }"
    >
      <slot/>
    </a>
  </RouterLink>
</template>

<script setup lang="ts">
defineProps(['to'])
</script>

<style scoped>

</style>
