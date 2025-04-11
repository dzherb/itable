<template>
  <ListContainer>
    <TableItem v-for="i in 4" :key="i" />
    <CreatePlug class="mt-4" />
  </ListContainer>
</template>

<script setup lang="ts">
import CreatePlug from '@/components/reusable/lists/CreatePlug.vue'
import TableItem from '@/components/pages/tables/TableItem.vue'
import ListContainer from '@/components/reusable/lists/ListContainer.vue'
</script>

<style scoped></style>
