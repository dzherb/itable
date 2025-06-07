<template>
  <div>
    <ExtendedNavbarBlock>
      <PortfolioControlBlock />
    </ExtendedNavbarBlock>
    <div class="px-5 pb-5">
      <RelatedTables class="mt-6" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import ExtendedNavbarBlock from '@/components/reusable/layout/ExtendedNavbarBlock.vue'
import PortfolioControlBlock from '@/components/pages/portfolios/PortfolioControlBlock.vue'
import RelatedTables from '@/components/pages/portfolios/RelatedTables.vue'

const portfolioID = useRoute().query?.id

if (!portfolioID) {
  useRouter().push({ name: 'portfolios' })
}
</script>
