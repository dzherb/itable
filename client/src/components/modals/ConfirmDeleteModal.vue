<template>
  <BaseModal :closable="false" @close="$emit('close')">
    <div class="flex flex-col gap-4">
      <h2 class="text-sm font-bold text-primary dark:text-primary-200">
        Вы действительно хотите удалить {{ entity }}?
      </h2>
      <p class="text-xs text-primary-800 dark:text-primary-200">Восстановить будет невозможно</p>
      <div class="mt-1 flex flex-col justify-between gap-2 xs:flex-row xs:gap-5">
        <BaseButton class="basis-full">Да</BaseButton>
        <BaseButton inverted class="basis-full" @click="$emit('close')">Нет</BaseButton>
      </div>
    </div>
  </BaseModal>
</template>

<style scoped></style>
<script setup lang="ts">
import BaseModal from '@/components/modals/BaseModal.vue'
import BaseButton from '@/components/reusable/buttons/BaseButton.vue'

defineProps<{
  entity?: string
}>()

defineEmits<{
  close: []
}>()
</script>
