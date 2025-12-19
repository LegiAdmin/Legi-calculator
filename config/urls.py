
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from succession_engine.views import SimulatorView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Simulator UI
    path('simulator/', SimulatorView.as_view(), name='simulator'),
    
    # API Endpoints
    path('api/v1/', include('succession_engine.api.urls')),
    
    # OpenAPI Schema & Docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
