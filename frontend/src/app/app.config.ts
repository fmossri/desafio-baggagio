import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';
import { providePrimeNG } from 'primeng/config';
import { MessageService } from 'primeng/api';
import Nora from '@primeuix/themes/nora';
import { definePreset, palette } from '@primeuix/themes';

import { routes } from './app.routes';
import { authInterceptor } from './core/auth/auth.interceptor';

const AppPreset = definePreset(Nora, {
    semantic: {
      primary: palette('#3b5bdb'),
      colorScheme: {
        light: {
            surface: {
                0: '#e8eef5',
            },
            content: {
                background: '#d3dde8',
                hoverBackground: '#c5d0dc',
            },
            formField: {
                background: '#e8eef5',
                filledBackground: '#e8eef5',
            },
        },
      },
    },
});
export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true}),
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimationsAsync(),
    providePrimeNG({
        theme: {
            preset: AppPreset,
            options: { darkModeSelector: false },
        },
    }),
    MessageService,
  ],
};
