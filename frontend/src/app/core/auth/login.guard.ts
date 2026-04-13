import { inject } from "@angular/core";
import { CanActivateFn, Router } from "@angular/router";

import { AuthService } from "./auth.service";

export const loginGuard: CanActivateFn = () => {
    const auth = inject(AuthService);
    const router = inject(Router);
    return auth.isLoggedIn() ? router.createUrlTree(['/products']) : true;
};