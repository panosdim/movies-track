import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'movies',
    pathMatch: 'full',
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./features/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'movies',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/movies/movies.component').then((m) => m.MoviesComponent),
  },
];
