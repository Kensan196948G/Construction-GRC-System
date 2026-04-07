import apiClient from '@/api/client'

export interface UserProfile {
  id: number
  username: string
  email: string
  first_name: string
  last_name: string
  role: string
  role_display: string
  department: string
  display_name: string
  phone: string
  is_active: boolean
  totp_enabled: boolean
  date_joined: string
  last_login: string | null
}

export interface TOTP2FASetupResponse {
  secret: string
  provisioning_uri: string
  qr_code_base64: string
}

export interface TOTP2FAVerifyRequest {
  token: string
}

export interface TOTP2FAMessageResponse {
  message: string
}

/** ログインユーザーのプロフィール取得 */
export async function getUserProfile(): Promise<UserProfile> {
  const response = await apiClient.get<UserProfile>('/api/v1/auth/profile/')
  return response.data
}

/** 2FA セットアップ開始 (QRコード + シークレット取得) */
export async function setup2FA(): Promise<TOTP2FASetupResponse> {
  const response = await apiClient.post<TOTP2FASetupResponse>('/api/v1/auth/2fa/setup/')
  return response.data
}

/** 2FA 検証 & 有効化 (6桁トークン) */
export async function verify2FA(token: string): Promise<TOTP2FAMessageResponse> {
  const response = await apiClient.post<TOTP2FAMessageResponse>('/api/v1/auth/2fa/verify/', {
    token,
  } satisfies TOTP2FAVerifyRequest)
  return response.data
}

/** 2FA 無効化 */
export async function disable2FA(): Promise<TOTP2FAMessageResponse> {
  const response = await apiClient.post<TOTP2FAMessageResponse>('/api/v1/auth/2fa/disable/')
  return response.data
}
