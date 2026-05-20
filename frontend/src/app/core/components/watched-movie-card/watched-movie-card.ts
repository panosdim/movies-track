import { Component, Input } from '@angular/core';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { WatchedMovie } from '../../models/movie.model';
import { environment } from '../../../../environments/environment';
import { FormsModule } from '@angular/forms';
import { RatingModule } from 'primeng/rating';

@Component({
  selector: 'app-watched-movie-card',
  imports: [CardModule, ButtonModule, RatingModule, FormsModule],
  templateUrl: './watched-movie-card.html',
  styleUrl: './watched-movie-card.scss',
})
export class WatchedMovieCard {
  @Input({ required: true }) movie: WatchedMovie = {} as WatchedMovie;

  protected readonly imageBaseUrl = environment.imageBaseUrl;
}
