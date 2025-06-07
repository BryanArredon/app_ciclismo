import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { Usuario } from '../interfaces/models';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000/api';

  // Mock data for simulation
  private mockUsers: Usuario[] = [
    {
      id: '1',
      nombre: 'Carlos Méndez',
      email: 'carlos@gmail.com',
      nivel: 'intermedio',
      bicicleta: 'Montaña Trek X-Caliber',
      fecha_registro: new Date('2023-01-15')
    },
    {
      id: '2',
      nombre: 'Ana García',
      email: 'ana.garcia@hotmail.com',
      nivel: 'avanzado',
      bicicleta: 'Ruta Specialized Tarmac',
      fecha_registro: new Date('2023-03-20')
    },
    {
      id: '3',
      nombre: 'Miguel Torres',
      email: 'miguel.t@yahoo.com',
      nivel: 'principiante',
      bicicleta: 'Híbrida Giant Escape',
      fecha_registro: new Date('2023-05-10')
    },
    {
      id: '4',
      nombre: 'Laura Pérez',
      email: 'laura.perez@gmail.com',
      nivel: 'intermedio',
      bicicleta: 'Montaña Cannondale Trail',
      fecha_registro: new Date('2023-06-01')
    }
  ];

  constructor(private http: HttpClient) {}

  // Mock implementations
  getUsuarios(): Observable<Usuario[]> {
    return of(this.mockUsers);
  }

  getUsuario(id: string): Observable<Usuario> {
    const user = this.mockUsers.find(u => u.id === id);
    return of(user!);
  }

  createUsuario(usuario: Omit<Usuario, 'id'>): Observable<Usuario> {
    const newUser: Usuario = {
      ...usuario,
      id: (this.mockUsers.length + 1).toString()
    };
    this.mockUsers.push(newUser);
    return of(newUser);
  }

  updateUsuario(id: string, usuario: Partial<Usuario>): Observable<Usuario> {
    const index = this.mockUsers.findIndex(u => u.id === id);
    if (index !== -1) {
      this.mockUsers[index] = { ...this.mockUsers[index], ...usuario };
      return of(this.mockUsers[index]);
    }
    throw new Error('Usuario no encontrado');
  }

  deleteUsuario(id: string): Observable<void> {
    const index = this.mockUsers.findIndex(u => u.id === id);
    if (index !== -1) {
      this.mockUsers.splice(index, 1);
      return of(void 0);
    }
    throw new Error('Usuario no encontrado');
  }
}