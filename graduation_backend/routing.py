from django.urls import re_path
from utils.consumers import UserNotificationsConsumer

websocket_urlpatterns = [
	re_path(r"ws/notifications/$", UserNotificationsConsumer.as_asgi()),
]


