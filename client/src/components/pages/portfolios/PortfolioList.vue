<template>
  <ListContainer>
    <PortfolioListItem :id="12" name="Портфель 1" :total="500000" v-for="i in 2" :key="i" />
    <CreatePlug class="mt-4" />
  </ListContainer>
</template>

<script setup lang="ts">
import PortfolioListItem from '@/components/pages/portfolios/PortfolioListItem.vue'
import CreatePlug from '@/components/reusable/lists/CreatePlug.vue'
import ListContainer from '@/components/reusable/lists/ListContainer.vue'
</script>
