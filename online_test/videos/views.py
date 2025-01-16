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
from requests.auth import HTTPBasicAuth

from PIL import Image
from io import BytesIO
import cv2
from concurrent.futures import ThreadPoolExecutor
import torch
import dlib
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
        print('session id from dajngo create session function',session_id)
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
def check_session_exists(session_id):
    """
    Check if a session exists on the OpenVidu server.
    """
    url = f"{OPENVIDU_URL}/openvidu/api/sessions/{session_id}"
    response = requests.get(url, auth=HTTPBasicAuth('OPENVIDUAPP', OPENVIDU_SECRET))
    return response.status_code == 200
@csrf_exempt
def generate_token(request, session_id):
    if request.method == 'POST':
        
        
        try:
            
            if not check_session_exists(session_id):
              raise Exception(f"Session {session_id} does not exist.")
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


# OpenVidu server credentials

def monitor_candidate(request, test_id):
    # Create an OpenVidu session
    #openvidu = OpenVidu(OPENVIDU_URL, OPENVIDU_SECRET)
    #session = openvidu.create_session()

    # Generate a token for the candidate
   # token = session.generate_token()

    return render(request, 'admin/monitor_candidate.html', {
        'test_id': test_id,
        'session_id': "session.session_id",
        'token': "token",
    })



# Thread pool to handle multiple video streams
executor = ThreadPoolExecutor(max_workers=5)
@csrf_exempt
def process_frame(request):
    print(request.method)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            #print('dataaaaa',data)
            #user_name = data.get('username')
            frame = data.get('frame')
            print('frame')
            video_id = data.get('videoId')
            frame_data = frame.split('data:image/jpeg;base64,')[1]
            img_data = base64.b64decode(frame_data)
           # print(img_data)
            predFacePose(img_data)
            # Submit frame for analysis in a separate thread
            face = executor.submit(analyze_frame, img_data, video_id,frame_data)
            phone = executor.submit(detect_phone, img_data, video_id) 
            result_face = face.result()
            result_phone = phone.result()
  
            #result2 = future2.result()
            #print('the result of analysis here:', result)
            print('the result of analysis here3:', result_phone)
            
            return JsonResponse(result_face)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def analyze_frame(img_data, video_id,frame_data):
 
        try:
            # Convert to OpenCV image
        
            np_img = np.frombuffer(img_data, np.uint8)
            img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
            # Perform face detection
            landmark_detector = dlib.shape_predictor(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            for face in faces:
            
                
                    landmarks = landmark_detector(gray, face)
                    print('---------------------------------------')
                    
                    # Get the positions of the eyes (index 36-41 for left eye and 42-47 for right eye)
                    left_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)])
                    right_eye = np.array([(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)])
                    
                    # Find the center of both eyes
                    left_eye_center = np.mean(left_eye, axis=0)
                    right_eye_center = np.mean(right_eye, axis=0)

                    # Calculate the angle between the eyes to estimate the head orientation
                    eye_center_x = (left_eye_center[0] + right_eye_center[0]) / 2
                    eye_center_y = (left_eye_center[1] + right_eye_center[1]) / 2
                    
                    # If the center of the eyes moves left or right, we can assume the head is turning
                    if eye_center_x < frame_data.shape[1] / 2:
                        print('Looking Left')
                        head_direction = "Looking Left"
                    else:
                        print('Looking Right')
                        head_direction = "Looking Right"

                    # Draw the face and the direction text
                    cv2.rectangle(frame_data, (face.left(), face.top()), (face.right(), face.bottom()), (0, 255, 0), 2)
                    cv2.putText(frame_data, head_direction, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    return {'video_id': video_id, 'faces_detected': len(faces)}
        except Exception as e:
                    
                    print(f"Error occurred: {e}")
                    return None



model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
def detect_phone(frame_data,video_id):
    # Decode the base64 image
    #img_data = base64.b64decode(frame_data)
    np_arr = np.frombuffer(frame_data, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Convert BGR to RGB
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Run YOLOv5 model on the image
    results = model(img_rgb)
    print('model result',results)
    # Extract detections
    detections = results.pandas().xyxy[0]
   
    for _, row in detections.iterrows():
        if row['name'] == 'cell phone':
            print(f"Phone detected with confidence: {row['confidence']:.2f}")
            #return True, row['confidence']
            return {'video_id': video_id, 'Phone detected': row['confidence']}

    return False, None
from facenet_pytorch import MTCNN
from matplotlib import pyplot  as plt

import math
mtcnn = MTCNN(image_size=160,
              margin=0,
              min_face_size=20,
              thresholds=[0.6, 0.7, 0.7], # MTCNN thresholds
              factor=0.709,
              post_process=True,
              device='cpu' # If you don't have GPU
        )
def npAngle(a, b, c):
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b) 
    
    cosine_angle = np.dot(ba, bc)/(np.linalg.norm(ba)*np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)
    
    return np.degrees(angle)
def predFacePose(imgaePath):
    with open('output_image.jpg', 'wb') as file:
     file.write(imgaePath)
   
    im = Image.open('output_image.jpg') # Reading the image
    
    if im.mode != "RGB": # Convert the image if it has more than 3 channels, because MTCNN will refuse anything more than 3 channels.
        im = im.convert('RGB')
    
    bbox_, prob_, landmarks_ = mtcnn.detect(im, landmarks=True) # The detection part producing bounding box, probability of the detected face, and the facial landmarks
    angle_R_List = []
    angle_L_List = []
    predLabelList = []
   
    for bbox, landmarks, prob in zip(bbox_, landmarks_, prob_):
        if bbox is not None: # To check if we detect a face in the image
            if prob > 0.9: # To check if the detected face has probability more than 90%, to avoid 
                angR = npAngle(landmarks[0], landmarks[1], landmarks[2]) # Calculate the right eye angle
                angL = npAngle(landmarks[1], landmarks[0], landmarks[2])# Calculate the left eye angle
                angN = npAngle(landmarks[0], landmarks[2], landmarks[1])  # Nose angle
                angle_R_List.append(angR)
                angle_L_List.append(angL)
                print("Nose Angle: {} - Right Eye Angle: {} - Left Eye Angle: {}".format(angN, angR, angL))

                if ((int(angR) in range(35, 57)) and (int(angL) in range(35, 58))):
                    predLabel='Frontal'
                    predLabelList.append(predLabel)
                    print(predLabelList)
                else: 
                    if angR < angL and angN >= 40:
                        predLabel = 'Left Profile'
                    elif angR > angL and angN >= 40:
                        predLabel = 'Right Profile'
                    elif angN > 60:
                        predLabel = 'Upward'
                    elif angN < 40:
                        predLabel = 'Downward'
                    else:
                        predLabel = 'Unknown'
                    predLabelList.append(predLabel)
            else:
                print('The detected face is Less then the detection threshold')
        else:
            print('No face detected in the image')
#Nose Angle: 96.36418748661991 - Right Eye Angle: 41.19043268321722 - Left Eye Angle: 42.445379830162885
#Nose Angle: 59.782075240300735 - Right Eye Angle: 31.645555243218418 - Left Eye Angle: 88.57236951648083
#Nose Angle: 74.22350687040046 - Right Eye Angle: 58.61101968012335 - Left Eye Angle: 47.16547344947621