<template>
  <GoBackNavigationBar v-if="backTo" :backTo class="z-20" />
  <NavigationBar v-else class="z-20" />

  <main class="relative min-h-screen overflow-x-hidden dark:bg-primary-800">
    <div class="h-[72px] w-full bg-primary dark:bg-primary-900"></div>
    <RouterView v-slot="{ Component, route }">
      <Transition mode="out-in" :name="applyTransition ? (route?.meta?.transition as string) : ''">
        <KeepAlive>
          <Component :is="Component" />
        </KeepAlive>
      </Transition>
    </RouterView>
  </main>
</template>

<script setup lang="ts">
import NavigationBar from '@/components/navigation/NavigationBar.vue'
import { usePreferredReducedMotion } from '@vueuse/core'
import { computed } from 'vue'
import { useTailwindBreakpoints } from '@/composables/useTailwindBreakpoints.ts'
import GoBackNavigationBar from '@/components/navigation/GoBackNavigationBar.vue'
import { useRoute } from 'vue-router'

const reducedMotion = usePreferredReducedMotion()

const { breakpoints } = useTailwindBreakpoints()
const lgOrGreater = breakpoints.greaterOrEqual('lg')

const backTo = computed(() => useRoute().meta?.backTo as string)

const applyTransition = computed(
  () => reducedMotion.value === 'no-preference' && !lgOrGreater.value,
)
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
