import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { RatingModule } from 'primeng/rating';
import { FormsModule } from '@angular/forms';
import { ConfirmationService } from 'primeng/api';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { MoviesService, WatchListMovieCard, MobileWatchListMovieCard, WatchlistMovie } from '@core';

@Component({
  selector: 'app-watchlist',
  standalone: true,
  imports: [
    CommonModule,
    CardModule,
    ButtonModule,
    TagModule,
    RatingModule,
    FormsModule,
    ConfirmDialogModule,
    WatchListMovieCard,
    MobileWatchListMovieCard,
  ],
  providers: [ConfirmationService],
  templateUrl: './watch-list.component.html',
  styleUrl: './watch-list.component.scss',
})
export class WatchListComponent implements OnInit {
  private readonly moviesService = inject(MoviesService);
  private readonly confirmationService = inject(ConfirmationService);

  movies = signal<WatchlistMovie[]>([]);
  loading = signal(false);
  isMobile = signal(false);

  ngOnInit(): void {
    const mediaQuery = window.matchMedia('(max-width: 960px)');
    this.isMobile.set(mediaQuery.matches);
    mediaQuery.addEventListener('change', (e) => this.isMobile.set(e.matches));
    this.loadMovies();
  }

  loadMovies(): void {
    this.loading.set(true);
    this.moviesService.getWatchlist().subscribe({
      next: (data) => {
        this.movies.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  confirmDeleteMovie(movie: WatchlistMovie): void {
    this.confirmationService.confirm({
      header: 'Delete movie',
      message: `Are you sure you want to delete ${movie.title ?? 'this movie'} from your watchlist?`,
      icon: 'pi pi-exclamation-triangle',
      acceptButtonStyleClass: 'p-button-danger',
      acceptLabel: 'Delete',
      rejectLabel: 'Cancel',
      accept: () => this.deleteMovie(movie),
    });
  }

  markAsWatched(movie: WatchlistMovie): void {
    this.moviesService.markAsWatched(movie.id).subscribe({
      next: () => {
        this.movies.update((movies) => movies.filter((item) => item.id !== movie.id));
      },
    });
  }

  private deleteMovie(movie: WatchlistMovie): void {
    this.moviesService.deleteMovie(movie.id).subscribe({
      next: () => {
        this.movies.update((movies) => movies.filter((item) => item.id !== movie.id));
      },
    });
  }
}
