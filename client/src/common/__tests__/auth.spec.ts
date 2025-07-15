import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest'
import * as auth from '@/common/auth'
import { useAuthStore } from '@/stores/auth'
import { createPinia, setActivePinia } from 'pinia'

global.fetch = vi.fn()

describe('auth', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetAllMocks()
  })

  it('stores and retrieves tokens from localStorage', () => {
    auth.setTokens({ accessToken: '123', refreshToken: '321' })
    expect(auth.getAccessToken()).toBe('123')
    expect(auth.getRefreshToken()).toBe('321')
  })

  it('removes token on clearTokens', () => {
    auth.setTokens({ accessToken: '123', refreshToken: '321' })
    auth.clearTokens()
    expect(auth.getAccessToken()).toBeNull()
    expect(auth.getRefreshToken()).toBeNull()
  })

  it('refreshes token correctly', async () => {
    auth.setTokens({ accessToken: 'old_access_token', refreshToken: 'old_refresh_token' })

    const accessToken = 'new_access_token'
    const refreshToken = 'new_refresh_token'

    ;(fetch as Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access_token: accessToken, refresh_token: refreshToken }),
    })

    const tokens = await auth.refreshTokens()
    expect(tokens.accessToken).toBe(accessToken)
    expect(tokens.refreshToken).toBe(refreshToken)
  })

  it('throws on failed refresh', async () => {
    auth.setTokens({ accessToken: '123', refreshToken: '321' })
    ;(fetch as Mock).mockResolvedValue({ ok: false })

    await expect(auth.refreshTokens()).rejects.toThrow('Tokens refresh failed')
  })

  it('throws on refresh attempt with no refresh token available', async () => {
    ;(fetch as Mock).mockResolvedValue({ ok: false })

    await expect(auth.refreshTokens()).rejects.toThrow('No refresh token available')
  })
})

describe('authentication', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.resetAllMocks()
    setActivePinia(createPinia())
  })

  it('logins and stores tokens', async () => {
    ;(fetch as Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ access_token: '123', refresh_token: '321' }),
    })

    await useAuthStore().login('a@a.com', 'password')

    expect(auth.getAccessToken()).toBe('123')
    expect(auth.getRefreshToken()).toBe('321')
  })

  it('throws on login with invalid credentials', async () => {
    ;(fetch as Mock).mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
      json: () => Promise.resolve({ error: 'invalid credentials' }),
    })

    await expect(useAuthStore().login('a@a.com', 'password')).rejects.toThrow('Unauthorized')

    expect(auth.getAccessToken()).toBeNull()
    expect(auth.getRefreshToken()).toBeNull()
  })
})
