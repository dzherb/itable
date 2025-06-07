<template>
  <teleport to="body">
    <UseFocusTrap :options="{ immediate: true, allowOutsideClick: true }">
      <div
        class="fade-in fixed top-0 left-0 z-40 flex h-full w-screen items-center justify-center overflow-y-auto bg-black/40 py-10 dark:bg-black/30"
      >
        <div
          v-on-click-outside="() => $emit('close')"
          ref="mainContainer"
          class="slide-in mx-5 my-auto max-w-[510px] grow rounded-soft bg-white px-6 py-6 shadow-md dark:bg-primary-800"
        >
          <slot name="header">
            <div class="flex justify-end">
              <CloseButton @click="$emit('close')" />
            </div>
          </slot>
          <div v-if="$slots.default" class="px-2 pb-2">
            <slot name="default" />
          </div>
        </div>
      </div>
    </UseFocusTrap>
  </teleport>
</template>

<script setup lang="ts">
import { UseFocusTrap } from '@vueuse/integrations/useFocusTrap/component'
import { vOnClickOutside } from '@vueuse/components'
import CloseButton from '@/components/reusable/buttons/CloseButton.vue'

defineEmits<{
  close: []
}>()
</script>

<style scoped>
.fade-in {
  animation: 150ms ease-out 0s 1 fade-in-animation forwards;
}
@keyframes fade-in-animation {
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
}

.slide-in {
  animation: 300ms ease-out 0s 1 slide-in-animation forwards;
}
@keyframes slide-in-animation {
  0% {
    transform: translateY(-5%);
  }
  100% {
    transform: translateY(0);
  }
}
</style>
