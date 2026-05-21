import { Component, input } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ProgressBarModule } from 'primeng/progressbar';
import { TooltipModule } from 'primeng/tooltip';
import { environment } from '../../../../environments/environment';
import { WatchlistMovie } from '../../models/movie.model';

@Component({
  selector: 'app-watch-list-movie-card',
  imports: [CardModule, ButtonModule, ProgressBarModule, TooltipModule],
  templateUrl: './watch-list-movie-card.html',
  styleUrl: './watch-list-movie-card.scss',
})
export class WatchListMovieCard {
  movie = input.required<WatchlistMovie>();

  protected readonly imageBaseUrl = environment.imageBaseUrl;
  protected readonly Math = Math;
}
