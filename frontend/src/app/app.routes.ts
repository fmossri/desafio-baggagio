import { Routes } from '@angular/router';

import { authGuard } from './core/auth/auth.guard';
import { loginGuard } from './core/auth/login.guard';
import { Login } from './features/auth/login/login';
import { ProductList } from './features/products/product-list/product-list';

export const routes: Routes = [
    { path: '', pathMatch: 'full', redirectTo: 'products' },
    { path: 'login', component: Login, canActivate: [loginGuard] },
    { path: 'products', component: ProductList, canActivate: [authGuard] },
    { path: '**', redirectTo: 'products' },
];
