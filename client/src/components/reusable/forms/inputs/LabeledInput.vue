<template>
  <div class="flex flex-col gap-3">
    <label
      class="text-sm font-bold text-primary-400 select-none dark:text-primary-200"
      v-if="label"
      :for="$attrs?.name as string"
    >
      {{ label }}
    </label>
    <BaseInput v-bind="$attrs" :autofocus />
  </div>
</template>

<script setup lang="ts">
import BaseInput from '@/components/reusable/forms/inputs/BaseInput.vue'

defineOptions({
  inheritAttrs: false,
})

const props = defineProps<{
  label?: string
  autofocus?: boolean
}>()
</script>
