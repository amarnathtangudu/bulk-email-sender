import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Recipient {
  id: string;
  email: string;
  status: 'idle' | 'sending' | 'success' | 'failed';
  variables: { [key: string]: string };
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private baseUrl = 'http://localhost:8000';

  constructor(private http: HttpClient) {}

  downloadCSVTemplate(placeholders: string[]): Observable<Blob> {
    return this.http.post(`${this.baseUrl}/generate-template`, { placeholders }, { responseType: 'blob' });
  }

  sendBulkEmails(payload: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/send-bulk`, payload);
  }

  generateEmail(payload: any): Observable<any> {
    return this.http.post(`${this.baseUrl}/generate-email`, payload);
  }
}
