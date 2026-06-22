import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ConfirmationService } from 'primeng/api';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ConfirmDialogModule } from 'primeng/confirmdialog';
import { RatingModule } from 'primeng/rating';
import { TagModule } from 'primeng/tag';
import { WatchedMovieCard, WatchedMovie, MoviesService, MobileWatchewatdMovieCard } from '@core';

@Component({
  selector: 'app-watched-movies',
  standalone: true,
  imports: [
    CommonModule,
    CardModule,
    ButtonModule,
    TagModule,
    RatingModule,
    FormsModule,
    ConfirmDialogModule,
    WatchedMovieCard,
    MobileWatchewatdMovieCard,
  ],
  providers: [ConfirmationService],
  templateUrl: './watched-movies.component.html',
  styleUrl: './watched-movies.component.scss',
})
export class WatchedMoviesComponent implements OnInit {
  private readonly moviesService = inject(MoviesService);
  private readonly confirmationService = inject(ConfirmationService);

  movies = signal<WatchedMovie[]>([]);
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
    this.moviesService.getWatched().subscribe({
      next: (data) => {
        this.movies.set(data);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  rateMovie(movie: WatchedMovie, rating: number): void {
    this.moviesService.rateMovie(movie.id, rating).subscribe({
      next: (updatedMovie) => {
        this.movies.update((movies) =>
          movies.map((item) =>
            item.id === movie.id ? { ...item, rating: updatedMovie.rating } : item,
          ),
        );
      },
    });
  }

  confirmDeleteMovie(movie: WatchedMovie): void {
    this.confirmationService.confirm({
      header: 'Delete movie',
      message: `Are you sure you want to delete ${movie.title ?? 'this movie'} from your watched movies?`,
      icon: 'pi pi-exclamation-triangle',
      acceptButtonStyleClass: 'p-button-danger',
      acceptLabel: 'Delete',
      rejectLabel: 'Cancel',
      accept: () => this.deleteMovie(movie),
    });
  }

  private deleteMovie(movie: WatchedMovie): void {
    this.moviesService.deleteMovie(movie.id).subscribe({
      next: () => {
        this.movies.update((movies) => movies.filter((item) => item.id !== movie.id));
      },
    });
  }
}
