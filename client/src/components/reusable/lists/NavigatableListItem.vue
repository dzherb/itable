<template>
  <BaseItemCard>
    <div class="flex flex-col gap-2">
      <slot name="name" />
      <slot name="additional" />
    </div>
    <button class="flex h-10 w-10 items-center justify-center rounded-full bg-primary shadow-sm">
      <ArrowIcon class="stroke-white dark:stroke-primary-200" />
    </button>
  </BaseItemCard>
</template>

<script setup lang="ts">
import ArrowIcon from '@/components/icons/ArrowIcon.vue'
import BaseItemCard from '@/components/reusable/lists/BaseItemCard.vue'
</script>
