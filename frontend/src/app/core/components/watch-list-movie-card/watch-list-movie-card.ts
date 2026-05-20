import { Component, Input } from '@angular/core';
import { CardModule } from 'primeng/card';
import { TooltipModule } from 'primeng/tooltip';
import { ProgressBarModule } from 'primeng/progressbar';
import { ButtonModule } from 'primeng/button';
import { WatchlistMovie } from '../../models/movie.model';
import { environment } from '../../../../environments/environment';

@Component({
  selector: 'app-watch-list-movie-card',
  imports: [CardModule, ButtonModule, ProgressBarModule, TooltipModule],
  templateUrl: './watch-list-movie-card.html',
  styleUrl: './watch-list-movie-card.scss',
})
export class WatchListMovieCard {
  @Input({ required: true }) movie: WatchlistMovie = {} as WatchlistMovie;

  protected readonly imageBaseUrl = environment.imageBaseUrl;
  protected readonly Math = Math;
}
