import { Injectable, PLATFORM_ID, Inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Usuario } from '../interfaces/models';
import { isPlatformServer } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000/api'; // Adjust this to match your backend URL

  constructor(
    private http: HttpClient,
    @Inject(PLATFORM_ID) private platformId: Object
  ) {}

  private handleSSR<T>(fallback: T): Observable<T> {
    if (isPlatformServer(this.platformId)) {
      return of(fallback);
    }
    return null!;
  }

  // Usuarios (Cyclists)
  getUsuarios(): Observable<Usuario[]> {
    return this.handleSSR<Usuario[]>([]) || 
      this.http.get<Usuario[]>(`${this.baseUrl}/usuarios`);
  }

  getUsuario(id: string): Observable<Usuario> {
    return this.handleSSR<Usuario>(null!) || 
      this.http.get<Usuario>(`${this.baseUrl}/usuarios/${id}`);
  }

  createUsuario(usuario: Omit<Usuario, 'id'>): Observable<Usuario> {
    return this.handleSSR<Usuario>(null!) || 
      this.http.post<Usuario>(`${this.baseUrl}/usuarios`, usuario);
  }

  updateUsuario(id: string, usuario: Partial<Usuario>): Observable<Usuario> {
    return this.handleSSR<Usuario>(null!) || 
      this.http.put<Usuario>(`${this.baseUrl}/usuarios/${id}`, usuario);
  }

  deleteUsuario(id: string): Observable<void> {
    return this.handleSSR<void>(undefined) || 
      this.http.delete<void>(`${this.baseUrl}/usuarios/${id}`);
  }
}