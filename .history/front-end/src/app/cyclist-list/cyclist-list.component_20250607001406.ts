// filepath: c:\Users\Bryan Emilio\Documents\UTNG\Remedial_BD\crud_ciclismo\front-end\src\app\cyclist-list\cyclist-list.component.ts
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { ApiService } from '../services/api.service';
import { Usuario } from '../interfaces/models';
import { Modal } from 'bootstrap';

@Component({
  selector: 'app-cyclist-list',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './cyclist-list.component.html',
  styleUrls: ['./cyclist-list.component.scss']
})
export class CyclistListComponent implements OnInit {
  cyclists: Usuario[] = [];
  cyclistForm: FormGroup;
  isEditing = false;
  private modal: Modal | null = null;
  private currentId: string | null = null;

  constructor(
    private apiService: ApiService,
    private fb: FormBuilder
  ) {
    this.cyclistForm = this.fb.group({
      nombre: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      nivel: ['principiante', Validators.required],
      bicicleta: ['', Validators.required]
    });
  }

  ngOnInit(): void {
    this.loadCyclists();
    this.modal = new Modal(document.getElementById('cyclistModal')!);
  }

  loadCyclists(): void {
    this.apiService.getUsuarios().subscribe({
      next: (data) => this.cyclists = data,
      error: (error) => console.error('Error loading cyclists:', error)
    });
  }

  openAddModal(): void {
    this.isEditing = false;
    this.currentId = null;
    this.cyclistForm.reset({ nivel: 'principiante' });
    this.modal?.show();
  }

  editCyclist(cyclist: Usuario): void {
    this.isEditing = true;
    this.currentId = cyclist.id;
    this.cyclistForm.patchValue(cyclist);
    this.modal?.show();
  }

  saveCyclist(): void {
    if (this.cyclistForm.valid) {
      const cyclist = this.cyclistForm.value;
      cyclist.fecha_registro = new Date();

      const request = this.isEditing && this.currentId
        ? this.apiService.updateUsuario(this.currentId, cyclist)
        : this.apiService.createUsuario(cyclist);

      request.subscribe({
        next: () => {
          this.loadCyclists();
          this.modal?.hide();
        },
        error: (error) => console.error('Error saving cyclist:', error)
      });
    }
  }

  deleteCyclist(id: string): void {
    if (confirm('¿Estás seguro de eliminar este ciclista?')) {
      this.apiService.deleteUsuario(id).subscribe({
        next: () => this.loadCyclists(),
        error: (error) => console.error('Error deleting cyclist:', error)
      });
    }
  }
}