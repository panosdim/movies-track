import { Routes } from '@angular/router';
import { authGuard } from '@core/guards';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'watchlist',
    pathMatch: 'full',
  },
  {
    path: 'login',
    loadComponent: () => import('./features/login/login.component').then((m) => m.LoginComponent),
  },
  {
    path: 'watchlist',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./features/watch-list/watch-list.component').then((m) => m.WatchListComponent),
  },
    {
      path: 'watched',
      canActivate: [authGuard],
      loadComponent: () =>
        import('./features/watched-movies/watched-movies.component').then(
          (m) => m.WatchedMoviesComponent,
        ),
    },
    {
      path: 'movies/add',
      canActivate: [authGuard],
      loadComponent: () =>
        import('./features/add-movie/add-movie.component').then((m) => m.AddMovieComponent),
    },
];
