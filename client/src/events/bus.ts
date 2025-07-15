import mitt from 'mitt'
import type { TokenPair } from '@/common/auth.ts'

export type Events = {
  tokenRefreshSucceed: TokenPair
  tokenRefreshFailed: Error
  userLoggedIn: void
  userLoggedOut: void
}

export const eventBus = mitt<Events>()
