<template>
  <ExtendedNavbarBlock>
    <PortfolioDetailItem />
  </ExtendedNavbarBlock>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import ExtendedNavbarBlock from '@/components/reusable/layout/ExtendedNavbarBlock.vue'
import PortfolioDetailItem from '@/components/pages/portfolios/PortfolioDetailItem.vue'

const portfolioID = useRoute().query?.id

if (!portfolioID) {
  useRouter().push({ name: 'portfolios' })
}
</script>
