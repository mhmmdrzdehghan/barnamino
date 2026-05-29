import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"chat_{self.conversation_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def ai_message(self, event):
        await self.send(text_data=json.dumps({
            "text": event["text"],
            "role": event["role"],
        }))


    async def stream_done(self, event):
        await self.send(text_data=json.dumps({
            "type": "done",
            "full_text": event["full_text"]
        }))
