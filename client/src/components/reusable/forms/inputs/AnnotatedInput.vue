<template>
  <div class="flex flex-col gap-3">
    <label
      class="text-primary-400 text-sm font-bold select-none dark:text-primary-200"
      v-if="label" :for="String($attrs?.name)"
    >
      {{ label }}
    </label>
    <BaseInput v-bind="$attrs" />
  </div>
</template>

<script setup lang="ts">
import BaseInput from "@/components/reusable/forms/inputs/BaseInput.vue";

defineOptions({
  inheritAttrs: false
})

const props = defineProps<{
  label?: string
}>()
</script>

<style scoped>

</style>
