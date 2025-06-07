import { Routes } from '@angular/router';
import { CyclistListComponent } from './cyclist-list/cyclist-list.component';
import { RutsLisComponent } from './ruts-lis/ruts-lis.component';
import { EvetsLisComponent } from './evets-lis/evets-lis.component';

export const routes: Routes = [
    { path: '', redirectTo: '/cyclists', pathMatch: 'full' },
    { path: 'cyclists', component: CyclistListComponent },
    { path: 'rutas', component: RutsLisComponent },
    { path: 'eventos', component: EvetsLisComponent }
];
