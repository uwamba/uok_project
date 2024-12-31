// camera.js

function getCSRFToken() {
    let cookieValue = null;
    document.cookie.split(';').forEach(function(cookie) {
        if (cookie.trim().startsWith('csrftoken=')) {
            cookieValue = cookie.trim().substring('csrftoken='.length);
        }
    });
    return cookieValue;
}

const video = document.getElementById('localVideo');

// Get the candidate's video feed
navigator.mediaDevices.getUserMedia({ video: true, audio: false }).then(stream => {
    video.srcObject = stream;

    const pc = new RTCPeerConnection();
    pc.addTrack(stream.getTracks()[0], stream);

    // Create an offer and send it to the server
    pc.createOffer().then(offer => {
        console.log("Generated Offer:", offer);  // Check offer in the console
        return fetch('stream/offer/', {
            method: 'POST',  // Use POST method
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),  // Add CSRF token to the request header
            },
            body: JSON.stringify({
                offer: {
                    sdp: offer.sdp,
                    type: offer.type
                }
            })
        });
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to send offer: " + response.statusText);
        }
        return response.json();
    })
    .then(data => {
        console.log("Received Answer:", data);  // Check response in the console
        return pc.setRemoteDescription(data.answer);
    })
    .catch(error => console.error("Error:", error));
});
