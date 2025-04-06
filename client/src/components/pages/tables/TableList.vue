<template>
  <ListContainer>
    <TableItem v-for="_ in 4" />
    <CreatePlug class="mt-4" />
  </ListContainer>
</template>

<script setup lang="ts">
import CreatePlug from '@/components/reusable/lists/CreatePlug.vue'
import TableItem from '@/components/pages/tables/TableItem.vue'
import ListContainer from '@/components/reusable/lists/ListContainer.vue'
</script>

<style scoped></style>
