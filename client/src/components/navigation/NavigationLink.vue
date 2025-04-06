<template>
  <RouterLink :to="to" v-slot="{ isActive, navigate, href }" custom>
    <a
      :href
      @click="navigate"
      class="text-xs font-bold text-white dark:text-primary-300 transition-opacity"
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
