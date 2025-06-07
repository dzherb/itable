<template>
  <BaseModal v-if="showModal" @close="showModal = false" />
  <button
    @click="showModal = true"
    v-bind="$attrs"
    class="flex h-[88px] items-center justify-center gap-3 rounded-soft text-lg text-white opacity-50 transition-opacity select-none hover:opacity-70 active:opacity-70"
  >
    Создать <PlusIcon />
  </button>
</template>

<script setup lang="ts">
import PlusIcon from '@/components/icons/PlusIcon.vue'
import BaseModal from '@/components/modals/BaseModal.vue'
import { shallowRef } from 'vue'

defineOptions({
  inheritAttrs: false,
})

const showModal = shallowRef(false)
</script>

<style scoped>
button {
  background-image: url("data:image/svg+xml,%3csvg width='100%25' height='100%25' xmlns='http://www.w3.org/2000/svg'%3e%3crect width='100%25' height='100%25' fill='none' rx='12' ry='12' stroke='white' stroke-width='1' stroke-dasharray='12' stroke-dashoffset='12' stroke-linecap='square'/%3e%3c/svg%3e");
  border-radius: 12px;
}
</style>
