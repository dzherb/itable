<template>
  <ModalBase :closable="false" @close="$emit('close')">
    <div class="flex flex-col gap-4">
      <h2 class="text-sm font-bold text-primary dark:text-primary-200">
        Вы действительно хотите удалить {{ entity }}?
      </h2>
      <p class="text-xs text-primary-800 dark:text-primary-200">Восстановить будет невозможно</p>
      <div class="mt-1 flex flex-col justify-between gap-2 xs:flex-row xs:gap-5">
        <BaseButton class="basis-full" @click="$emit('confirm')">Да</BaseButton>
        <BaseButton inverted class="basis-full" @click="$emit('close')">Нет</BaseButton>
      </div>
    </div>
  </ModalBase>
</template>

<style scoped></style>
<script setup lang="ts">
import BaseButton from '@/components/reusable/buttons/BaseButton.vue'
import ModalBase from '@/components/reusable/modals/ModalBase.vue'

defineProps<{
  entity?: string
}>()

defineEmits<{
  close: []
  confirm: []
}>()
</script>
