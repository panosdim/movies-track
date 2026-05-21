import { Component, inject } from '@angular/core';
import { Router, RouterOutlet } from '@angular/router';
import { HeaderComponent, Footer } from '@core';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, HeaderComponent, Footer],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  private readonly router = inject(Router);

  readonly title = 'Movies Track';

  showHeader(): boolean {
    return !this.router.url.includes('/login');
  }

  showFooter(): boolean {
    return !this.router.url.includes('/login');
  }
}
