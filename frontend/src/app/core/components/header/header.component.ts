import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MenubarModule } from 'primeng/menubar';
import { ButtonModule } from 'primeng/button';
import { AvatarModule } from 'primeng/avatar';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '@core/services';
import { MenuItem } from 'primeng/api';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, MenubarModule, ButtonModule, AvatarModule, RouterLink],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
})
export class HeaderComponent {
  private readonly router = inject(Router);
  private readonly authService = inject(AuthService);
  readonly menuItems: MenuItem[] = [
    {
      label: 'Watchlist',
      icon: 'pi pi-video',
      routerLink: '/watchlist',
      routerLinkActiveOptions: { exact: true },
    },
    {
      label: 'Watched Movies',
      icon: 'pi pi-eye',
      routerLink: '/watched',
      routerLinkActiveOptions: { exact: true },
    },
  ];

  onLogout(): void {
    this.authService.logout();
  }

  onAddMovie(): void {
    this.router.navigate(['/movies/add']);
  }
}
