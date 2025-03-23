import { useColorMode } from '@vueuse/core'
import { computed, nextTick } from 'vue'

export const useTheme = () => {
  const { store, state } = useColorMode({ disableTransition: false })
  const isDark = computed(() => state.value === 'dark')
  const isLight = computed(() => state.value === 'light')
  const toggleThemeState = () => {
    if (isDark.value) {
      store.value = 'light'
    } else {
      store.value = 'dark'
    }
  }

  const toggleThemeWithTransition = async (event: MouseEvent | TouchEvent) => {
    if (!document.startViewTransition) {
      // Fallback if a browser doesn't support the View Transitions API
      toggleThemeState()
      return
    }

    const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX
    const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY

    const maxSize = Math.max(window.innerWidth, window.innerHeight) * 2

    await document.startViewTransition(() => {
      nextTick(() => toggleThemeState())
    }).ready

    document.documentElement.animate(
      {
        clipPath: [
          `circle(0px at ${clientX}px ${clientY}px)`,
          `circle(${maxSize}px at ${clientX}px ${clientY}px)`,
        ],
      },
      {
        duration: 500,
        easing: 'ease-in-out',
        pseudoElement: '::view-transition-new(root)',
      },
    )
  }

  return {
    isDark,
    isLight,
    toggleThemeState,
    toggleThemeWithTransition,
  }
}
