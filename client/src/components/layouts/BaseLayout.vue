<template>
  <main :class="{ dark: isDark }" class="min-h-screen dark:bg-primary-800">
    <NavigationBar />
    <RouterView v-slot="{ Component, route }">
      <Transition mode="out-in" :name="applyTransition ? String(route?.meta?.transition) : ''">
        <KeepAlive>
          <Component class="w-full" :is="Component" />
        </KeepAlive>
      </Transition>
    </RouterView>
  </main>
</template>

<script setup lang="ts">
import NavigationBar from '@/components/navigation/NavigationBar.vue'
import { usePreferredReducedMotion } from '@vueuse/core'
import { computed } from 'vue'
import { useTheme } from '@/composables/useTheme.ts'

const reducedMotion = usePreferredReducedMotion()
const applyTransition = computed(() => reducedMotion.value === 'no-preference')

const { isDark } = useTheme()
</script>

<style scoped>
@import '@/assets/main.css';

.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  @apply transition-all duration-200 ease-in-out lg:transition-none lg:duration-0;
}

.slide-left-enter-to,
.slide-right-enter-to {
  position: absolute;
  right: 0;
}

.slide-left-enter-from {
  position: absolute;
  right: 100%;
}

.slide-left-leave-to {
  position: absolute;
  left: 100%;
}

.slide-right-enter-from {
  position: absolute;
  right: -100%;
}

.slide-right-leave-to {
  position: absolute;
  left: -100%;
}

.slide-left-leave-from,
.slide-right-leave-from {
  position: absolute;
  left: 0;
}
</style>
