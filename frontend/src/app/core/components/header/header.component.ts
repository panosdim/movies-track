import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MenubarModule } from 'primeng/menubar';
import { ButtonModule } from 'primeng/button';
import { AvatarModule } from 'primeng/avatar';
import { RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { MenuItem } from 'primeng/api';
import { Card } from 'primeng/card';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, MenubarModule, ButtonModule, AvatarModule, RouterLink],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss',
})
export class HeaderComponent {
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
}
