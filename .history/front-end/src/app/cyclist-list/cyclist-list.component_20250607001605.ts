// filepath: c:\Users\Bryan Emilio\Documents\UTNG\Remedial_BD\crud_ciclismo\front-end\src\app\cyclist-list\cyclist-list.component.ts
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';
import { Usuario } from '../interfaces/models';
import { Modal } from 'bootstrap';
import { Subscription } from 'rxjs';

@Component({
  selector: 'app-cyclist-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './cyclist-list.component.html',
  styleUrls: ['./cyclist-list.component.scss']
})
export class CyclistListComponent implements OnInit, OnDestroy {
  cyclists: Usuario[] = [];
  cyclistForm: FormGroup;
  isEditing = false;
  private modal: Modal | null = null;
  private currentId: string | null = null;
  private subscriptions: Subscription = new Subscription();

  constructor(
    private apiService: ApiService,
    private fb: FormBuilder
  ) {
    this.initializeForm();
  }

  private initializeForm(): void {
    this.cyclistForm = this.fb.group({
      nombre: ['', [Validators.required, Validators.minLength(3)]],
      email: ['', [Validators.required, Validators.email]],
      nivel: ['principiante', Validators.required],
      bicicleta: ['', [Validators.required, Validators.minLength(2)]]
    });
  }

  ngOnInit(): void {
    this.loadCyclists();
    const modalElement = document.getElementById('cyclistModal');
    if (modalElement) {
      this.modal = new Modal(modalElement);
    } else {
      console.error('Modal element not found');
    }
  }

  ngOnDestroy(): void {
    this.subscriptions.unsubscribe();
    this.modal?.dispose();
  }

  loadCyclists(): void {
    const sub = this.apiService.getUsuarios().subscribe({
      next: (data) => this.cyclists = data,
      error: (error) => console.error('Error loading cyclists:', error)
    });
    this.subscriptions.add(sub);
  }

  openAddModal(): void {
    this.isEditing = false;
    this.currentId = null;
    this.cyclistForm.reset({ nivel: 'principiante' });
    this.modal?.show();
  }

  editCyclist(cyclist: Usuario): void {
    if (!cyclist || !cyclist.id) {
      console.error('Invalid cyclist data');
      return;
    }
    
    this.isEditing = true;
    this.currentId = cyclist.id;
    this.cyclistForm.patchValue({
      nombre: cyclist.nombre,
      email: cyclist.email,
      nivel: cyclist.nivel,
      bicicleta: cyclist.bicicleta
    });
    this.modal?.show();
  }

  saveCyclist(): void {
    if (this.cyclistForm.valid) {
      const cyclist: Usuario = {
        ...this.cyclistForm.value,
        fecha_registro: this.isEditing ? undefined : new Date()
      };

      const sub = (this.isEditing && this.currentId
        ? this.apiService.updateUsuario(this.currentId, cyclist)
        : this.apiService.createUsuario(cyclist))
        .subscribe({
          next: () => {
            this.loadCyclists();
            this.modal?.hide();
            this.cyclistForm.reset({ nivel: 'principiante' });
          },
          error: (error) => {
            console.error('Error saving cyclist:', error);
            alert('Error al guardar el ciclista. Por favor, intente nuevamente.');
          }
        });

      this.subscriptions.add(sub);
    }
  }

  deleteCyclist(id: string): void {
    if (!id) {
      console.error('Invalid cyclist ID');
      return;
    }

    if (confirm('¿Estás seguro de eliminar este ciclista?')) {
      const sub = this.apiService.deleteUsuario(id).subscribe({
        next: () => {
          this.loadCyclists();
          alert('Ciclista eliminado exitosamente');
        },
        error: (error) => {
          console.error('Error deleting cyclist:', error);
          alert('Error al eliminar el ciclista. Por favor, intente nuevamente.');
        }
      });
      this.subscriptions.add(sub);
    }
  }
}