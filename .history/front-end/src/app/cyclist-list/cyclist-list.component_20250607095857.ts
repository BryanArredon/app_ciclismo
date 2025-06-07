import { Component, OnInit, OnDestroy, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';
import { Usuario } from '../interfaces/models';
import { Subscription, catchError, finalize, throwError } from 'rxjs';

@Component({
  selector: 'app-cyclist-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './cyclist-list.component.html',
  styleUrls: ['./cyclist-list.component.scss']
})
export class CyclistListComponent implements OnInit, OnDestroy {
  cyclists: Usuario[] = [];
  cyclistForm!: FormGroup;
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
    this.cyclistForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      email: ['', [Validators.required, Validators.email]],
      nivel: ['principiante', [Validators.required]],
      bicicleta: ['', [Validators.required, Validators.minLength(2)]]
    });
  }

  ngOnInit(): void {
    this.loadCyclists();
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
  }

  loadCyclists(): void {
    if (this.isLoading) return;
    
    this.isLoading = true;
    this.errorMessage = null;

    const sub = this.apiService.getUsuarios().pipe(
      catchError((error: Error) => {
        this.errorMessage = 'Error al cargar los ciclistas. Por favor, intente nuevamente.';
        console.error('Error loading cyclists:', error);
        return throwError(() => error);
      }),
      finalize(() => this.isLoading = false)
    ).subscribe({
      next: (data) => this.cyclists = data,
      error: () => this.cyclists = []
    });

    this.subscriptions.add(sub);
  }

  openAddModal(): void {
    this.isEditing = false;
    this.currentId = null;
    this.cyclistForm.reset({ nivel: 'principiante' });
    this.errorMessage = null;
    this.showModal = true;
  }

  closeModal(): void {
    this.showModal = false;
  }

  editCyclist(cyclist: Usuario): void {
    if (!cyclist._id) {
      console.error('Invalid cyclist data');
      return;
    }
    
    this.isEditing = true;
    this.currentId = cyclist._id;
    this.errorMessage = null;
    
    this.cyclistForm.patchValue({
      nombre: cyclist.nombre,
      email: cyclist.email,
      nivel: cyclist.nivel,
      bicicleta: cyclist.bicicleta
    });
    
    this.showModal = true;
  }

  saveCyclist(): void {
    if (this.cyclistForm.invalid || this.isLoading) {
        return;
    }

    this.isLoading = true;
    this.errorMessage = null;

    const formValue = this.cyclistForm.value;
    const cyclist: Partial<Usuario> = {
        nombre: formValue.nombre,
        email: formValue.email,
        nivel: formValue.nivel,
        bicicleta: formValue.bicicleta
    };

    if (!this.isEditing) {
        cyclist.fecha_registro = new Date();
    }

    const request$ = this.isEditing && this.currentId
        ? this.apiService.updateUsuario(this.currentId, cyclist)
        : this.apiService.createUsuario(cyclist);

    const sub = request$.pipe(
        catchError((error: any) => {
            this.errorMessage = error.error?.detail || 'Error al guardar el ciclista. Por favor, intente nuevamente.';
            console.error('Error saving cyclist:', error);
            return throwError(() => error);
        }),
        finalize(() => {
            this.isLoading = false;
        })
    ).subscribe({
        next: () => {
            this.loadCyclists();
            this.showModal = false;
            this.cyclistForm.reset({ nivel: 'principiante' });
        },
        error: () => {} // Error already handled in catchError
    });

    this.subscriptions.add(sub);
  }

  deleteCyclist(id: string): void {
    if (!id || this.isLoading) {
      return;
    }

    if (!confirm('¿Estás seguro de eliminar este ciclista?')) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = null;

    const sub = this.apiService.deleteUsuario(id).pipe(
      catchError((error: Error) => {
        this.errorMessage = 'Error al eliminar el ciclista. Por favor, intente nuevamente.';
        console.error('Error deleting cyclist:', error);
        return throwError(() => error);
      }),
      finalize(() => {
        this.isLoading = false;
      })
    ).subscribe({
      next: () => this.loadCyclists(),
      error: () => {} // Error already handled in catchError
    });

    this.subscriptions.add(sub);
  }
}