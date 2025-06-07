export interface Usuario {
  _id?: string;  // Changed from id to _id to match MongoDB
  nombre: string;
  email: string;
  nivel: 'principiante' | 'intermedio' | 'avanzado';
  bicicleta: string;
  fecha_registro?: Date;
}