import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { MessageService } from 'primeng/api';
import { environment } from '@environments';
import {
  MobileWatchListMovieCard,
  MoviesService,
  TmdbMovie,
  TmdbPopularResponse,
  WatchListMovieCard,
  WatchedMovie,
  WatchlistMovie,
} from '@core';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { ToastModule } from 'primeng/toast';
import { forkJoin } from 'rxjs';

interface MovieAutocompleteSuggestion {
  title: string;
  releaseDate: string | null;
  posterUrl: string;
}

type SearchQueryValue = string | MovieAutocompleteSuggestion | null;

@Component({
  selector: 'app-add-movie',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    AutoCompleteModule,
    WatchListMovieCard,
    MobileWatchListMovieCard,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './add-movie.component.html',
  styleUrl: './add-movie.component.scss',
})
export class AddMovieComponent implements OnInit {
  private readonly http = inject(HttpClient);
  private readonly moviesService = inject(MoviesService);
  private readonly router = inject(Router);
  private readonly messageService = inject(MessageService);

  searchQuery = signal('');
  autocompleteSuggestions = signal<MovieAutocompleteSuggestion[]>([]);
  searchResults = signal<TmdbMovie[]>([]);
  loading = signal(false);
  isMobile = signal(false);
  existingMovieIds = signal<Set<number>>(new Set());

  watchlistSearchResults = computed<WatchlistMovie[]>(() =>
    this.searchResults().map((movie) => this.mapToWatchlistMovie(movie)),
  );

  ngOnInit(): void {
    const mediaQuery = window.matchMedia('(max-width: 960px)');
    this.isMobile.set(mediaQuery.matches);
    mediaQuery.addEventListener('change', (e) => this.isMobile.set(e.matches));
    this.loadExistingMovieIds();
  }

  private loadExistingMovieIds(): void {
    forkJoin({
      watchlist: this.moviesService.getWatchlist(),
      watched: this.moviesService.getWatched(),
    }).subscribe({
      next: ({ watchlist, watched }) => {
        this.existingMovieIds.set(this.collectMovieIds(watchlist, watched));
      },
      error: () => {
        this.existingMovieIds.set(new Set());
      },
    });
  }

  private collectMovieIds(watchlist: WatchlistMovie[], watched: WatchedMovie[]): Set<number> {
    return new Set(
      [...watchlist, ...watched]
        .map((movie) => movie.movieId)
        .filter((movieId): movieId is number => movieId !== null),
    );
  }

  updateSearchQuery(value: SearchQueryValue): void {
    const normalizedValue = this.normalizeSearchQuery(value);
    this.searchQuery.set(normalizedValue);

    if (!normalizedValue.trim()) {
      this.clearSearchState();
    }
  }

  private normalizeSearchQuery(value: SearchQueryValue): string {
    if (typeof value === 'string') {
      return value;
    }

    if (value && typeof value === 'object' && 'title' in value) {
      return value.title;
    }

    return '';
  }

  clearSearchState(): void {
    this.autocompleteSuggestions.set([]);
    this.searchResults.set([]);
    this.loading.set(false);
  }

  loadAutocompleteSuggestions(query: string | null): void {
    const trimmedQuery = this.normalizeSearchQuery(query).trim();

    if (trimmedQuery.length < 2) {
      this.autocompleteSuggestions.set([]);
      return;
    }

    this.http
      .post<[string, string | null, string][]>(environment.autocompleteUrl(), {
        term: trimmedQuery,
      })
      .subscribe({
        next: (results) => {
          this.autocompleteSuggestions.set(
            results.map(([title, releaseDate, posterUrl]) => ({
              title,
              releaseDate,
              posterUrl,
            })),
          );
        },
        error: () => {
          this.autocompleteSuggestions.set([]);
        },
      });
  }

  searchMovies(query: SearchQueryValue): void {
    const trimmedQuery = this.normalizeSearchQuery(query).trim();

    if (trimmedQuery.length < 2) {
      this.clearSearchState();
      return;
    }

    this.loading.set(true);
    this.http.post<TmdbPopularResponse>(environment.searchUrl(), { term: trimmedQuery }).subscribe({
      next: (data) => {
        this.searchResults.set(data.results || []);
        this.loading.set(false);
      },
      error: () => {
        this.searchResults.set([]);
        this.loading.set(false);
      },
    });
  }

  onEnter(): void {
    this.searchMovies(this.searchQuery());
  }

  onSuggestionSelect(suggestion: MovieAutocompleteSuggestion): void {
    this.searchQuery.set(suggestion.title);
    this.searchMovies(suggestion.title);
  }

  isAddToWatchlistDisabled(movieId: number): boolean {
    return this.existingMovieIds().has(movieId);
  }

  addToWatchlist(movie: WatchlistMovie): void {
    if (this.isAddToWatchlistDisabled(movie.movieId)) {
      return;
    }

    this.moviesService
      .addToWatchlist({
        movieId: movie.movieId,
        title: movie.title,
        poster: movie.poster,
      })
      .subscribe({
        next: () => {
          this.existingMovieIds.update((movieIds) => new Set(movieIds).add(movie.movieId));
          this.router.navigate(['/watchlist']);
        },
        error: () => {
          this.messageService.add({
            severity: 'error',
            summary: 'Unable to add movie',
            detail:
              'Something went wrong while adding this movie to your watchlist. Please try again.',
            life: 4000,
          });
        },
      });
  }

  private mapToWatchlistMovie(movie: TmdbMovie): WatchlistMovie {
    return {
      id: movie.id,
      movieId: movie.id,
      title: movie.title,
      poster: movie.posterPath,
      providers: [],
      voteAverage: movie.voteAverage,
    };
  }
}
