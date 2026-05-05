import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'movies',
    pathMatch: 'full',
  },
  {
    path: 'movies',
    loadComponent: () =>
      import('./features/movies/movies.component').then((m) => m.MoviesComponent),
  },
];
