import { Component, input, output } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ProgressBarModule } from 'primeng/progressbar';
import { TooltipModule } from 'primeng/tooltip';
import { environment } from '@environments';
import { WatchlistMovie } from '@core/models';

@Component({
  selector: 'app-watch-list-movie-card',
  imports: [CardModule, ButtonModule, ProgressBarModule, TooltipModule],
  templateUrl: './watch-list-movie-card.html',
  styleUrl: './watch-list-movie-card.scss',
})
export class WatchListMovieCard {
  movie = input.required<WatchlistMovie>();
  searchMode = input(false);
  addDisabled = input(false);
  addToWatchlist = output<WatchlistMovie>();
  deleteMovie = output<WatchlistMovie>();

  protected readonly imageBaseUrl = environment.imageBaseUrl;
  protected readonly Math = Math;
}
