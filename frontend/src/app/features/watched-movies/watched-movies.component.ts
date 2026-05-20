import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { RatingModule } from 'primeng/rating';
import { FormsModule } from '@angular/forms';
import { MoviesService } from '../../core/services/movies.service';
import { WatchedMovie } from '../../core/models/movie.model';
import { WatchedMovieCard } from "../../core/components/watched-movie-card/watched-movie-card";

@Component({
  selector: 'app-watched-movies',
  standalone: true,
  imports: [CommonModule, CardModule, ButtonModule, TagModule, RatingModule, FormsModule, WatchedMovieCard],
  templateUrl: './watched-movies.component.html',
  styleUrl: './watched-movies.component.scss',
})
export class WatchedMoviesComponent implements OnInit {
  private readonly moviesService = inject(MoviesService);

  movies = signal<WatchedMovie[]>([]);
  loading = signal(false);

  ngOnInit(): void {
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
