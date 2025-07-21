"""
URL configuration for innkeeper project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenRefreshView
from users.authentication import InkeeperTokenObtainPairView


urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT auth endpoints
    path('api/auth/login/', InkeeperTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User registration and profile endpoints
    path('api/auth/', include('users.urls')),

    # Main API endpoints
    path('api/', include('api.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
