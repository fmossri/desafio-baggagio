import { Component, inject } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { ToastModule } from 'primeng/toast';

import { AuthService } from './core/auth/auth.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ButtonModule, ToastModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
    readonly auth = inject(AuthService);
    private readonly router = inject(Router);

    logout(): void {
        this.auth.logout();
        void this.router.navigate(['/login']);
    }
}
