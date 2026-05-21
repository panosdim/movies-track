import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { providePrimeNG } from 'primeng/config';
import Aura from '@primeuix/themes/aura';
import { definePreset } from '@primeuix/themes';

import { routes } from './app.routes';
import { camelcaseInterceptor, authInterceptor } from '@core/interceptors';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    provideHttpClient(withInterceptors([camelcaseInterceptor, authInterceptor])),
    providePrimeNG({
      theme: {
        preset: definePreset(Aura, {
          components: {
            menubar: {
              root: {
                padding: '1rem 1.5rem',
              },
            },
          },
        }),
      },
    }),
  ],
};
