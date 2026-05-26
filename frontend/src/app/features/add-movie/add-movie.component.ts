import { Component, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '@environments';
import { TmdbMovie } from '@core/models';
import { AutoCompleteModule } from 'primeng/autocomplete';
import { CardModule } from 'primeng/card';
import { ProgressBarModule } from 'primeng/progressbar';
import { ButtonModule } from 'primeng/button';

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
  searchResults = signal<TmdbMovie[]>([]);
  loading = signal(false);

  searchMovies(query: string): void {
    if (!query || query.length < 2) {
      this.searchResults.set([]);
      return;
    }

    this.loading.set(true);
    this.http
      .get<any>(environment.searchUrl() + `?query=${encodeURIComponent(query)}`)
      .subscribe({
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

  protected readonly Math = Math;
}
