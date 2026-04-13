import { HttpInterceptorFn, HttpErrorResponse } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';

import { AuthService } from './auth.service';

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
            const isLogin = request.url.includes('/auth/login');
            if (error.status === 401 && !isLogin) {
                auth.logout();
                void router.navigate(['/login']);
            }
            return throwError(() => error);
        })
    );
}