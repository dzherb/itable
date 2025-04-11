import { defineStore } from 'pinia'
import { ref } from 'vue'
import { setTokens, clearTokens, type TokenPair, type TokenPairResponse } from '@/api/authService'
import { apiFetch } from '@/api/apiClient.ts'

interface User {
  id: number
  email: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = ref(false)

  const login = async (email: string, password: string) => {
    const response = await apiFetch(
      '/api/auth/login/',
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
        }),
      },
      false,
    )
    const data: TokenPairResponse = await response.json()
    const tokens: TokenPair = {
      accessToken: data.access_token,
      refreshToken: data.refresh_token,
    }
    setTokens(tokens)
    isAuthenticated.value = true
  }

  const logout = () => {
    clearTokens()
    isAuthenticated.value = false
  }

  async function fetchProfile() {
    try {
      const response = await apiFetch('/api/users/me/', {}, false)
      user.value = await response.json()
      isAuthenticated.value = true
    } catch {
      isAuthenticated.value = false
    }
  }

  return { user, isAuthenticated, login, logout, fetchProfile }
})
