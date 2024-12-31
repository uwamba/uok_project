import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { VideoSessionComponent } from './video-session/video-session.component';  // Import your component

const routes: Routes = [
  { path: '', redirectTo: '/video-session', pathMatch: 'full' },
  { path: 'video-session', component: VideoSessionComponent },
  // Add other routes here
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
