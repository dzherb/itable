<template>
  <input
    ref="input"
    v-model="model"
    class="h-11 rounded-md border border-primary-300/50 px-4 text-sm text-primary-800 outline-0 transition-colors hover:border-primary-300/80 focus:border-primary-400 dark:bg-primary-700 dark:text-primary-200"
  />
</template>

<script setup lang="ts">
import { useTemplateRef, watchEffect } from 'vue'

const model = defineModel()

const props = defineProps<{
  autofocus?: boolean
}>()

const inputRef = useTemplateRef('input')

watchEffect(() => {
  if (inputRef.value && props.autofocus) {
    inputRef.value.focus()
  }
})
</script>
