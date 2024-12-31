
from django.shortcuts import render
import logging
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger(__name__)

def camera_test(request):
    return render(request, 'offer.html')
@csrf_exempt
def ice_candidate(request):
    if request.method == 'POST':
        try:
            candidate_data = json.loads(request.body)
            candidate = candidate_data.get('candidate')
            
            # Forward the candidate to the other peer
            forward_candidate_to_peer(candidate)
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def forward_candidate_to_peer(candidate):
    # Logic to forward candidate to the other peer (based on your signaling mechanism)
    pass
def answer(request):
    if request.method == 'POST':
        # Parse the answer from the admin
        answer = json.loads(request.body).get('answer')
        
        # Here you send the answer to the candidate
        send_answer_to_candidate(answer)
        
        return JsonResponse({'status': 'answer_sent'})

    return JsonResponse({'error': 'Invalid method'}, status=405)

def admin_video_view(request):
    return render(request, 'admin.html')
def offer(request):
    if request.method == 'POST':
        # Get offer from the candidate
        offer = request.POST.get('offer')
        print(f"Received offer: {offer}")

        # Store offer in session for the admin to retrieve
        # Storing the offer in the session so that the admin can fetch it later
        request.session['candidate_offer'] = offer  # Store offer in session
        
        # Answer to send back to the candidate (simulated here for simplicity)
        answer = {
            'sdp': 'answer_sdp_data',
            'type': 'answer'
        }
        return JsonResponse(answer)
    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)

# View for admin to get the candidate's offer from the session
def admin_offer(request):
    if request.method == 'POST':
        # Retrieve the offer from the session
        offer = request.session.get('candidate_offer')

        if offer:
            # Simulate the offer being returned to the admin
            return JsonResponse({
                'sdp': offer,  # The offer we previously saved in the session
                'type': 'offer'
            })
        else:
            return JsonResponse({'error': 'No offer available'}, status=404)
    else:
        return JsonResponse({'error': 'Method Not Allowed'}, status=405)
