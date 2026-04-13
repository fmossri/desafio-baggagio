export interface LoginRequest {
    email: string;
    password: string;
}

export interface TokenResponse {
    access_token: string;
    token_type: string;
}

export interface UserMe {
    id: string;
    email: string;
    is_active: boolean;
}