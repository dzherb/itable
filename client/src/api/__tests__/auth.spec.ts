import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest'
import * as authService from '@/api/authService'
import { useAuthStore } from '@/stores/auth.ts'
import { createPinia, setActivePinia } from 'pinia'

global.fetch = vi.fn()

describe('authService', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetAllMocks()
  })

  it('should store and retrieve tokens from localStorage', () => {
    authService.setTokens({ accessToken: '123', refreshToken: '321' })
    expect(authService.getAccessToken()).toBe('123')
    expect(authService.getRefreshToken()).toBe('321')
  })

  it('should remove token on clearTokens', () => {
    authService.setTokens({ accessToken: '123', refreshToken: '321' })
    authService.clearTokens()
    expect(authService.getAccessToken()).toBeNull()
    expect(authService.getRefreshToken()).toBeNull()
  })

  it('should refresh token correctly', async () => {
    authService.setTokens({ accessToken: 'old_access_token', refreshToken: 'old_refresh_token' })

    const accessToken = 'new_access_token'
    const refreshToken = 'new_refresh_token'

    ;(fetch as Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access_token: accessToken, refresh_token: refreshToken }),
    })

    const tokens = await authService.refreshTokens()
    expect(tokens.accessToken).toBe(accessToken)
    expect(tokens.refreshToken).toBe(refreshToken)
  })

  it('should throw on failed refresh', async () => {
    authService.setTokens({ accessToken: '123', refreshToken: '321' })
    ;(fetch as Mock).mockResolvedValue({ ok: false })

    await expect(authService.refreshTokens()).rejects.toThrow('Tokens refresh failed')
  })

  it('should throw on refresh attempt with no refresh token available', async () => {
    ;(fetch as Mock).mockResolvedValue({ ok: false })

    await expect(authService.refreshTokens()).rejects.toThrow('No refresh token available')
  })
})

describe('authentication', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetAllMocks()
    setActivePinia(createPinia())
  })

  it('should login and store tokens', async () => {
    ;(fetch as Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access_token: '123', refresh_token: '321' }),
    })

    await useAuthStore().login('a@a.com', 'password')

    expect(useAuthStore().isAuthenticated).toBe(true)
    expect(authService.getAccessToken()).toBe('123')
    expect(authService.getRefreshToken()).toBe('321')
  })

  it('should throw on login with invalid credentials', async () => {
    ;(fetch as Mock).mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
      json: () => Promise.resolve({ error: 'invalid credentials' }),
    })

    await expect(useAuthStore().login('a@a.com', 'password')).rejects.toThrow('Unauthorized')

    expect(useAuthStore().isAuthenticated).toBe(false)
    expect(authService.getAccessToken()).toBeNull()
    expect(authService.getRefreshToken()).toBeNull()
  })
})
