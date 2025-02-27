var OV;
var session;


/* OPENVIDU METHODS */


function joinSession() {

	var mySessionId = document.getElementById("sessionId").value;
	var myUserName = document.getElementById("userName").value;

	// --- 1) Get an OpenVidu object ---

	OV = new OpenVidu();

	// --- 2) Init a session ---

	session = OV.initSession();

	// --- 3) Specify the actions when events take place in the session ---

	// On every new Stream received...
	
	session.on('streamCreated', event => {
		console.log('stream created and available')
		subscribeToStream(event.stream);
	});
	
	// Function to handle stream subscription and user data


	// On every Stream destroyed...
	session.on('streamDestroyed', event => {

		// Delete the HTML element with the user's nickname. HTML videos are automatically removed from DOM
		removeUserData(event.stream.connection);
	});

	// On every asynchronous exception...
	session.on('exception', (exception) => {
		console.warn(exception);
	});


	// --- 4) Connect to the session with a valid user token ---

	// Get a token from the OpenVidu deployment
	getToken(mySessionId,myUserName).then(response => {
		const token = response.token; // Extract the token string
		console.log('Extracted Token:', token); // Optional: Log the extracted token for debugging
	
		session.connect(token, { clientData: myUserName })
			.then(() => {
				// Successful connection
				console.log('Connected to the session');
				document.getElementById('session-title').innerText = mySessionId;
				document.getElementById('join').style.display = 'none';
				document.getElementById('session').style.display = 'block';

				const connections = session.remoteConnections;
                console.log('Existing connectionssssssssss:', connections);

				connections.forEach(connection => {
                    connection.streams.forEach(stream => {
                        console.log('Subscribing to existing stream:', stream);
                        subscribeToStream(stream);
                    });
                });

				
               // --- 6) Get your own camera stream with the desired properties ---
				var publisher = OV.initPublisher('video-container', {
					audioSource: true,
                    videoSource: true,
                    publishAudio: true,
                    publishVideo: true,
					resolution: '320x240',  // The resolution of your video
					frameRate: 30,			// The frame rate of your video
					insertMode: 'APPEND',	// How the video is inserted in the target element 'video-container'
					mirror: false       	// Whether to mirror your local video or not
				});

				// --- 7) Specify the actions when events take place in our publisher ---

				// When our HTML video has been added to DOM...
				console.log('adding video dom........');
				publisher.on('videoElementCreated', function (event) {
					console.log('adding video dom');
					initMainVideo(event.element, myUserName);
					appendUserData(event.element, myUserName);
					event.element['muted'] = true;
				});

				// --- 8) Publish your stream ---

				session.publish(publisher);
			})
			.catch(error => {
				console.error('Error connecting to the session:', error.code, error.message);
			});
	});
	
}

function leaveSession() {

	// --- 9) Leave the session by calling 'disconnect' method over the Session object ---

	session.disconnect();

	// Removing all HTML elements with user's nicknames.
	// HTML videos are automatically removed when leaving a Session
	removeAllUserData();

	// Back to 'Join session' page
	document.getElementById('join').style.display = 'block';
	document.getElementById('session').style.display = 'none';
}

window.onbeforeunload = function () {
	if (session) session.disconnect();
};


/* APPLICATION SPECIFIC METHODS */

window.addEventListener('load', function () {
	generateParticipantInfo();
});

function generateParticipantInfo() {
	document.getElementById("sessionId").value = "SessionA";
	document.getElementById("userName").value = "Participant" + Math.floor(Math.random() * 100);
}

function appendUserData(videoElement, connection) {
	var userData;
	var nodeId;
	if (typeof connection === "string") {
		userData = connection;
		nodeId = connection;
	} else {
		userData = JSON.parse(connection.data).clientData;
		nodeId = connection.connectionId;
	}
	var dataNode = document.createElement('div');
	dataNode.className = "data-node";
	dataNode.id = "data-" + nodeId;
	dataNode.innerHTML = "<p>" + userData + "</p>";
	videoElement.parentNode.insertBefore(dataNode, videoElement.nextSibling);
	addClickListener(videoElement, userData);
}

function removeUserData(connection) {
	var dataNode = document.getElementById("data-" + connection.connectionId);
	dataNode.parentNode.removeChild(dataNode);
}

function removeAllUserData() {
	var nicknameElements = document.getElementsByClassName('data-node');
	while (nicknameElements[0]) {
		nicknameElements[0].parentNode.removeChild(nicknameElements[0]);
	}
}

function addClickListener(videoElement, userData) {
	videoElement.addEventListener('click', function () {
		var mainVideo = $('#main-video video').get(0);
		if (mainVideo.srcObject !== videoElement.srcObject) {
			$('#main-video').fadeOut("fast", () => {
				$('#main-video p').html(userData);
				mainVideo.srcObject = videoElement.srcObject;
				$('#main-video').fadeIn("fast");
			});
		}
	});
}

function initMainVideo(videoElement, userData) {
	document.querySelector('#main-video video').srcObject = videoElement.srcObject;
	document.querySelector('#main-video p').innerHTML = userData;
	document.querySelector('#main-video video')['muted'] = true;
}
function subscribeToStream(stream) {
	// Subscribe to the stream
	const subscriber = session.subscribe(stream, 'video-container');

	// Handle the creation of the video element
	subscriber.on('videoElementCreated', event => {
		console.log('Video appended to DOM:', event.element);

		// Add user metadata below the video
		appendUserData(event.element, stream.connection.data); // Assuming clientData is stored in connection.data
	});
}

/**
 * --------------------------------------------
 * GETTING A TOKEN FROM YOUR APPLICATION SERVER
 * --------------------------------------------
 * The methods below request the creation of a Session and a Token to
 * your application server. This keeps your OpenVidu deployment secure.
 *
 * In this sample code, there is no user control at all. Anybody could
 * access your application server endpoints! In a real production
 * environment, your application server must identify the user to allow
 * access to the endpoints.
 *
 * Visit https://docs.openvidu.io/en/stable/application-server to learn
 * more about the integration of OpenVidu in your application server.
 */

var APPLICATION_SERVER_URL = "http://localhost:4443/";

function getToken(mySessionId,username) {
	return createSession(mySessionId).then(sessionId => createToken(sessionId,username));
}

const SESSION_URL = 'http://localhost:4443/api/sessions';

async function createSession(sessionId) {
	console.error('SESSION IDDDDDDDDD:', sessionId);
	const csrftoken = getCSRFToken();
    try {
		const response = await fetch(`http://127.0.0.1:8000/video/create_session/`, {
            method: 'POST',
            headers: {
                'Authorization': 'Basic ' + btoa('OPENVIDUAPP:my_secret'),  // Replace with your actual OpenVidu secret
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrftoken,  // Include CSRF token if required by your backend
            },
            body: JSON.stringify({ customSessionId: sessionId }),

		});

        if (!response.ok) {

			if (response.status === 409) {
				// Session already exists
				const sessionData = await response.json();
				console.log('Session already exists:', sessionData.customSessionId);
				return sessionData.customSessionId;
				
			} else {
				// Other errors
				const errorDetails = await response.json().catch(() => null); // Handle cases where response isn't JSON
				throw new Error(
					`HTTP Error: ${response.status} ${response.statusText}\n` +
					`Details: ${JSON.stringify(errorDetails)}`
				);
			}

            // Parse error details if possible
            
        }

    } catch (error) {
        console.error('Error creating session:', error.message || error);
    }
}
async function createToken(sessionId,username) {

    const csrftoken = getCSRFToken();  // Assuming you're using CSRF token protection, replace this if necessary

    console.log('Requesting token for sessionId:', sessionId);

    try {
        const response = await fetch(`http://127.0.0.1:8000/video/generate_token/${sessionId}/`, {
            method: 'POST',
            headers: {
                'Authorization': 'Basic ' + btoa('OPENVIDUAPP:my_secret'),  // Replace with your actual OpenVidu secret
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': csrftoken,  // Include CSRF token if required by your backend
            },
            body: JSON.stringify({ username: username, customSessionId: sessionId }), // Send the participant's username in the body
        });

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();  // Parse the JSON response
        return data;  // Return the response data (token)
    } catch (error) {
        console.error('Error occurred while fetching token:', error);
        throw error;  // Throw error for further handling if needed
    }
}



function getCSRFToken() {
	const name = 'csrftoken';
	const cookies = document.cookie.split(';');
	for (let cookie of cookies) {
		const [key, value] = cookie.trim().split('=');
		if (key === name) {
			return decodeURIComponent(value);
		}
	}
	return null;
}



