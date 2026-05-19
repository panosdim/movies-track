import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CardModule } from 'primeng/card';
import { ButtonModule } from 'primeng/button';
import { TagModule } from 'primeng/tag';
import { RatingModule } from 'primeng/rating';
import { FormsModule } from '@angular/forms';
import { MoviesService } from '../../../core/services/movies.service';
import { Movie } from '../../../core/models/movie.model';

@Component({
  selector: 'app-movies-watched',
  standalone: true,
  imports: [CommonModule, CardModule, ButtonModule, TagModule, RatingModule, FormsModule],
  templateUrl: './movies-watched.component.html',
  styleUrl: './movies-watched.component.scss',
})
export class MoviesWatchedComponent implements OnInit {
  private readonly moviesService = inject(MoviesService);

  movies = signal<Movie[]>([]);
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