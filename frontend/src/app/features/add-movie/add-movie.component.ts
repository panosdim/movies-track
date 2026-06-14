import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments';
import { TmdbMovie, TmdbPopularResponse } from '@core/models';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { CardModule } from 'primeng/card';
import { ProgressBarModule } from 'primeng/progressbar';
import { ButtonModule } from 'primeng/button';

interface MovieAutocompleteSuggestion {
  title: string;
  releaseDate: string | null;
  posterUrl: string;
}

@Component({
  selector: 'app-add-movie',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    AutoCompleteModule,
    CardModule,
    ProgressBarModule,
    ButtonModule,
  ],
  templateUrl: './add-movie.component.html',
  styleUrl: './add-movie.component.scss',
})
export class AddMovieComponent {
  private readonly http = inject(HttpClient);

  searchQuery = signal('');
  autocompleteSuggestions = signal<MovieAutocompleteSuggestion[]>([]);
  searchResults = signal<TmdbMovie[]>([]);
  loading = signal(false);

  updateSearchQuery(value: string | null): void {
    const normalizedValue = value ?? '';
    this.searchQuery.set(normalizedValue);

    if (!normalizedValue.trim()) {
      this.clearSearchState();
    }
  }

  clearSearchState(): void {
    this.autocompleteSuggestions.set([]);
    this.searchResults.set([]);
    this.loading.set(false);
  }

  loadAutocompleteSuggestions(query: string | null): void {
    const trimmedQuery = (query ?? '').trim();

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

  searchMovies(query: string | null): void {
    const trimmedQuery = (query ?? '').trim();

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

  protected readonly Math = Math;
}
