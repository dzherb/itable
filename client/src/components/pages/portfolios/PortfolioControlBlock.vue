<template>
  <RenamePortfolioModal v-if="showRenamePortfolioModal" @close="showRenamePortfolioModal = false" />
  <ConfirmDeleteModal
    entity="портфель"
    v-if="showDeletePortfolioModal"
    @confirm="() => {}"
    @close="showDeletePortfolioModal = false"
  />

  <div class="flex gap-2">
    <ListContainer class="grow">
      <PortfolioDetailItem />
    </ListContainer>
    <div class="flex flex-col justify-start gap-2">
      <CardButton @click="showRenamePortfolioModal = true">
        <EditIcon class="dark:stroke-primary-300" />
      </CardButton>
      <CardButton @click="showDeletePortfolioModal = true">
        <DeleteIcon class="dark:fill-primary-300" />
      </CardButton>
    </div>
  </div>
</template>

<script setup lang="ts">
import EditIcon from '@/components/icons/EditIcon.vue'
import CardButton from '@/components/reusable/buttons/CardButton.vue'
import PortfolioDetailItem from '@/components/pages/portfolios/PortfolioDetailItem.vue'
import DeleteIcon from '@/components/icons/DeleteIcon.vue'
import RenamePortfolioModal from '@/components/modals/RenamePortfolioModal.vue'
import { shallowRef } from 'vue'
import ConfirmDeleteModal from '@/components/modals/ConfirmDeleteModal.vue'
import ListContainer from '@/components/reusable/lists/ListContainer.vue'

const showRenamePortfolioModal = shallowRef(false)
const showDeletePortfolioModal = shallowRef(false)
</script>
