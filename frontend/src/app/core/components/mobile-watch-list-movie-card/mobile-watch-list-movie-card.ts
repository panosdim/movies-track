import { Component, Input } from '@angular/core';
import { WatchlistMovie } from '../../models/movie.model';
import { environment } from '../../../../environments/environment';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { ProgressBarModule } from 'primeng/progressbar';

@Component({
  selector: 'app-mobile-watch-list-movie-card',
  imports: [CardModule, ButtonModule, ProgressBarModule],
  templateUrl: './mobile-watch-list-movie-card.html',
  styleUrl: './mobile-watch-list-movie-card.scss',
})
export class MobileWatchListMovieCard {
  @Input({ required: true }) movie: WatchlistMovie = {} as WatchlistMovie;

  protected readonly imageBaseUrl = environment.imageBaseUrl;
  protected readonly Math = Math;
}
