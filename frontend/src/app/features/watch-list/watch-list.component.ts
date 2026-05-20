import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { RatingModule } from 'primeng/rating';
import { FormsModule } from '@angular/forms';
import { MoviesService } from '../../core/services/movies.service';
import { WatchlistMovie } from '../../core/models/movie.model';
import { WatchListMovieCard } from '../../core/components/watch-list-movie-card/watch-list-movie-card';
import { MobileWatchListMovieCard } from '../../core/components/mobile-watch-list-movie-card/mobile-watch-list-movie-card';

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
    WatchListMovieCard,
    MobileWatchListMovieCard,
  ],
  templateUrl: './watch-list.component.html',
  styleUrl: './watch-list.component.scss',
})
export class WatchListComponent implements OnInit {
  private readonly moviesService = inject(MoviesService);

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
}
