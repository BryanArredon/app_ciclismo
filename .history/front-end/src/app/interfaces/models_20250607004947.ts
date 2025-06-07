export interface Usuario {
  id?: string;
  nombre: string;
  email: string;
  nivel: 'principiante' | 'intermedio' | 'avanzado';
  bicicleta: string;
  fecha_registro?: Date;
}