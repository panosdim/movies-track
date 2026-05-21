import { CommonModule } from '@angular/common';
import { Component, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
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
    WatchedMovieCard,
    MobileWatchewatdMovieCard
],
  templateUrl: './watched-movies.component.html',
  styleUrl: './watched-movies.component.scss',
})
export class WatchedMoviesComponent implements OnInit {
  private readonly moviesService = inject(MoviesService);

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
}
