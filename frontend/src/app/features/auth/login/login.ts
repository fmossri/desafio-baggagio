import { Component, inject } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { ButtonModule } from 'primeng/button';
import { InputTextModule } from 'primeng/inputtext';
import { PasswordModule } from 'primeng/password';
import { AuthService } from '../../../core/auth/auth.service';

import { UserNotifyService } from '../../../core/notify/user-notify.service';


@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    ButtonModule,
    InputTextModule,
    PasswordModule,
  ],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
    private readonly fb = inject(FormBuilder);
    private readonly auth = inject(AuthService);
    private readonly router = inject(Router);
    private readonly notify = inject(UserNotifyService);

    readonly form = this.fb.nonNullable.group({
        email: ['', [Validators.required, Validators.email]],
        password: ['', [Validators.required]],
    });

    loading = false;

    submit(): void {
        if (this.form.invalid) {
            this.form.markAllAsTouched();
            return;
        }
        this.loading = true;
        this.auth.login(this.form.getRawValue()).subscribe({
            next: () => {
                this.auth.loadMe().subscribe({
                    next: () => {
                        this.loading = false;
                        void this.router.navigateByUrl('/products');
                    },
                    error: (err: unknown) => {
                        this.loading = false;
                        this.auth.logout();
                        this.notify.error(err, { skip401: true });
                    },
                });
            },
            error: () => {
                this.loading = false;
                this.notify.errorText('Autenticação',"Não foi possível autenticar. Verifique suas credenciais e tente novamente.");
            },
        });
    }
}
