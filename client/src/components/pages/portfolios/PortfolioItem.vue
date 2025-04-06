<template>
  <div
    class="flex items-center justify-between rounded-soft bg-white p-4 shadow-sm dark:bg-primary-800"
  >
    <div class="flex flex-col gap-2">
      <span class="text-primary dark:text-primary-300">{{ name }}</span>
      <span class="text-2xl font-bold text-primary-500 dark:text-primary-200">{{ totalWithCurrency }}</span>
    </div>
    <button class="flex h-10 w-10 items-center justify-center rounded-full bg-primary shadow-sm">
      <ArrowIcon class="stroke-white dark:stroke-primary-200" />
    </button>
  </div>
</template>

<script setup lang="ts">
import ArrowIcon from '@/components/icons/ArrowIcon.vue'
import {computed} from "vue";
import {currencyRUBFormatter} from "@/utils/currency.ts";

const props = defineProps<{
  name: string
  total: number
}>()

const totalWithCurrency = computed(
  () => currencyRUBFormatter.format(props.total)
)
</script>

<style scoped></style>
