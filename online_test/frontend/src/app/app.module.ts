import { Component } from '@angular/core';
import { VideoSessionComponent } from './video-session/video-session.component';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  standalone: true,  // Marking this component as standalone
  imports: [VideoSessionComponent],  // Import VideoSessionComponent here
})
export class AppComponent {
  title = 'frontend';
}
