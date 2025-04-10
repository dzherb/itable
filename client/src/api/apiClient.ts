import { clearTokens, getAccessToken, refreshToken } from './authService'

interface FetchOptions extends RequestInit {
  _retry?: boolean
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

export const apiFetch = async (
  input: RequestInfo,
  options: FetchOptions = {},
): Promise<Response> => {
  const token = getAccessToken()

  const headers: HeadersInit = {
    ...options.headers,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    'Content-Type': 'application/json',
  }

  const fetchOptions: RequestInit = {
    ...options,
    headers,
  }

  const response = await fetch(input, fetchOptions)

  if (response.status === 401 && !options._retry) {
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

    try {
      const newToken = await refreshToken()
      isRefreshing = false
      resolveQueue(null, newToken)

      return apiFetch(input, {
        ...options,
        headers: {
          ...headers,
          Authorization: `Bearer ${newToken}`,
        },
      })
    } catch (err) {
      isRefreshing = false
      resolveQueue(err as Error)
      clearTokens()
      throw err
    }
  }

  return response
}
