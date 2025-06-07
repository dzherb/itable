<template>
  <BaseItemCard>
    <div class="flex flex-col gap-2">
      <slot name="name" />
      <slot name="additional" />
    </div>
    <slot name="append" />
  </BaseItemCard>
</template>

<script setup lang="ts">
import BaseItemCard from '@/components/reusable/lists/BaseItemCard.vue'
</script>
