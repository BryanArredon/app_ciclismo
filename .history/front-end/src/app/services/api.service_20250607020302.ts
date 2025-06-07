import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of, delay } from 'rxjs';
import { Usuario } from '../interfaces/models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private mockData: Usuario[] = [
    {
      id: '1',
      nombre: 'Carlos Méndez',
      email: 'carlos@gmail.com',
      nivel: 'intermedio',
      bicicleta: 'Montaña Trek X-Caliber',
      fecha_registro: new Date('2024-01-15')
    },
    {
      id: '2',
      nombre: 'Ana García',
      email: 'ana.garcia@hotmail.com',
      nivel: 'avanzado',
      bicicleta: 'Ruta Specialized Tarmac',
      fecha_registro: new Date('2024-02-20')
    },
    {
      id: '3',
      nombre: 'Miguel Torres',
      email: 'miguel.t@yahoo.com',
      nivel: 'principiante',
      bicicleta: 'Híbrida Giant Escape',
      fecha_registro: new Date('2024-03-10')
    },
    {
      id: '4',
      nombre: 'Laura Pérez',
      email: 'laura.perez@gmail.com',
      nivel: 'intermedio',
      bicicleta: 'BMX Mongoose Legion',
      fecha_registro: new Date('2024-03-15')
    }
  ];

  constructor(private http: HttpClient) {}

  getUsuarios(): Observable<Usuario[]> {
    return of(this.mockData).pipe(delay(500)); // Simulate network delay
  }

  createUsuario(usuario: Omit<Usuario, 'id'>): Observable<Usuario> {
    const newUser: Usuario = {
      ...usuario,
      id: (this.mockData.length + 1).toString(),
      fecha_registro: new Date()
    };
    this.mockData.push(newUser);
    return of(newUser).pipe(delay(500));
  }

  updateUsuario(id: string, usuario: Partial<Usuario>): Observable<Usuario> {
    const index = this.mockData.findIndex(u => u.id === id);
    if (index !== -1) {
      this.mockData[index] = { ...this.mockData[index], ...usuario };
      return of(this.mockData[index]).pipe(delay(500));
    }
    throw new Error('Usuario no encontrado');
  }

  deleteUsuario(id: string): Observable<void> {
    const index = this.mockData.findIndex(u => u.id === id);
    if (index !== -1) {
      this.mockData.splice(index, 1);
      return of(void 0).pipe(delay(500));
    }
    throw new Error('Usuario no encontrado');
  }
}