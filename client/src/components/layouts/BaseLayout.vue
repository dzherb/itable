<template>
  <NavigationBar class="z-20" />
  <main
    :class="{ dark: isDark }"
    class="relative min-h-screen overflow-x-hidden dark:bg-primary-800"
  >
    <div class="h-[72px] w-full bg-primary dark:bg-primary-900"></div>
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
import { useTailwindBreakpoints } from '@/composables/useTailwindBreakpoints.ts'

const reducedMotion = usePreferredReducedMotion()

const { breakpoints } = useTailwindBreakpoints()
const lgOrGreater = breakpoints.greaterOrEqual('lg')

const applyTransition = computed(
  () => reducedMotion.value === 'no-preference' && !lgOrGreater.value,
)

// todo hydration mismatch if client expects dark mode on
const { isDark } = useTheme()
</script>

<style scoped>
@import '@/assets/main.css';

.slide-left-enter-active,
.slide-left-leave-active,
.slide-right-enter-active,
.slide-right-leave-active {
  @apply transition-all duration-200 ease-in-out;
}

.slide-left-enter-from {
  transform: translateX(-100%);
}

.slide-left-leave-to {
  transform: translateX(100%);
}

.slide-right-enter-from {
  transform: translateX(100%);
}

.slide-right-leave-to {
  transform: translateX(-100%);
}

.slide-left-leave-from,
.slide-right-leave-from {
  transform: translateX(0);
}
</style>
