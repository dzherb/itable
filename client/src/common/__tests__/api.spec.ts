import { describe, it, expect, vi, beforeEach, type Mock } from 'vitest'
import * as auth from '@/common/auth'
import { apiFetch } from '@/common/api'
import { eventBus } from '@/events/bus.ts'

global.fetch = vi.fn()

describe('apiFetch', () => {
  beforeEach(() => {
    vi.resetAllMocks()
    localStorage.clear()
    eventBus.all.clear()
  })

  it('adds Authorization header when access token is present', async () => {
    auth.setTokens({ accessToken: 'abc123', refreshToken: 'abc321' })
    ;(fetch as Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    })

    const result = await apiFetch('/api/test/').then((r) => r.json())

    expect(result).toEqual({ success: true })

    const call = (fetch as Mock).mock.calls[0]
    const headers = new Headers(call[1]?.headers)
    expect(headers.get('Authorization')).toBe('Bearer abc123')
  })

  it('throws error on non-OK response (e.g. 403)', async () => {
    auth.setTokens({ accessToken: 'abc123', refreshToken: 'abc321' })
    ;(fetch as Mock).mockResolvedValueOnce({
      ok: false,
      status: 403,
      json: () => Promise.resolve({}),
    })

    await expect(apiFetch('/api/test')).rejects.toThrow('Request failed')
  })

  it('attempts refresh and retries on 401', async () => {
    const eventHandler = vi.fn()
    eventBus.on('tokenRefreshSucceed', eventHandler)

    auth.setTokens({ accessToken: 'abc123', refreshToken: 'abc321' })
    ;(fetch as Mock)
      // 1st call — original request returns 401
      .mockResolvedValueOnce({
        status: 401,
        ok: false,
        json: () => Promise.resolve({}),
      })
      // 2nd call — refresh request succeeds
      .mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({ access_token: 'new_access_token', refresh_token: 'new_refresh_token' }),
      })
      // 3rd call — retried request succeeds
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ result: 'ok' }),
      })

    const result = await apiFetch('/api/secure').then((r) => r.json())

    expect(result).toEqual({ result: 'ok' })

    expect(auth.getAccessToken()).toBe('new_access_token')
    expect(auth.getRefreshToken()).toBe('new_refresh_token')

    const thirdCall = (fetch as Mock).mock.calls[2]
    const headers = new Headers(thirdCall[1]?.headers)
    expect(headers.get('Authorization')).toBe('Bearer new_access_token')

    expect(eventHandler).toHaveBeenCalledOnce()
    expect(eventHandler).toHaveBeenCalledWith({
      accessToken: 'new_access_token',
      refreshToken: 'new_refresh_token',
    })
  })

  it('fails if refresh also fails', async () => {
    const eventHandler = vi.fn()
    eventBus.on('tokenRefreshFailed', eventHandler)

    auth.setTokens({ accessToken: '123', refreshToken: '321' })
    ;(fetch as Mock).mockResolvedValue({
      ok: false,
      status: 401,
      json: () => Promise.resolve({}),
    })

    await expect(apiFetch('/api/secure')).rejects.toThrow('Tokens refresh failed')
    expect(eventHandler).toHaveBeenCalledOnce()
  })

  it('throws if no refresh token found', async () => {
    const eventHandler = vi.fn()
    eventBus.on('tokenRefreshFailed', eventHandler)
    ;(fetch as Mock).mockResolvedValueOnce({ status: 401, ok: false })

    await expect(apiFetch('/api/secure')).rejects.toThrow('No refresh token available')
    expect(eventHandler).toHaveBeenCalledOnce()
  })

  it('refreshes once when multiple requests receive 401 simultaneously', async () => {
    const eventHandler = vi.fn()
    eventBus.on('tokenRefreshSucceed', eventHandler)

    auth.setTokens({ accessToken: 'expired_token', refreshToken: 'refresh_token' })

    const fetchMock = fetch as Mock

    fetchMock.mockImplementation((url: string, options: RequestInit) => {
      const authHeader = (options?.headers as Record<string, string>)?.Authorization

      if (url === '/api/auth/refresh/')
        return Promise.resolve({
          ok: true,
          json: () =>
            Promise.resolve({
              access_token: 'new_access_token',
              refresh_token: 'new_refresh_token',
            }),
        })

      if (url === '/api/data1/' && authHeader === 'Bearer new_access_token')
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ result: 'request1' }),
        })

      if (url === '/api/data2/' && authHeader === 'Bearer new_access_token')
        return Promise.resolve({
          ok: true,
          json: () => Promise.resolve({ result: 'request2' }),
        })

      if (url === '/api/data1/' || url === '/api/data2/')
        return Promise.resolve({
          ok: false,
          status: 401,
          json: () => Promise.resolve({}),
        })
    })

    const [res1, res2] = await Promise.all([
      apiFetch('/api/data1/').then((r) => r.json()),
      apiFetch('/api/data2/').then((r) => r.json()),
    ])

    expect(res1).toEqual({ result: 'request1' })
    expect(res2).toEqual({ result: 'request2' })

    // Убеждаемся, что refresh был вызван лишь однажды,
    // как и emit соответствующего события
    const refreshCalls = fetchMock.mock.calls.filter(([url]) => url === '/api/auth/refresh/')
    expect(refreshCalls.length).toBe(1)
    expect(eventHandler).toHaveBeenCalledOnce()
  })

  it('fails all requests when refresh fails after multiple 401s', async () => {
    const eventHandler = vi.fn()
    eventBus.on('tokenRefreshFailed', eventHandler)

    auth.setTokens({ accessToken: 'expired_token', refreshToken: 'refresh_token' })

    const fetchMock = fetch as Mock

    fetchMock.mockImplementation((url: string) => {
      if (url === '/api/auth/refresh/') {
        return Promise.resolve({
          ok: false,
          status: 403,
          json: () => Promise.resolve({ detail: 'Invalid refresh token' }),
        })
      }

      if (url === '/api/data1/' || url === '/api/data2/') {
        return Promise.resolve({
          ok: false,
          status: 401,
          json: () => Promise.resolve({}),
        })
      }

      return Promise.reject(new Error(`Unhandled URL: ${url}`))
    })

    const results = await Promise.allSettled([apiFetch('/api/data1/'), apiFetch('/api/data2/')])

    for (const result of results) {
      expect(result.status).toBe('rejected')
      expect((result as PromiseRejectedResult).reason).toBeInstanceOf(Error)
      expect((result as PromiseRejectedResult).reason.message).toBe('Tokens refresh failed')
    }

    const refreshCalls = fetchMock.mock.calls.filter(([url]) => url === '/api/auth/refresh/')
    expect(refreshCalls.length).toBe(1)
    expect(eventHandler).toHaveBeenCalledOnce()
  })
})
