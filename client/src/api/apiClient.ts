import { clearTokens, getAccessToken, refreshTokens } from './authService'

interface FetchOptions extends RequestInit {
  _retry?: boolean
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

export const apiFetch = async (
  input: RequestInfo,
  options: FetchOptions = {},
  handleTokensRefresh = true,
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

  // TODO maybe I should create apiFetchWithRefresh?
  if (handleTokensRefresh && response.status === 401 && !options._retry) {
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
      const newAccessToken = (await refreshTokens()).accessToken
      isRefreshing = false
      resolveQueue(null, newAccessToken)

      return apiFetch(input, {
        ...options,
        headers: {
          ...headers,
          Authorization: `Bearer ${newAccessToken}`,
        },
      })
    } catch (err) {
      isRefreshing = false
      resolveQueue(err as Error)
      clearTokens()
      // todo redirect to login?
      throw err
    }
  }

  if (!response.ok) {
    const errData = await response.json().catch(() => ({}))
    const err: AnnotatedError = new Error(response.statusText || 'Request failed')
    err.status = response.status
    err.data = errData
    throw err
  }

  return response
}
