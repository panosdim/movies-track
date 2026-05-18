import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap, catchError, of, map } from 'rxjs';
import { environment } from '../../../environments/environment';

export interface MeResponse {
  token: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export type LoginResponse = MeResponse;

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);

  /** In-memory token storage — cleared on page refresh. */
  private token: string | null = null;

  getToken(): string | null {
    return this.token;
  }

  setToken(token: string): void {
    this.token = token;
  }

  clearToken(): void {
    this.token = null;
  }

  /**
   * Calls POST /api/v1/login with email + password credentials.
   * Stores the returned token on success.
   */
  login(email: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(environment.loginUrl(), { email, password } satisfies LoginRequest)
      .pipe(tap((res) => this.setToken(res.token)));
  }

  /**
   * Calls GET /api/v1/me with the stored Bearer token.
   * On success the server returns a fresh token which is stored automatically.
   * Returns `true` if authenticated, `false` otherwise.
   */
  checkAuth(): Observable<boolean> {
    const token = this.getToken();

    if (!token) {
      return of(false);
    }

    const headers = new HttpHeaders({ Authorization: `Bearer ${token}` });

    return this.http.get<MeResponse>(environment.meUrl(), { headers }).pipe(
      tap((res) => this.setToken(res.token)),
      map(() => true),
      catchError(() => of(false)),
    );
  }
}
