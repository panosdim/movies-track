import {
  Component,
  OnInit,
  AfterViewInit,
  OnDestroy,
  inject,
  signal,
  computed,
  ElementRef,
} from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';

import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { InputTextModule } from 'primeng/inputtext';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { ProgressBarModule } from 'primeng/progressbar';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';
import { MessageModule } from 'primeng/message';
import { FloatLabelModule } from 'primeng/floatlabel';
import { PasswordModule } from 'primeng/password';

import { AuthService } from '../../core/services/auth.service';
import { PopularMoviesService } from '../../core/services/popular-movies.service';
import { TmdbMovie } from '../../core/models/tmdb-movie.model';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    ButtonModule,
    CardModule,
    InputTextModule,
    IconFieldModule,
    InputIconModule,
    ProgressBarModule,
    MessageModule,
    ToastModule,
    FloatLabelModule,
    PasswordModule,
  ],
  providers: [MessageService],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss',
})
export class LoginComponent implements OnInit, AfterViewInit, OnDestroy {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly popularMoviesService = inject(PopularMoviesService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly messageService = inject(MessageService);
  private readonly el = inject(ElementRef);

  readonly imageBaseUrl = environment.imageBaseUrl + 'w500';

  // Grid item dimensions (must match SCSS values)
  private readonly POSTER_WIDTH = 180;
  private readonly POSTER_HEIGHT = 260;
  private readonly GAP = 24;

  posters = signal<TmdbMovie[]>([]);
  isLoginInProgress = signal(false);
  showPassword = false;

  /** How many posters fit in the current grid area. */
  private gridCapacity = signal(0);

  /** Subset of posters that actually fits in the available space. */
  readonly visiblePosters = computed(() => {
    const capacity = this.gridCapacity();
    return capacity > 0 ? this.posters().slice(0, capacity) : this.posters();
  });

  private resizeObserver: ResizeObserver | null = null;

  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
  });

  ngOnInit(): void {
    this.popularMoviesService.getPopularMovies().subscribe((data) => {
      this.posters.set(data.results);
    });
  }

  ngAfterViewInit(): void {
    // DOM is rendered here — clientWidth/clientHeight are valid.
    const leftPanel: HTMLElement = this.el.nativeElement.querySelector('.login-left');
    if (leftPanel) {
      this.resizeObserver = new ResizeObserver(() => this.updateGridCapacity(leftPanel));
      this.resizeObserver.observe(leftPanel);
      this.updateGridCapacity(leftPanel);
    }
  }

  ngOnDestroy(): void {
    this.resizeObserver?.disconnect();
  }

  private updateGridCapacity(container: HTMLElement): void {
    // Available width/height inside the left panel (padding is 32px on sides)
    const availableWidth = container.clientWidth;
    const availableHeight = container.clientHeight;

    const cols = Math.max(
      1,
      Math.floor((availableWidth + this.GAP) / (this.POSTER_WIDTH + this.GAP)),
    );
    const rows = Math.max(
      1,
      Math.floor((availableHeight + this.GAP) / (this.POSTER_HEIGHT + this.GAP)),
    );

    this.gridCapacity.set(cols * rows);
  }

  onLogin(): void {
    if (this.loginForm.invalid || this.isLoginInProgress()) return;

    this.isLoginInProgress.set(true);
    const { email, password } = this.loginForm.getRawValue();

    this.authService.login(email!, password!).subscribe({
      next: () => {
        this.isLoginInProgress.set(false);
        const returnUrl = this.route.snapshot.queryParamMap.get('returnUrl') ?? '/movies';
        this.router.navigateByUrl(returnUrl);
      },
      error: () => {
        this.isLoginInProgress.set(false);
        this.messageService.add({
          severity: 'error',
          summary: 'Login failed',
          detail: 'Invalid email or password.',
          life: 4000,
        });
      },
    });
  }

  isInvalid(controlName: string) {
    const control = this.loginForm.get(controlName);
    return control?.invalid && (control.touched || this.isLoginInProgress());
  }

  hasError(controlName: string) {
    const control = this.loginForm.get(controlName);
    return control?.errors;
  }
}
