import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { MapComponent } from './features/map.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, MapComponent],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class AppComponent {
  protected readonly title = signal('pathforge-frontend');
}
