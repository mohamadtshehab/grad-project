from django.urls import path
from characters.views import character_relationships, latest_character_profiles, character_detail

app_name = 'characters'

urlpatterns = [
    path('<slug:character_id>/', character_detail, name='character-detail'),
    path('<slug:character_id>/relationships/', character_relationships, name='character-relationships'),
    path('latest-profiles/', latest_character_profiles, name='latest-character-profiles'),
]
