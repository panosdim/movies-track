import { Component, input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { RatingModule } from 'primeng/rating';
import { environment } from '@environments';
import { WatchedMovie } from '@core/models';

@Component({
  selector: 'app-watched-movie-card',
  imports: [CardModule, ButtonModule, RatingModule, FormsModule],
  templateUrl: './watched-movie-card.html',
  styleUrl: './watched-movie-card.scss',
})
export class WatchedMovieCard {
  movie = input.required<WatchedMovie>();

  protected readonly imageBaseUrl = environment.imageBaseUrl;
}
