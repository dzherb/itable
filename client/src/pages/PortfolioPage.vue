<template>
  <ExtendedNavbarBlock>
    <PortfolioControlBlock />
  </ExtendedNavbarBlock>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import ExtendedNavbarBlock from '@/components/reusable/layout/ExtendedNavbarBlock.vue'
import PortfolioControlBlock from '@/components/pages/portfolios/PortfolioControlBlock.vue'

const portfolioID = useRoute().query?.id

if (!portfolioID) {
  useRouter().push({ name: 'portfolios' })
}
</script>
