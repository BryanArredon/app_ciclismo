import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';
import { Evento } from '../interfaces/models';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-evets-lis',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './evets-lis.component.html',
  styleUrl: './evets-lis.component.css'
})
export class EvetsLisComponent implements OnInit, OnDestroy {
  eventos: Evento[] = [];
  eventoForm!: FormGroup;
  isEditing = false;
  isLoading = false;
  errorMessage: string | null = null;
  showModal = false;
  private currentId: string | null = null;
  private subscriptions = new Subscription();

  constructor(
    private apiService: ApiService,
    private fb: FormBuilder
  ) {
    this.initializeForm();
  }

  private initializeForm(): void {
    this.eventoForm = this.fb.group({
      nombre: ['', [Validators.required]],
      fecha_evento: ['', [Validators.required]],
      ubicacion: ['', [Validators.required]],
      tipo: ['', [Validators.required]],
      participantes: [[]],
      distancia_km: ['', [Validators.required, Validators.min(0)]],
      organizador: ['', [Validators.required]],
      inscripcion_abierta: [true],
      costo: ['', [Validators.required, Validators.min(0)]]
    });
  }

  ngOnInit(): void {
    this.loadEventos();
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  loadEventos(): void {
    this.isLoading = true;
    const sub = this.apiService.getEventos().subscribe({
      next: (data) => {
        this.eventos = data;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading events:', error);
        this.errorMessage = 'Error al cargar los eventos';
        this.isLoading = false;
      }
    });
    this.subscriptions.add(sub);
  }

  saveEvento(): void {
    if (this.eventoForm.invalid || this.isLoading) return;

    this.isLoading = true;
    const eventoData = this.eventoForm.value;
    
    const request$ = this.isEditing && this.currentId
      ? this.apiService.updateEvento(this.currentId, eventoData)
      : this.apiService.createEvento(eventoData);

    const sub = request$.subscribe({
      next: () => {
        this.loadEventos();
        this.showModal = false;
        this.eventoForm.reset({inscripcion_abierta: true});
        this.isEditing = false;
        this.currentId = null;
      },
      error: (error) => {
        console.error('Error saving event:', error);
        this.errorMessage = 'Error al guardar el evento';
        this.isLoading = false;
      }
    });
    this.subscriptions.add(sub);
  }

  deleteEvento(id: string): void {
    if (confirm('¿Está seguro de eliminar este evento?')) {
      const sub = this.apiService.deleteEvento(id).subscribe({
        next: () => this.loadEventos(),
        error: (error) => {
          console.error('Error deleting event:', error);
          this.errorMessage = 'Error al eliminar el evento';
        }
      });
      this.subscriptions.add(sub);
    }
  }

  editEvento(evento: Evento): void {
    this.isEditing = true;
    this.currentId = evento._id || null;
    this.eventoForm.patchValue(evento);
    this.showModal = true;
  }

  openAddModal(): void {
    this.isEditing = false;
    this.currentId = null;
    this.eventoForm.reset({inscripcion_abierta: true});
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.eventoForm.reset({inscripcion_abierta: true});
    this.errorMessage = null;
  }
}
