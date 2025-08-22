from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.utils import timezone


class UserNotificationsConsumer(AsyncJsonWebsocketConsumer):
	async def connect(self):
		user = self.scope.get("user")
		print(f"🔌 WebSocket connection attempt - User: {user}")
		print(f"🔌 Scope keys: {list(self.scope.keys())}")
		
		# For testing, accept connection even without auth
		if user and user.is_authenticated:
			self.group_name = f"user_{user.id}"
			await self.channel_layer.group_add(self.group_name, self.channel_name)
			print(f"✅ Authenticated user connected to group: {self.group_name}")
		else:
			# For testing purposes, create a test group
			self.group_name = "test_group"
			await self.channel_layer.group_add(self.group_name, self.channel_name)
			print(f"⚠️  Test connection to group: {self.group_name}")
		
		await self.accept()
		print(f"✅ WebSocket connection accepted")

	async def disconnect(self, close_code):
		group = getattr(self, "group_name", None)
		if group:
			await self.channel_layer.group_discard(group, self.channel_name)

	async def job_update(self, event):
		"""Handle job update events."""
		print(f"📨 Consumer received job update event: {event}")
		
		# Remove the 'type' field added by Django Channels before sending to client
		event_data = {k: v for k, v in event.items() if k != 'type'}
		
		await self.send_json(event_data)
		print(f"✅ Standardized event sent to WebSocket client")

	async def receive_json(self, content):
		"""Handle incoming messages from client"""
		print(f"📨 Received message: {content}")
		
		# Echo back for testing
		await self.send_json({
			"type": "echo",
			"message": f"Echo: {content.get('message', 'No message')}",
			"timestamp": timezone.now().isoformat()
		})


