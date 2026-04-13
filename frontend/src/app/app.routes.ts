import { Routes } from '@angular/router';

import { authGuard } from './core/auth/auth.guard';
import { Login } from './features/auth/login/login';
import { ProductList } from './features/products/product-list/product-list';

export const routes: Routes = [
    { path: '', pathMatch: 'full', redirectTo: 'products' },
    { path: 'login', component: Login },
    { path: 'products', component: ProductList, canActivate: [authGuard] },
    { path: '**', redirectTo: 'products' },
];
