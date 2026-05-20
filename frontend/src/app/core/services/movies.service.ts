import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { WatchedMovie, WatchlistMovie } from '../models/movie.model';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class MoviesService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = 'http://localhost:8000/api/v1/movies';

  getWatchlist(): Observable<WatchlistMovie[]> {
    return this.http.get<WatchlistMovie[]>(environment.watchlistUrl());
  }

  getWatched(): Observable<WatchedMovie[]> {
    return this.http.get<WatchedMovie[]>(environment.watchedMoviesUrl());
  }
}
