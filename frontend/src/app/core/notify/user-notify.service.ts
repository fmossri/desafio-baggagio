import { inject, Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { MessageService } from 'primeng/api';
import { httpErrorToUserMessage } from '../http/http-error-message';

@Injectable({ providedIn: 'root' })
export class UserNotifyService {
    private readonly messages = inject(MessageService);
    private readonly toastKey = 'app';

    success(summary: string, detail: string): void {
        this.messages.add({ key: this.toastKey, severity: 'success', summary, detail, life: 4000 });
    }

    error(err: unknown, options?: { skip401?: boolean }): void {
        if (
            options?.skip401 &&
            err instanceof HttpErrorResponse &&
            err.status === 401
        ) {
            return;
        }
        const message = httpErrorToUserMessage(err);
        this.messages.add({ 
            key: this.toastKey, 
            severity: message.severity,
            summary: message.summary, 
            detail: message.detail, 
            life: 4000,
        });
    }

    errorText(summary: string, detail: string): void {
        this.messages.add({ key: this.toastKey, severity: 'error', summary, detail, life: 4000 });
    }
}