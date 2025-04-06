<template>
  <NavigatableListItem>
    <template #name>
      <span class="text-sm text-primary dark:text-primary-300">{{ name }}</span>
    </template>
    <template #additional>
      <span class="text-2xl font-bold text-primary-500 dark:text-primary-200">
        {{ totalWithCurrency }}
      </span>
    </template>
  </NavigatableListItem>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { currencyRUBFormatter } from '@/utils/currency.ts'
import NavigatableListItem from '@/components/reusable/lists/NavigatableListItem.vue'

const props = defineProps<{
  name: string
  total: number
}>()

const totalWithCurrency = computed(() => currencyRUBFormatter.format(props.total))
</script>

<style scoped></style>
