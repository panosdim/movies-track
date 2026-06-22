import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '@environments';
import { WatchedMovie, WatchlistMovie } from '@core/models';

export interface AddToWatchlistRequest {
  movieId: number;
  title: string | null;
  poster: string | null;
}

export interface RateMovieRequest {
  rating: number;
}

@Injectable({ providedIn: 'root' })
export class MoviesService {
  private readonly http = inject(HttpClient);

  getWatchlist(): Observable<WatchlistMovie[]> {
    return this.http.get<WatchlistMovie[]>(environment.watchlistUrl());
  }

  getWatched(): Observable<WatchedMovie[]> {
    return this.http.get<WatchedMovie[]>(environment.watchedMoviesUrl());
  }

  addToWatchlist(movie: AddToWatchlistRequest): Observable<WatchlistMovie> {
    return this.http.post<WatchlistMovie>(environment.moviesUrl(), movie);
  }

  deleteMovie(movieId: number): Observable<void> {
    return this.http.delete<void>(`${environment.moviesUrl()}/${movieId}`);
  }

  markAsWatched(movieId: number): Observable<WatchedMovie> {
    return this.http.post<WatchedMovie>(`${environment.watchedMoviesUrl()}/${movieId}`, {});
  }

  rateMovie(movieId: number, rating: number): Observable<WatchedMovie> {
    const body: RateMovieRequest = { rating };
    return this.http.post<WatchedMovie>(`${environment.moviesUrl()}/rate/${movieId}`, body);
  }
}
