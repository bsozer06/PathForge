import { Component, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { NgIf } from '@angular/common';
import { FormsModule } from '@angular/forms';
import * as L from 'leaflet';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-map',
  standalone: true,
  imports: [NgIf, FormsModule],
  template: `
    <div class="controls">
      <label>Start: <input type="number" [(ngModel)]="start.lat" step="0.0001" /> <input type="number" [(ngModel)]="start.lon" step="0.0001" /></label>
      <label>End: <input type="number" [(ngModel)]="end.lat" step="0.0001" /> <input type="number" [(ngModel)]="end.lon" step="0.0001" /></label>
      <button (click)="computeRoute()">Route</button>
      <span *ngIf="loading">Loading...</span>
      <span *ngIf="error" class="error">{{error}}</span>
    </div>
    <div #map style="height:500px;width:100%;margin-top:16px;"></div>
  `,
  styles: [`.controls { display: flex; gap: 16px; align-items: center; } .error { color: #c00; margin-left: 12px; }`]
})
export class MapComponent implements AfterViewInit {
  @ViewChild('map', { static: true }) mapElement!: ElementRef;
  private map!: L.Map;
  private routeLayer?: L.GeoJSON;

  start = { lat: 41.01, lon: 28.97 };
  end = { lat: 41.08, lon: 29.01 };
  loading = false;
  error = '';

  constructor(private http: HttpClient) {}

  ngAfterViewInit() {
    this.map = L.map(this.mapElement.nativeElement).setView([41.04, 28.99], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '© OpenStreetMap contributors'
    }).addTo(this.map);
  }

  computeRoute() {
    this.loading = true;
    this.error = '';
    // Adjust API URL if backend runs on a different port
    const apiUrl = 'http://localhost:8000/route';
    console.log('Route request:', { start: this.start, end: this.end });
    this.http.post<any>(apiUrl, { start: this.start, end: this.end }).subscribe({
      next: geojson => {
        console.log('Route response:', geojson);
        if (this.routeLayer) {
          this.map.removeLayer(this.routeLayer);
        }
        // The backend returns a GeoJSON Feature, but L.geoJSON expects a FeatureCollection or Geometry
        // Wrap the feature as a FeatureCollection for Leaflet
        const featureCollection: GeoJSON.FeatureCollection = {
          type: 'FeatureCollection',
          features: [geojson]
        };
        this.routeLayer = L.geoJSON(featureCollection as any, {
          style: { color: 'red', weight: 5 }
        }).addTo(this.map);
        this.map.fitBounds(this.routeLayer.getBounds());
        this.loading = false;
      },
      error: err => {
        console.error('Route error:', err);
        this.error = err.message || 'Route not found';
        this.loading = false;
      }
    });
  }
}
