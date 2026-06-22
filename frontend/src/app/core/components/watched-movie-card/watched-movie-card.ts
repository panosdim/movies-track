import { Component, input, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { RatingModule } from 'primeng/rating';
import { TooltipModule } from 'primeng/tooltip';
import { environment } from '@environments';
import { WatchedMovie } from '@core/models';

@Component({
  selector: 'app-watched-movie-card',
  imports: [CardModule, ButtonModule, RatingModule, FormsModule, TooltipModule],
  templateUrl: './watched-movie-card.html',
  styleUrl: './watched-movie-card.scss',
})
export class WatchedMovieCard {
  movie = input.required<WatchedMovie>();
  rateMovie = output<number>();
  deleteMovie = output<WatchedMovie>();

  protected readonly imageBaseUrl = environment.imageBaseUrl;
}
