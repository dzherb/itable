<template>
  <svg width="9" height="15" viewBox="0 0 9 15" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      v-bind="$attrs"
      d="M8 1L1 7.5L8 14"
      stroke="white"
      stroke-width="1.95312"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>

<script setup lang="ts">
defineOptions({
  inheritAttrs: false,
})
</script>
