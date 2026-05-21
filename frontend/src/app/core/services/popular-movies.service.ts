import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '@environments';
import { TmdbPopularResponse } from '@core/models';

@Injectable({ providedIn: 'root' })
export class PopularMoviesService {
  private readonly http = inject(HttpClient);

  getPopularMovies(): Observable<TmdbPopularResponse> {
    return this.http.get<TmdbPopularResponse>(environment.popularUrl());
  }
}
