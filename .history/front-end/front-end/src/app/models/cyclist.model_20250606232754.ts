export interface Usuario {
    _id?: string;
    nombre: string;
    email: string;
    nivel: string;
    bicicleta: string;
    fecha_registro: Date;
  }


  export interface Ruta {
    _id?: string;
    usuario_id: string;
    nombre: string;
    distancia_km: number;
    tiempo_minutos: number;
    fecha: Date;
    elevacion_m: number;
    equipo_usado: string[];
    notas: string;
    condiciones: {
      clima: string;
      temperatura_c: number;
      viento_kmh: number;
    };
  }


  export interface Evento {
    _id?: string;
    nombre: string;
    fecha_evento: Date;
    ubicacion: string;
    tipo: string;
    participantes: string[];
    distancia_km: number;
    organizador: string;
    inscripcion_abierta: boolean;
    costo: number;
  }