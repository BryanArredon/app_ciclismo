import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';
import { Ruta } from '../interfaces/models';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-ruts-lis',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './ruts-lis.component.html',
  styleUrl: './ruts-lis.component.css'
})
export class RutsLisComponent implements OnInit, OnDestroy {
  rutas: Ruta[] = [];
  rutaForm!: FormGroup;
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
    this.rutaForm = this.fb.group({
      usuario_id: ['', [Validators.required]],
      nombre: ['', [Validators.required]],
      distancia_km: ['', [Validators.required, Validators.min(0)]],
      tiempo_minutos: ['', [Validators.required, Validators.min(0)]],
      fecha: ['', [Validators.required]],
      elevacion_m: ['', [Validators.required]],
      equipo_usado: ['', [Validators.required]],
      notas: [''],
      condiciones: this.fb.group({
        clima: ['', [Validators.required]],
        temperatura_c: ['', [Validators.required]],
        viento_kmh: ['', [Validators.required]]
      })
    });
  }

  ngOnInit(): void {
    this.loadRutas();
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  loadRutas(): void {
    this.isLoading = true;
    const sub = this.apiService.getRutas().subscribe({
      next: (data) => {
        this.rutas = data;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Error loading routes:', error);
        this.errorMessage = 'Error al cargar las rutas';
        this.isLoading = false;
      }
    });
    this.subscriptions.add(sub);
  }

  saveRuta(): void {
    if (this.rutaForm.invalid || this.isLoading) return;

    this.isLoading = true;
    const rutaData = this.rutaForm.value;
    
    const request$ = this.isEditing && this.currentId
      ? this.apiService.updateRuta(this.currentId, rutaData)
      : this.apiService.createRuta(rutaData);

    const sub = request$.subscribe({
      next: () => {
        this.loadRutas();
        this.showModal = false;
        this.rutaForm.reset();
      },
      error: (error) => {
        console.error('Error saving route:', error);
        this.errorMessage = 'Error al guardar la ruta';
        this.isLoading = false;
      }
    });
    this.subscriptions.add(sub);
  }

  deleteRuta(id: string): void {
    if (confirm('¿Está seguro de eliminar esta ruta?')) {
      const sub = this.apiService.deleteRuta(id).subscribe({
        next: () => this.loadRutas(),
        error: (error) => {
          console.error('Error deleting route:', error);
          this.errorMessage = 'Error al eliminar la ruta';
        }
      });
      this.subscriptions.add(sub);
    }
  }

  editRuta(ruta: Ruta): void {
    this.isEditing = true;
    this.currentId = ruta._id || null;
    this.rutaForm.patchValue(ruta);
    this.showModal = true;
  }

  openAddModal(): void {
    this.isEditing = false;
    this.currentId = null;
    this.rutaForm.reset();
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
    this.rutaForm.reset();
    this.errorMessage = null;
  }
}
