const ACCESS_KEY = 'access_token'
const REFRESH_KEY = 'refresh_token'

export interface TokenPair {
  accessToken: string
  refreshToken: string
}

export interface TokenPairResponse {
  access_token: string
  refresh_token: string
}

export const getAccessToken = (): string | null => {
  return localStorage.getItem(ACCESS_KEY)
}

export const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_KEY)
}

export const setTokens = (tokens: TokenPair): void => {
  localStorage.setItem(ACCESS_KEY, tokens.accessToken)
  localStorage.setItem(REFRESH_KEY, tokens.refreshToken)
}

export const clearTokens = (): void => {
  localStorage.removeItem(ACCESS_KEY)
  localStorage.removeItem(REFRESH_KEY)
}

export const refreshTokens = async (): Promise<TokenPair> => {
  const token = getRefreshToken()
  if (!token) throw new Error('No refresh token available')

  const response = await fetch('/api/auth/refresh/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh_token: token }),
  })

  if (!response.ok) throw new Error('Tokens refresh failed')

  const data: TokenPairResponse = await response.json()
  const tokens: TokenPair = { accessToken: data.access_token, refreshToken: data.refresh_token }
  setTokens(tokens)
  return tokens
}
