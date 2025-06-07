<template>
  <ListItem>
    <template #name>
      <span class="text-sm font-bold text-primary dark:text-primary-300">{{ name }}</span>
    </template>
    <template #additional>
      <span class="text-2xl font-bold text-primary-500 dark:text-primary-200">
        {{ totalWithCurrency }}
      </span>
    </template>
    <template #append>
      <div class="relative h-full min-w-20">
        <span class="absolute top-1 right-0 text-xs text-primary-400 dark:text-primary-300">
          от {{ dateFormatted }}
        </span>
      </div>
    </template>
  </ListItem>
</template>

<script setup lang="ts">
// todo there is a lot in common with the PortfolioListItem, we should have a base component

import { computed, shallowRef } from 'vue'
import { currencyRUBFormatter } from '@/utils/currency.ts'
import ListItem from '@/components/reusable/lists/ListItem.vue'

const name = shallowRef('Портфель 1')
const total = shallowRef(500000)
const created = shallowRef(new Date())

const totalWithCurrency = computed(() => currencyRUBFormatter.format(total.value))
const dateFormatted = computed(() => created.value.toLocaleDateString())
</script>
