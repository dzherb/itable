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

  const login = async (email: string, password: string): Promise<void> => {
    const res = await fetch('/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })

    const data: TokenPairResponse = await res.json()
    const tokens: TokenPair = { accessToken: data.access_token, refreshToken: data.refresh_token }
    if (!res.ok) throw new Error('Login failed')

    setTokens(tokens)
    isAuthenticated.value = true
  }

  const logout = () => {
    clearTokens()
    isAuthenticated.value = false
  }

  async function fetchProfile() {
    const res = await apiFetch('/api/users/me/')
    if (res.ok) {
      user.value = await res.json()
      isAuthenticated.value = true
    } else {
      isAuthenticated.value = false
    }
  }

  return { user, isAuthenticated, login, logout, fetchProfile }
})
