import { Routes } from '@angular/router';
import { CyclistListComponent } from './cyclist-list/cyclist-list.component';

export const routes: Routes = [
    { path: '', redirectTo: '/cyclists', pathMatch: 'full' },
    { path: 'cyclists', component: CyclistListComponent }
];
