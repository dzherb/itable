<template>
  <div class="flex max-w-[700px] flex-col gap-2">
    <PortfolioItem name="Портфель 1" :total="500000" v-for="_ in 2" />
    <PortfolioCreatePlug class="mt-4" />
  </div>
</template>

<script setup lang="ts">
import PortfolioItem from '@/components/pages/portfolios/PortfolioItem.vue'
import PortfolioCreatePlug from '@/components/pages/portfolios/PortfolioCreatePlug.vue'
</script>

<style scoped></style>
