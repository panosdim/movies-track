import { Component, input } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { RatingModule } from 'primeng/rating';
import { environment } from '../../../../environments/environment';
import { WatchedMovie } from '../../models/movie.model';

@Component({
  selector: 'app-mobile-watched-movie-card',
  imports: [CardModule, ButtonModule, RatingModule, FormsModule],
  templateUrl: './mobile-watched-movie-card.html',
  styleUrl: './mobile-watched-movie-card.scss',
})
export class MobileWatchewatdMovieCard {
  movie = input.required<WatchedMovie>();
  protected readonly imageBaseUrl = environment.imageBaseUrl;
}
