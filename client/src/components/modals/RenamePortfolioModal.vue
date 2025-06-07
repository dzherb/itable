<template>
  <BaseModal :closable="false" @close="$emit('close')">
    <form class="flex flex-col gap-4" @submit.prevent>
      <h2 class="text-sm font-bold text-primary dark:text-primary-200">Назовите портфель</h2>
      <BaseInput autofocus />
      <div class="mt-1 flex flex-col justify-between gap-2 xs:flex-row xs:gap-5">
        <BaseButton class="basis-full">Сохранить</BaseButton>
        <BaseButton inverted class="basis-full" @click="$emit('close')">Отмена</BaseButton>
      </div>
    </form>
  </BaseModal>
</template>

<script setup lang="ts">
import BaseModal from '@/components/modals/BaseModal.vue'
import BaseInput from '@/components/reusable/forms/inputs/BaseInput.vue'
import BaseButton from '@/components/reusable/buttons/BaseButton.vue'

defineEmits<{
  close: []
}>()
</script>
