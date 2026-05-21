import { Component, input } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ProgressBarModule } from 'primeng/progressbar';
import { environment } from '@environments';
import { WatchlistMovie } from '@core/models';

@Component({
  selector: 'app-mobile-watch-list-movie-card',
  imports: [CardModule, ButtonModule, ProgressBarModule],
  templateUrl: './mobile-watch-list-movie-card.html',
  styleUrl: './mobile-watch-list-movie-card.scss',
})
export class MobileWatchListMovieCard {
  movie = input.required<WatchlistMovie>();

  protected readonly imageBaseUrl = environment.imageBaseUrl;
  protected readonly Math = Math;
}
