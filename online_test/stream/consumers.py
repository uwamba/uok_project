import json
from channels.generic.websocket import AsyncWebsocketConsumer

class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"call_{self.room_name}"

        # Join the room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get("type")  # Extract the 'type' field
        
        if message_type == "offer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_signal",
                    "message": {
                        "type": "offer",
                        "sdp": data.get("sdp")
                    }
                }
            )
        elif message_type == "answer":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_signal",
                    "message": {
                        "type": "answer",
                        "sdp": data.get("sdp")
                    }
                }
            )
        elif message_type == "candidate":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_signal",
                    "message": {
                        "type": "candidate",
                        "candidate": data.get("candidate"),
                        "sdpMid": data.get("sdpMid"),
                        "sdpMLineIndex": data.get("sdpMLineIndex")
                    }
                }
            )
        else:
            print("Unknown message type received:", data)

    async def send_signal(self, event):
        await self.send(text_data=json.dumps(event["message"]))
