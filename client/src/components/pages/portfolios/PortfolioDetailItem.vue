<template>
  <ListItem>
    <template #name>
      <span class="text-sm leading-none text-primary dark:text-primary-300">{{ name }}</span>
    </template>
    <template #additional>
      <span class="text-2xl leading-none font-bold text-primary-500 dark:text-primary-200">
        {{ totalWithCurrency }}
      </span>
    </template>
    <template #append>
      <div class="h-full text-xs leading-[14px] text-primary-400 dark:text-primary-300">
        от {{ dateFormatted }}
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
