import { Component, OnInit, NgZone } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { LucideAngularModule, Send, User, MapPin, Calendar, FileText, CheckCircle, AlertCircle, Download, Upload, Trash2, Settings, X, Copy, ClipboardCheck, RotateCcw, Sparkles, WandSparkles, RefreshCw } from 'lucide-angular';
import { ApiService, Recipient } from './services/api.service';


@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule, LucideAngularModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent implements OnInit {
  readonly Send = Send;
  readonly User = User;
  readonly MapPin = MapPin;
  readonly Calendar = Calendar;
  readonly FileText = FileText;
  readonly CheckCircle = CheckCircle;
  readonly AlertCircle = AlertCircle;
  readonly Download = Download;
  readonly Upload = Upload;
  readonly Trash2 = Trash2;
  readonly Settings = Settings;
  readonly X = X;
  readonly Copy = Copy;
  readonly ClipboardCheck = ClipboardCheck;
  readonly RotateCcw = RotateCcw;
  readonly Sparkles = Sparkles;
  readonly WandSparkles = WandSparkles;
  readonly RefreshCw = RefreshCw;

  copiedSubject = false;
  copiedPreview = false;

  // AI Generation
  showAIPanel = false;
  aiPrompt = '';
  aiMode: 'generate' | 'rewrite' | 'improve' = 'generate';
  isGenerating = false;
  generatedSubject = '';
  generatedBody = '';
  hasAIResult = false;

  template = {
    subject: 'Collaboration Inquiry | Globe Plates x {{hotel_name}}, {{location}} ({{dates}})',
    body: `Dear {{hotel_name}} Team,

We hope this message finds you well.

We are Globe Plates — a travel couple creating refined, cinematic destination content focused on boutique stays, curated dining, and experiential travel. Our audience primarily consists of couples and international travelers planning upcoming trips.

Over the last 90 days, our content has generated 239,000+ views, reaching over 143,000 accounts, with 97% of our reach coming from non-followers — reflecting strong discovery-based growth. Several of our destination reels have organically crossed 163K views.

We will be visiting {{location}} from {{dates}} and would love to explore a collaboration with you for a curated stay experience.

In exchange, we can offer:

• 1 Cinematic Reel tailored to highlight your property’s aesthetic and experience
• 5–10 high-resolution edited images
• Instagram Story coverage with location tagging
• A detailed Google review
• Organic content usage rights for your brand’s reposting

Our content style aligns particularly well with heritage, boutique, and experience-driven properties that appeal to couples and international travelers.

We would be delighted to explore either a complimentary or value-based stay collaboration, depending on what works best for your team.

Please let us know if this would be of interest.

Warm regards,
Globe Plates
Instagram: https://www.instagram.com/globeplates/
Email: globeplates@gmail.com
Contact: +91 8895035680`
  };

  placeholders: string[] = [];
  recipients: Recipient[] = [
    {
      id: '1',
      email: 'manager@thekillians.com',
      status: 'idle',
      variables: { hotel_name: 'The Killians Boutique Hotel', location: 'Fort Kochi', dates: '27–29 March' }
    },
    {
      id: '2',
      email: 'info@heritageinn.com',
      status: 'idle',
      variables: { hotel_name: 'Heritage Inn', location: 'Fort Kochi', dates: '27–29 March' }
    }
  ];

  selectedRecipientIndex = 0;
  previewSubject = '';
  previewBody = '';
  isSending = false;

  smtpUser = '';
  smtpPassword = '';
  showSettings = false;

  notifications: { type: 'success' | 'error', message: string, id: number }[] = [];

  constructor(private apiService: ApiService, private ngZone: NgZone) { }

  ngOnInit() {
    this.detectPlaceholders();
    this.updatePreview();
  }

  detectPlaceholders() {
    const combined = this.template.subject + this.template.body;
    const regex = /{{(.*?)}}/g;
    const matches = combined.matchAll(regex);
    const set = new Set<string>();
    for (const match of matches) {
      set.add(match[1].trim());
    }
    this.placeholders = Array.from(set);

    // Ensure all recipients have these variables
    this.recipients.forEach(r => {
      this.placeholders.forEach(p => {
        if (r.variables[p] === undefined) {
          r.variables[p] = '';
        }
      });
    });
  }

  get selectedRecipient() {
    return this.recipients[this.selectedRecipientIndex];
  }

  updatePreview() {
    const recipient = this.selectedRecipient;
    if (!recipient) return;

    let subject = this.template.subject;
    let body = this.template.body;

    const vars = { ...recipient.variables };

    // Fill in default display for missing values
    this.placeholders.forEach(p => {
      if (!vars[p]) vars[p] = `{{${p}}}`;
    });

    // For the subject (plain text)
    Object.entries(vars).forEach(([key, value]) => {
      const regex = new RegExp(`{{${key}}}`, 'g');
      subject = subject.replace(regex, value);
    });

    // For the body (HTML highlighted)
    let htmlBody = body;
    Object.entries(vars).forEach(([key, value]) => {
      const regex = new RegExp(`{{${key}}}`, 'g');
      const highlighted = `<span class="text-indigo-400 font-semibold">${value}</span>`;
      htmlBody = htmlBody.replace(regex, highlighted);
    });

    this.previewSubject = subject;
    this.previewBody = htmlBody;
  }

  addRecipient() {
    const vars: { [key: string]: string } = {};
    this.placeholders.forEach(p => vars[p] = '');

    this.recipients.push({
      id: Math.random().toString(36).substr(2, 9),
      email: '',
      status: 'idle',
      variables: vars
    });
  }

  removeRecipient(index: number) {
    this.recipients.splice(index, 1);
    if (this.selectedRecipientIndex >= this.recipients.length) {
      this.selectedRecipientIndex = Math.max(0, this.recipients.length - 1);
    }
  }

  clearAllRecipients() {
    if (confirm('Are you sure you want to clear all recipients?')) {
      this.recipients = [];
      this.selectedRecipientIndex = 0;
    }
  }

  removeNotification(id: number) {
    this.notifications = this.notifications.filter(n => n.id !== id);
  }

  addNotification(type: 'success' | 'error', message: string) {
    const id = Date.now() + Math.random();
    this.notifications = [...this.notifications, { type, message, id }];
    setTimeout(() => {
      this.ngZone.run(() => {
        this.removeNotification(id);
      });
    }, 5000);
  }

  downloadCSVTemplate() {
    this.apiService.downloadCSVTemplate(this.placeholders).subscribe((blob: Blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      document.body.appendChild(a);
      a.style.display = 'none';
      a.href = url;
      a.download = 'recipients_template.csv';
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    });
  }

  uploadCSV(event: any) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e: any) => {
      const text = e.target.result;
      const lines = text.split(/\r?\n/).filter((l: string) => l.trim());
      if (lines.length < 2) return;

      let headerLine = lines[0];
      if (headerLine.startsWith('\ufeff')) {
        headerLine = headerLine.substring(1);
      }

      const parseCSVLine = (line: string) => {
        const result = [];
        let current = '';
        let inQuotes = false;
        for (let i = 0; i < line.length; i++) {
          const char = line[i];
          if (char === '"') {
            if (inQuotes && line[i + 1] === '"') {
              current += '"';
              i++;
            } else {
              inQuotes = !inQuotes;
            }
          } else if (char === ',' && !inQuotes) {
            result.push(current.trim());
            current = '';
          } else {
            current += char;
          }
        }
        result.push(current.trim());
        return result;
      };

      const headers = parseCSVLine(headerLine);
      const emailIndex = headers.findIndex(h => h.toLowerCase() === 'email');

      const newRecipients: Recipient[] = [];
      for (let i = 1; i < lines.length; i++) {
        const values = parseCSVLine(lines[i]);
        if (values.length < headers.length && values.length === 1 && !values[0]) continue;

        const vars: { [key: string]: string } = {};
        headers.forEach((h: string, idx: number) => {
          if (idx !== emailIndex) {
            vars[h] = values[idx] || '';
          }
        });

        newRecipients.push({
          id: Math.random().toString(36).substr(2, 9),
          email: emailIndex !== -1 ? values[emailIndex] : '',
          status: 'idle',
          variables: vars
        });
      }
      this.recipients = [...this.recipients, ...newRecipients];
      this.detectPlaceholders();
    };
    reader.readAsText(file);
    event.target.value = '';
  }

  async sendBulk() {
    if (!this.smtpUser || !this.smtpPassword) {
      this.addNotification('error', 'Please configure Gmail SMTP settings first.');
      this.showSettings = true;
      return;
    }

    if (this.recipients.length === 0) {
      this.addNotification('error', 'No recipients found.');
      return;
    }

    if (!confirm(`Are you sure you want to send emails to ${this.recipients.length} recipients?`)) {
      return;
    }

    this.isSending = true;

    // Set all to sending
    this.recipients.forEach(r => r.status = 'sending');

    try {
      const payload = {
        smtp_user: this.smtpUser,
        smtp_password: this.smtpPassword,
        template: this.template,
        recipients: this.recipients.map(r => ({
          id: r.id,
          email: r.email,
          variables: r.variables
        }))
      };

      const response: any = await this.apiService.sendBulkEmails(payload).toPromise();

      let successCount = 0;
      let failedCount = 0;

      if (response && response.results) {
        response.results.forEach((res: any) => {
          const recipient = this.recipients.find(r => r.id === res.id);
          if (recipient) {
            recipient.status = res.status;
            if (res.status === 'success') successCount++;
            else failedCount++;
          }
        });
      }

      if (failedCount === 0) {
        this.addNotification('success', `Successfully sent ${successCount} emails!`);
      } else {
        this.addNotification('error', `Sent ${successCount} successfully, but ${failedCount} failed.`);
      }

    } catch (e: any) {
      console.error(e);
      this.recipients.forEach(r => {
        if (r.status === 'sending') r.status = 'failed';
      });
      this.addNotification('error', e.error?.detail || 'Failed to send bulk emails. Check SMTP settings.');
    } finally {
      this.isSending = false;
    }
  }

  copySubject() {
    if (!this.previewSubject) return;
    navigator.clipboard.writeText(this.previewSubject).then(() => {
      this.copiedSubject = true;
      this.addNotification('success', 'Subject copied to clipboard!');
      setTimeout(() => { this.ngZone.run(() => { this.copiedSubject = false; }); }, 2000);
    });
  }

  copyPreview() {
    if (!this.previewBody) return;
    // Strip HTML tags to copy plain text
    const tmp = document.createElement('div');
    tmp.innerHTML = this.previewBody;
    const plainText = tmp.textContent || tmp.innerText || '';
    navigator.clipboard.writeText(plainText).then(() => {
      this.copiedPreview = true;
      this.addNotification('success', 'Preview body copied to clipboard!');
      setTimeout(() => { this.ngZone.run(() => { this.copiedPreview = false; }); }, 2000);
    });
  }

  clearSubject() {
    this.template.subject = '';
    this.detectPlaceholders();
    this.updatePreview();
  }

  clearBody() {
    this.template.body = '';
    this.detectPlaceholders();
    this.updatePreview();
  }

  async generateWithAI() {
    if (!this.aiPrompt.trim()) {
      this.addNotification('error', 'Please enter a prompt describing the email you want.');
      return;
    }

    this.isGenerating = true;
    this.hasAIResult = false;

    try {
      const payload: any = {
        prompt: this.aiPrompt,
        mode: this.aiMode,
        placeholders: this.placeholders
      };

      if (this.aiMode === 'rewrite' || this.aiMode === 'improve') {
        payload.existing_subject = this.template.subject;
        payload.existing_body = this.template.body;
      }

      const response: any = await this.apiService.generateEmail(payload).toPromise();

      if (response && response.subject && response.body) {
        this.generatedSubject = response.subject;
        this.generatedBody = response.body;
        this.hasAIResult = true;
        this.addNotification('success', 'Email generated! Review and accept below.');
      } else {
        this.addNotification('error', 'AI returned an unexpected response.');
      }
    } catch (e: any) {
      console.error(e);
      this.addNotification('error', e.error?.detail || 'AI generation failed. Check your API key.');
    } finally {
      this.isGenerating = false;
    }
  }

  acceptAIResult() {
    this.template.subject = this.generatedSubject;
    this.template.body = this.generatedBody;
    this.hasAIResult = false;
    this.generatedSubject = '';
    this.generatedBody = '';
    this.detectPlaceholders();
    this.updatePreview();
    this.addNotification('success', 'AI-generated email applied to template!');
  }

  discardAIResult() {
    this.hasAIResult = false;
    this.generatedSubject = '';
    this.generatedBody = '';
  }
}

