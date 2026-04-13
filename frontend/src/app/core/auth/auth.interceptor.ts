import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, switchMap, throwError } from 'rxjs';

import { AuthService } from './auth.service';

function isAuthPublicUrl(url: string): boolean {
    return (
        url.includes('/auth/login') ||
        url.includes('/auth/refresh') ||
        url.includes('/auth/logout')
    );
}

export const authInterceptor: HttpInterceptorFn = (request, next) => {
    const auth = inject(AuthService);
    const router = inject(Router);

    const token = auth.getAccessToken();
    const authReq = 
        token && !request.headers.has('Authorization')
        ? request.clone({ setHeaders: { Authorization: `Bearer ${token}` } })
        : request;

    return next(authReq).pipe(
        catchError((error: HttpErrorResponse) => {
            if (error.status !== 401 || isAuthPublicUrl(request.url)) {
                return throwError(() => error);
            }
            return auth.refreshAccess().pipe(
                switchMap(() => {
                    const newToken = auth.getAccessToken();
                    const retry = request.clone({
                        setHeaders: newToken ? { Authorization: `Bearer ${newToken}` } : {},
                    });
                    return next(retry);
                }),
                catchError(() => {
                    auth.clearLocalSession();
                    void router.navigate(['/login']);
                    return throwError(() => error);
                }),
            );
        }),
    );
};