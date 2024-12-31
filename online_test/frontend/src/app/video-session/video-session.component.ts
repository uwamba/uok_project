import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { OpenVidu } from 'openvidu-browser';
import { RouterModule } from '@angular/router';   // Import FormsModule

@Component({
  selector: 'app-video-session',
  standalone: true,
  templateUrl: './video-session.component.html',
  styleUrls: ['./video-session.component.css'],
  imports: [FormsModule],  // Add FormsModule to imports
})
export class VideoSessionComponent {
  userName: string = '';  // Define the userName property
  sessionId: string = '';  // Define the sessionId property
  OV: OpenVidu = new OpenVidu;
  session: any;
  localStream: any;

  APPLICATION_SERVER_URL = 'http://localhost:8000/';  // Django API server URL

  constructor() { }

  async joinSession(sessionId: string, userName: string) {
    this.OV = new OpenVidu();
    this.session = this.OV.initSession();

    this.session.on('streamCreated', (event: any) => {
      const subscriber = this.session.subscribe(event.stream, undefined);
      const videoContainer = document.getElementById('video-container');
      videoContainer?.appendChild(subscriber.video);
    });

    try {
      const token = await this.getToken(sessionId, userName);
      await this.session.connect(token, { clientData: userName });

      // Publish local camera
      this.localStream = await this.OV.initPublisherAsync('video-container');
      this.session.publish(this.localStream);

      const videoContainer = document.getElementById('video-container');
      videoContainer?.appendChild(this.localStream.video);
    } catch (error) {
      console.error('Error connecting to session:', error);
    }
  }

  async leaveSession() {
    if (this.session) {
      this.session.disconnect();
      this.session = null;
      const videoContainer = document.getElementById('video-container');
      if (videoContainer) videoContainer.innerHTML = '';
    }
  }

  private async getToken(sessionId: string, userName: string): Promise<string> {
    const response = await fetch(`${this.APPLICATION_SERVER_URL}api/sessions/${sessionId}/connections`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userName }),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch token');
    }

    const data = await response.json();
    return data.token;
  }
}


