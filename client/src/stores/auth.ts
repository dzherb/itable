import { defineStore } from 'pinia'
import { ref, toValue, type MaybeRefOrGetter } from 'vue'
import * as auth from '@/common/auth'
import { type TokenPair, type TokenPairResponse } from '@/common/auth'
import { apiV1 } from '@/common/api'
import { eventBus } from '@/events/bus.ts'

interface User {
  id: number
  email: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)

  const login = async (email: MaybeRefOrGetter<string>, password: MaybeRefOrGetter<string>) => {
    const data: TokenPairResponse = await apiV1
      .post(
        '/api/auth/login/',
        {
          email: toValue(email),
          password: toValue(password),
        },
        { handleRefresh: false },
      )
      .then((r) => r.json())

    const tokens: TokenPair = {
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
    }
    auth.setTokens(tokens)

    eventBus.emit('userLoggedIn')
  }

  const logout = async () => {
    auth.clearTokens()
    eventBus.emit('userLoggedOut')
  }

  const fetchCurrentUser = async () => {
    user.value = await apiV1.get('/api/users/me/').then((r) => r.json())
  }

  return { user, login, logout, fetchCurrentUser }
})
