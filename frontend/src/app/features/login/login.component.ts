import { Component, OnInit, inject, signal, ChangeDetectorRef } from '@angular/core';
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
export class LoginComponent implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly authService = inject(AuthService);
  private readonly popularMoviesService = inject(PopularMoviesService);
  private readonly router = inject(Router);
  private readonly route = inject(ActivatedRoute);
  private readonly messageService = inject(MessageService);
  private readonly cdr = inject(ChangeDetectorRef);

  readonly imageBaseUrl = environment.imageBaseUrl + 'w500';

  posters = signal<TmdbMovie[]>([]);
  isLoginInProgress = signal(false);
  showPassword = false;

  loginForm = this.fb.group({
    email: ['', [Validators.required, Validators.email]],
    password: ['', Validators.required],
  });

  ngOnInit(): void {
    this.popularMoviesService.getPopularMovies().subscribe((data) => {
      this.posters.set(data.results);
    });

    // Handle browser autofill by explicitly marking controls as touched and updating validity
    // after a short delay to allow autofill to complete.
    setTimeout(() => {
      const emailControl = this.loginForm.get('email');
      const passwordControl = this.loginForm.get('password');

      // Check if controls have values (autofilled) and mark them as touched
      if (emailControl && emailControl.value) {
        emailControl.markAsTouched();
        emailControl.updateValueAndValidity();
      }
      if (passwordControl && passwordControl.value) {
        passwordControl.markAsTouched();
        passwordControl.updateValueAndValidity();
      }
      this.cdr.detectChanges(); // Force change detection to update the button's disabled state
    }, 500); // A small delay to ensure autofill has occurred
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
