import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { LoginRequest, TokenResponse, UserMe } from '../models/auth.models';

const TOKEN_KEY = 'access_token';

@Injectable({ providedIn: 'root' })
export class AuthService {
    private readonly http = inject(HttpClient);
    private readonly router = inject(Router);

    private readonly userSubject = new BehaviorSubject<UserMe | null>(null);
    readonly user$ = this.userSubject.asObservable();

    getAccessToken(): string | null {
        return sessionStorage.getItem(TOKEN_KEY);
    }

    isLoggedIn(): boolean {
        return !!this.getAccessToken();
    }

    login(body: LoginRequest): Observable<TokenResponse> {
        return this.http
            .post<TokenResponse>(`${environment.apiUrl}/auth/login`, body)
            .pipe(tap((res) => sessionStorage.setItem(TOKEN_KEY, res.access_token)));
    }

    logout(): void {
        sessionStorage.removeItem(TOKEN_KEY);
        this.userSubject.next(null);
    }

    loadMe(): Observable<UserMe> {
        return this.http
            .get<UserMe>(`${environment.apiUrl}/auth/me`)
            .pipe(tap((user) => this.userSubject.next(user)));
    }
}