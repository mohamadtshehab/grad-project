from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Add your app URLs here when you create them
    # path('api/auth/', include('authentication.urls')),
    # path('api/books/', include('books.urls')),
    # path('api/chunks/', include('chunks.urls')),
    # path('api/characters/', include('characters.urls')),
    # path('api/users/', include('user.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
