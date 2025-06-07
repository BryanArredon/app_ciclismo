import { Injectable, PLATFORM_ID, Inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { Usuario, Ruta, Evento } from '../interfaces/models';
import { isPlatformServer } from '@angular/common';
import { catchError, tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000/api';

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

  // Usuarios endpoints
  getUsuarios(): Observable<Usuario[]> {
    return this.handleSSR<Usuario[]>([]) || 
      this.http.get<Usuario[]>(`${this.baseUrl}/usuarios`);
  }

  getUsuario(id: string): Observable<Usuario> {
    return this.handleSSR<Usuario>(null!) || 
      this.http.get<Usuario>(`${this.baseUrl}/usuarios/${id}`);
  }

  createUsuario(usuario: Omit<Usuario, '_id'>): Observable<Usuario> {
    const newUsuario = {
      ...usuario,
      fecha_registro: new Date()
    };
    return this.handleSSR<Usuario>(null!) || 
      this.http.post<Usuario>(`${this.baseUrl}/usuarios`, newUsuario).pipe(
        tap(response => console.log('Create response:', response)),
        catchError(error => {
          console.error('Create error:', error);
          return throwError(() => error);
        })
      );
  }

  updateUsuario(id: string, usuario: Partial<Usuario>): Observable<Usuario> {
    // Validate ObjectId format
    if (!id || !/^[0-9a-fA-F]{24}$/.test(id)) {
      return throwError(() => ({
        status: 400,
        error: { detail: 'ID de usuario inválido - debe ser un ObjectId válido de MongoDB' }
      }));
    }

    return this.http.put<Usuario>(`${this.baseUrl}/usuarios/${id}`, usuario).pipe(
      tap(response => console.log('Update response:', response)),
      catchError(error => {
        console.error('Update error:', error);
        return throwError(() => error);
      })
    );
  }

  deleteUsuario(id: string): Observable<void> {
    // Validate ObjectId format
    if (!id || !/^[0-9a-fA-F]{24}$/.test(id)) {
      return throwError(() => ({
        status: 400,
        error: { detail: 'ID de usuario inválido - debe ser un ObjectId válido de MongoDB' }
      }));
    }

    return this.http.delete<void>(`${this.baseUrl}/usuarios/${id}`).pipe(
      tap(() => console.log('Delete successful')),
      catchError(error => {
        console.error('Delete error:', error);
        return throwError(() => error);
      })
    );
  }

  // Rutas endpoints
  getRutas(): Observable<Ruta[]> {
    return this.http.get<Ruta[]>(`${this.baseUrl}/rutas`);
  }

  createRuta(ruta: Omit<Ruta, '_id'>): Observable<Ruta> {
    return this.http.post<Ruta>(`${this.baseUrl}/rutas`, ruta);
  }

  updateRuta(id: string, ruta: Partial<Ruta>): Observable<Ruta> {
    return this.http.put<Ruta>(`${this.baseUrl}/rutas/${id}`, ruta);
  }

  deleteRuta(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/rutas/${id}`);
  }

  // Eventos endpoints
  getEventos(): Observable<Evento[]> {
    return this.http.get<Evento[]>(`${this.baseUrl}/eventos`);
  }

  createEvento(evento: Omit<Evento, '_id'>): Observable<Evento> {
    return this.http.post<Evento>(`${this.baseUrl}/eventos`, evento);
  }

  updateEvento(id: string, evento: Partial<Evento>): Observable<Evento> {
    return this.http.put<Evento>(`${this.baseUrl}/eventos/${id}`, evento);
  }

  deleteEvento(id: string): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/eventos/${id}`);
  }
}