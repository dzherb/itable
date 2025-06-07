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
      <NavigateButton @click="navigateToPortfolio" />
    </template>
  </ListItem>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { currencyRUBFormatter } from '@/utils/currency.ts'
import { useRouter } from 'vue-router'
import ListItem from '@/components/reusable/lists/ListItem.vue'
import NavigateButton from '@/components/reusable/buttons/NavigateButton.vue'

const props = defineProps<{
  id: number
  name: string
  total: number
}>()

const totalWithCurrency = computed(() => currencyRUBFormatter.format(props.total))

const router = useRouter()

const navigateToPortfolio = () => {
  router.push({ name: 'portfolio', query: { id: props.id } })
}
</script>

<style scoped></style>
