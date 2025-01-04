import threading
from django.http import StreamingHttpResponse, JsonResponse, FileResponse
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import os
from django.shortcuts import render

import numpy as np
from scipy.spatial.transform import Rotation as R

from exams.models import Test
from videos.models import MonitoringLog
from videos.utils import capture_screen, monitor_webcam
import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import base64
import random

# Generate a random integer between a range
random_integer = random.randint(1000, 10000)  # Random integer between 1 and 100
print(f"Random integer: {random_integer}")

UPLOAD_DIR = 'uploads/'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

VIDEO_FILE_PATH = os.path.join(UPLOAD_DIR, 'live_video.webm')
VIDEO_FILE_PATH2 = os.path.join(UPLOAD_DIR, 'live_screen.webm')

@csrf_exempt
def upload_chunk(request):
    """ Append video chunks to a single file """
    if request.method == 'POST' and request.FILES.get('videoChunk'):
        chunk = request.FILES['videoChunk']
        
        with open(VIDEO_FILE_PATH, 'ab') as f:
            for chunk_part in chunk.chunks():
                f.write(chunk_part)
        
        return JsonResponse({"status": "success", "message": "Chunk appended."})
    return JsonResponse({"status": "failed", "message": "Invalid request."})

async def stream_video(request):
    """ Async view to serve the video file for progressive streaming. """
    if not os.path.exists(VIDEO_FILE_PATH):
        return JsonResponse({"status": "failed", "message": "No video file found"})

    # Range request handling for progressive loading
    range_header = request.headers.get('Range', None)
    file_size = os.path.getsize(VIDEO_FILE_PATH)

    # If there's a Range header, we'll serve the requested chunk
    if range_header:
        start, end = range_header.replace('bytes=', '').split('-')
        start = int(start)
        end = int(end) if end else file_size - 1
        length = (end - start) + 1

        # Open the video file asynchronously
        async def file_iterator():
            with open(VIDEO_FILE_PATH, 'rb') as f:
                f.seek(start)
                # Read and yield chunks asynchronously
                while chunk := f.read(8192):
                    yield chunk
                # Ensure the full requested range is served
                f.seek(start)
                yield f.read(length)

        response = StreamingHttpResponse(file_iterator(), status=206, content_type='video/webm')
        response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        response['Accept-Ranges'] = 'bytes'
        response['Content-Length'] = str(length)
        return response

    # If no Range header, return the whole file
    async def file_iterator_full():
        with open(VIDEO_FILE_PATH, 'rb') as f:
            # Yield chunks to stream the file
            while chunk := f.read(8192):
                yield chunk

    return StreamingHttpResponse(file_iterator_full(), content_type='video/webm')
def video_record_page(request):
    return render(request, 'record.html')
def view_video(request):
    return render(request, 'stream.html')
def view_screen(request):
    return render(request, 'screen.html')
def get_video_size(request):
    """ Return the current size of the video file being uploaded. """
    if os.path.exists(VIDEO_FILE_PATH):
        file_size = os.path.getsize(VIDEO_FILE_PATH)
        return JsonResponse({"status": "success", "file_size": file_size})
    return JsonResponse({"status": "failed", "message": "No video file found"})
@csrf_exempt
def upload_video(request):
    """ Append video chunks to a single file """
    if request.method == 'POST' and request.FILES.get('video_chunk'):
        chunk = request.FILES['video_chunk']
        
        with open(VIDEO_FILE_PATH2, 'ab') as f:
            for chunk_part in chunk.chunks():
                f.write(chunk_part)
        
        return JsonResponse({"status": "success", "message": "Chunk appended."})
    return JsonResponse({"status": "failed", "message": "Invalid request."})


def start_monitoring(request, exam_id):
    """Start monitoring screen and webcam."""
    user = request.user
    exam = Test.objects.get(id=exam_id)

    # Start monitoring in separate threads
    screen_thread = threading.Thread(target=capture_screen, args=(user, exam))
    webcam_thread = threading.Thread(target=monitor_webcam, args=(user, exam))
    screen_thread.start()
    webcam_thread.start()

    return JsonResponse({"message": "Monitoring started"})


def view_logs(request, exam_id):
    """View monitoring logs for an exam."""
    logs = MonitoringLog.objects.filter(exam_id=exam_id)
    return render(request, "exams/monitoring_logs.html", {"logs": logs})
# OpenVidu API URL and Secret
OPENVIDU_URL = "http://localhost:4443"  # Adjust based on your OpenVidu setup
OPENVIDU_SECRET = "my_secret"  # Replace with your actual secret key
USERNAME = "OPENVIDUAPP"
@csrf_exempt

def create_session(request):
    data = json.loads(request.body)
    customSessionId = data.get('customSessionId')
    print("0000000000000", customSessionId)
    
    url = "http://localhost:4443/openvidu/api/sessions"
    OPENVIDU_SECRET = "my_secret"
    USERNAME = "OPENVIDUAPP"

    # Encode the Authorization header
    auth_string = f"{USERNAME}:{OPENVIDU_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")

    # Payload for the request
    payload = json.dumps({
        "mediaMode": "ROUTED",
        "recordingMode": "MANUAL",
        "customSessionId": customSessionId,
        "forcedVideoCodec": "VP8",
        "allowTranscoding": False,
        "defaultRecordingProperties": {
            "name": "MyRecording",
            "hasAudio": True,
            "hasVideo": True,
            "outputMode": "COMPOSED",
            "recordingLayout": "BEST_FIT",
            "resolution": "1280x720",
            "frameRate": 25,
            "shmSize": 536870912,
            "mediaNode": {
                "id": "media_i-0c58bcdd26l11d0sd"
            }
        },
        "mediaNode": {
            "id": "media_i-0c58bcdd26l11d0sd"
        }
    })

    # Headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_base64}',
    }

    try:
        # Make the POST request
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()

        # Return the sessionId as a JsonResponse
        session_id = response.json().get("id")
        return JsonResponse({"sessionId": session_id}, status=200)

    except requests.exceptions.HTTPError as err:
        # Handle specific HTTP errors
        if err.response.status_code == 409:
            # Session already exists in OpenVidu
            return JsonResponse({"customSessionId": customSessionId}, status=409)
        else:
            # Return the error response
            return JsonResponse({"error": str(err)}, status=err.response.status_code)

    except json.JSONDecodeError:
        # Handle JSON parsing errors
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    
# OpenVidu server URL and secret
OPENVIDU_URL = 'http://localhost:4443'  # Adjust with your OpenVidu server URL
OPENVIDU_SECRET = 'my_secret'  # Replace with your OpenVidu secret

@csrf_exempt
def generate_token(request, session_id):
    if request.method == 'POST':
        
      
        try:
            # Construct the authorization string for OpenVidu
            auth_string = f"{USERNAME}:{OPENVIDU_SECRET}"
            auth_bytes = auth_string.encode("utf-8")
            auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
            
            # Extract participant name and customSessionId from the request body
            data = json.loads(request.body)
            user_name = data.get('username')
            customSessionId = data.get('customSessionId')

            if not user_name or not customSessionId:
                return JsonResponse({'errorMessage': 'username and customSessionId are required'}, status=400)
            
            print("customSessionId--customSessionId", customSessionId)

            # Create a session if it doesn't exist
            session_url = f"{OPENVIDU_URL}/api/sessions"
            session_data = {'mediaMode': 'ROUTED', 'customSessionId': customSessionId}

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Basic {auth_base64}',
            }

            session_response = requests.post(session_url, json=session_data, headers=headers)

            if session_response.status_code == 200:
                # If session is created successfully, generate a token for the participant
                session_info = session_response.json()
                print("Session info:", session_info)
                session_id = session_info['id']  # Get the session ID
                token_url = f"{OPENVIDU_URL}/api/sessions/{session_id}/connection"
                token_data = {'clientData': user_name, 'customSessionId': session_id}

                # Generate the token
                token_response = requests.post(token_url, json=token_data, headers=headers)

                if token_response.status_code == 200:
                    token = token_response.json()['token']
                    return JsonResponse({'token': token})
                else:
                    # Handle token generation failure
                    return JsonResponse({'errorMessage': 'Failed to generate token'}, status=500)

            elif session_response.status_code == 409:
                # Handle case where session already exists
                print("Session already exists:", customSessionId)
                token_url = f"{OPENVIDU_URL}/api/sessions/{customSessionId}/connection"
                token_data = {'clientData': user_name}

                # Generate a token for the existing session
                token_response = requests.post(token_url, json=token_data, headers=headers)

                if token_response.status_code == 200:
                    token = token_response.json()['token']
                    return JsonResponse({'token': token})
                else:
                    return JsonResponse({'errorMessage': 'Failed to generate token for existing session'}, status=500)

            else:
                # Handle session creation failure
                return JsonResponse({'errorMessage': 'Failed to create session'}, status=session_response.status_code)

        except json.JSONDecodeError:
            # Handle JSON parsing errors
            return JsonResponse({'errorMessage': 'Invalid JSON body'}, status=400)

        except requests.exceptions.RequestException as e:
            # Handle request exceptions
            return JsonResponse({'errorMessage': f'Request error: {str(e)}'}, status=500)

        except Exception as e:
            # Catch-all for unexpected errors
            return JsonResponse({'errorMessage': f'Unexpected error: {str(e)}'}, status=500)
    return JsonResponse({'errorMessage': 'Invalid request'}, status=400)







@csrf_exempt

def generate_token2(request):
    if request.method == "GET":
        # Extract session ID from the query parameters
        session_id = request.GET.get("session_id")
        auth_string = f"{USERNAME}:{OPENVIDU_SECRET}"
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
        #session_id = '100'
        if not session_id:
            return JsonResponse({"error": "sessionId parameter is required"}, status=400)

        # OpenVidu API configuration
        url = f"http://localhost:4443/openvidu/api/sessions/{session_id}/connection"
        headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth_base64}',
        }
        payload = json.dumps({
            "role": "PUBLISHER",  # Change to "SUBSCRIBER" if needed
            "data": "Custom metadata dd"  # Optional metadata
        })

        try:
            # Send request to OpenVidu API
            response = requests.post(url, headers=headers, data=payload)
            if response.status_code == 200:
                # Return the token in the response
               
                #token = response.json().get("token")
                
                #return JsonResponse({"token": token})
            
                token_data = response.json()
                print(token_data)
                return JsonResponse(token_data)
            else:
                # Return the OpenVidu server error message
                return JsonResponse({"error": response.json()}, status=response.status_code)
        except requests.RequestException as e:
            # Handle connection errors
            return JsonResponse({"error": f"Request failed: {str(e)}"}, status=500)

    # Return error if method is not GET
    return JsonResponse({"error": "Invalid HTTP method. Use GET."}, status=405)

    
    
def video_conf(request):
    return render(request, 'openvidu.html')
def testing(request):
    return render(request, 'index.html')