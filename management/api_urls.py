from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .api_views import CustomTokenObtainPairView, api_sitemap

urlpatterns = [
    # JWT Authentication Endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # Generic API Sitemap
    path('sitemap/', api_sitemap, name='api_sitemap'),
]
