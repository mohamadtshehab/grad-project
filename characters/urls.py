from django.urls import path
from characters.views import character_relationships

app_name = 'characters'

urlpatterns = [
    path('<slug:character_id>/relationships/', character_relationships, name='character-relationships'),
]
