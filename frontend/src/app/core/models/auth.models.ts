export interface LoginRequest {
    email: string;
    password: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
    refresh_token?: string | null;
}

export interface RefreshRequest {
    refresh_token: string;
}

export interface LogoutRequest {
    access_token: string;
    refresh_token?: string | null;
}

export interface UserMe {
    id: string;
    email: string;
    is_active: boolean;
}
