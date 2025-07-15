import { clearTokens, getAccessToken, refreshTokens, type TokenPair } from './auth.ts'
import { eventBus } from '@/events/bus.ts'

interface FetchOptions extends RequestInit {
  _retry?: boolean
  handleRefresh?: boolean
}

interface AnnotatedError extends Error {
  status?: number
  data?: unknown
}

let isRefreshing = false
let queue: Array<{
  requestFn: (token: string) => Promise<Response>
  resolve: (value: Response | PromiseLike<Response>) => void
  reject: (reason?: unknown) => void
}> = []

const queueRequest = (requestFn: (token: string) => Promise<Response>): Promise<Response> => {
  return new Promise((resolve, reject) => {
    queue.push({ requestFn, resolve, reject })
  })
}

const resolveQueue = (error: Error | null, token?: string): void => {
  queue.forEach(({ requestFn, resolve, reject }) => {
    if (error || !token) reject(error)
    else resolve(requestFn(token))
  })
  queue = []
}

// Обертка над fetch, которая:
// 1. При получении 401 пытается сделать refresh токенов (вероятнее всего access-токен протух)
// 2. Ставит запрос в очередь, если в этот момент уже делаем refresh
// 3. Если refresh не удался, то разрешит все запросы из очереди с ошибкой
// 4. При любом другом статусе > 400 кидает ошибку
export const apiFetch = async (
  input: RequestInfo,
  options: FetchOptions = {},
): Promise<Response> => {
  const token = getAccessToken()

  const headers: HeadersInit = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    'Content-Type': 'application/json',
    ...options.headers,
  }

  const fetchOptions: RequestInit = {
    ...options,
    headers,
  }

  const response = await fetch(input, fetchOptions)

  const handleRefresh = options?.handleRefresh ?? true
  const shouldRefresh = handleRefresh && response.status === 401 && !options._retry
  if (shouldRefresh) {
    if (isRefreshing) {
      return queueRequest((newToken) =>
        apiFetch(input, {
          ...options,
          _retry: true,
          headers: {
            ...headers,
            Authorization: `Bearer ${newToken}`,
          },
        }),
      )
    }

    options._retry = true
    isRefreshing = true

    let newTokenPair: TokenPair
    try {
      newTokenPair = await refreshTokens()
      resolveQueue(null, newTokenPair.accessToken)
    } catch (err) {
      resolveQueue(err as Error)
      clearTokens()
      eventBus.emit('tokenRefreshFailed', err as Error)
      throw err
    } finally {
      isRefreshing = false
    }

    eventBus.emit('tokenRefreshSucceed', newTokenPair)

    return await apiFetch(input, {
      ...options,
      headers: {
        ...headers,
        Authorization: `Bearer ${newTokenPair.accessToken}`,
      },
    })
  }

  if (!response.ok) {
    const errData = await response.json().catch(() => {})
    const err: AnnotatedError = new Error(response.statusText || 'Request failed')
    err.status = response.status
    err.data = errData
    throw err
  }

  return response
}

type JSONValue = null | string | number | boolean | Record<string, string> | Array<JSONValue>

export const apiV1 = {
  async get(
    url: string,
    params: Record<string, string> | null = null,
    extraOptions: FetchOptions = {},
  ): Promise<Response> {
    if (params !== null) {
      url += new URLSearchParams(params)
    }
    return await apiFetch(url, extraOptions)
  },
  async post(url: string, data: JSONValue, extraOptions: FetchOptions = {}): Promise<Response> {
    return await apiFetch(url, {
      method: 'POST',
      body: JSON.stringify(data),
      ...extraOptions,
    })
  },
  async put(url: string, data: JSONValue, extraOptions: FetchOptions = {}): Promise<Response> {
    return await apiFetch(url, {
      method: 'PUT',
      body: JSON.stringify(data),
      ...extraOptions,
    })
  },
  async patch(url: string, data: JSONValue, extraOptions: FetchOptions = {}): Promise<Response> {
    return await apiFetch(url, {
      method: 'PATCH',
      body: JSON.stringify(data),
      ...extraOptions,
    })
  },
  async delete(url: string, extraOptions: FetchOptions = {}): Promise<Response> {
    return await apiFetch(url, {
      method: 'DELETE',
      ...extraOptions,
    })
  },
}
