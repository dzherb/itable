import { breakpointsTailwind, useBreakpoints } from '@vueuse/core'

const breakpoints = useBreakpoints(breakpointsTailwind)

export const useTailwindBreakpoints = () => {
  return {
    breakpoints,
  }
}
