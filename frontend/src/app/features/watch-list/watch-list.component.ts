import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { RatingModule } from 'primeng/rating';
import { FormsModule } from '@angular/forms';
import { MoviesService } from '../../core/services/movies.service';
import { WatchlistMovie } from '../../core/models/movie.model';

@Component({
  selector: 'app-watchlist',
  standalone: true,
  imports: [CommonModule, CardModule, ButtonModule, TagModule, RatingModule, FormsModule],
  templateUrl: './watch-list.component.html',
  styleUrl: './watch-list.component.scss',
})
export class WatchListComponent implements OnInit {
  private readonly moviesService = inject(MoviesService);

  movies = signal<WatchlistMovie[]>([]);
  loading = signal(false);

  ngOnInit(): void {
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
