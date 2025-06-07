// filepath: c:\Users\Bryan Emilio\Documents\UTNG\Remedial_BD\crud_ciclismo\front-end\src\app\cyclist-list\cyclist-list.component.ts
import { Component, OnInit, OnDestroy, PLATFORM_ID, Inject } from '@angular/core';
import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';
import { Usuario } from '../interfaces/models';
import { Modal } from 'bootstrap';
import { Observable, Subscription, catchError, finalize, throwError } from 'rxjs';

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
  private modal: Modal | null = null;
  private currentId: string | null = null;
  private subscriptions = new Subscription();

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    private apiService: ApiService,
    private fb: FormBuilder
  ) {
    this.initializeForm();
  }

  private initializeForm(): void {
    this.cyclistForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3), Validators.maxLength(50)]],
      email: ['', [Validators.required, Validators.email, Validators.maxLength(100)]],
      nivel: ['principiante', [Validators.required]],
      bicicleta: ['', [Validators.required, Validators.minLength(2), Validators.maxLength(50)]]
    });
  }

  ngOnInit(): void {
    // Only setup modal in browser environment
    if (isPlatformBrowser(this.platformId)) {
      this.setupModal();
    }
    this.loadCyclists();
  }

  private setupModal(): void {
    // Ensure we're in browser environment before accessing DOM
    if (isPlatformBrowser(this.platformId)) {
      const modalElement = document.getElementById('cyclistModal');
      if (modalElement) {
        this.modal = new Modal(modalElement);
      } else {
        console.error('Modal element not found');
      }
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
    // Only dispose modal in browser environment
    if (isPlatformBrowser(this.platformId) && this.modal) {
      this.modal.dispose();
    }
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
    // Only show modal in browser environment
    if (isPlatformBrowser(this.platformId)) {
      this.modal?.show();
    }
  }

  editCyclist(cyclist: Usuario): void {
    if (!cyclist?.id) {
      console.error('Invalid cyclist data');
      return;
    }
    
    this.isEditing = true;
    this.currentId = cyclist.id;
    this.errorMessage = null;
    
    this.cyclistForm.patchValue({
      nombre: cyclist.nombre,
      email: cyclist.email,
      nivel: cyclist.nivel,
      bicicleta: cyclist.bicicleta
    });
    
    // Only show modal in browser environment
    if (isPlatformBrowser(this.platformId)) {
      this.modal?.show();
    }
  }

  saveCyclist(): void {
    if (this.cyclistForm.invalid || this.isLoading) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = null;

    const cyclist: Usuario = {
      ...this.cyclistForm.value,
      fecha_registro: this.isEditing ? undefined : new Date()
    };

    const request$: Observable<Usuario> = this.isEditing && this.currentId
      ? this.apiService.updateUsuario(this.currentId, cyclist)
      : this.apiService.createUsuario(cyclist);

    const sub = request$.pipe(
      catchError((error: Error) => {
        this.errorMessage = 'Error al guardar el ciclista. Por favor, intente nuevamente.';
        console.error('Error saving cyclist:', error);
        return throwError(() => error);
      }),
      finalize(() => {
        this.isLoading = false;
      })
    ).subscribe({
      next: () => {
        this.loadCyclists();
        this.modal?.hide();
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