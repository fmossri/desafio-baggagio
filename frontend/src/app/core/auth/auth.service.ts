import { Injectable, inject } from '@angular/core';
import { HttpBackend,HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, catchError, finalize, tap, throwError } from 'rxjs';

import { environment } from '../../../environments/environment';
import { LoginRequest, LogoutRequest, TokenResponse, UserMe } from '../models/auth.models';

const ACCESS_KEY = 'access_token';
const REFRESH_KEY = 'refresh_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
    private readonly http = inject(HttpClient);
    private readonly httpBackend = inject(HttpBackend);
    private readonly httpDirect = new HttpClient(this.httpBackend);

    private readonly userSubject = new BehaviorSubject<UserMe | null>(null);
    readonly user$ = this.userSubject.asObservable();

    getAccessToken(): string | null {
        return sessionStorage.getItem(ACCESS_KEY);
    }

    getRefreshToken(): string | null {
        return sessionStorage.getItem(REFRESH_KEY);
    }


    isLoggedIn(): boolean {
        return !!this.getAccessToken();
    }

    login(body: LoginRequest): Observable<TokenResponse> {
        return this.http
            .post<TokenResponse>(`${environment.apiUrl}/auth/login`, body)
            .pipe(tap((res) => {
                sessionStorage.setItem(ACCESS_KEY, res.access_token);
                if (res.refresh_token) {
                    sessionStorage.setItem(REFRESH_KEY, res.refresh_token);
                }
            }),
        );
    }

    refreshAccess(): Observable<TokenResponse> {
        const refreshToken = this.getRefreshToken();
        if (!refreshToken) {
            return throwError(() => new Error('No refresh token found'));
        }
        return this.httpDirect.post<TokenResponse>(`${environment.apiUrl}/auth/refresh`, { refresh_token: refreshToken })
            .pipe(tap((res) => {
                sessionStorage.setItem(ACCESS_KEY, res.access_token);
                if (res.refresh_token) {
                    sessionStorage.setItem(REFRESH_KEY, res.refresh_token);
                }
            }),
        );
    }

    clearLocalSession(): void {
        sessionStorage.removeItem(ACCESS_KEY);
        sessionStorage.removeItem(REFRESH_KEY);
        this.userSubject.next(null);
    }

    logout(): void {
        const access = this.getAccessToken();
        if (!access) {
            this.clearLocalSession();
            return;
        }
        const body: LogoutRequest = {
            access_token: access,
            refresh_token: this.getRefreshToken() ?? undefined,
        };
        this.httpDirect.post(`${environment.apiUrl}/auth/logout`, body)
            .pipe(finalize(() => this.clearLocalSession()))
            .subscribe();
    }

    loadMe(): Observable<UserMe> {
        return this.http
            .get<UserMe>(`${environment.apiUrl}/auth/me`)
            .pipe(tap((user) => this.userSubject.next(user)));
    }
}