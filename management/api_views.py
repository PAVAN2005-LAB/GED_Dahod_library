from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .serializers import CustomTokenObtainPairSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom Login Endpoint that returns clear error messages.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            return Response(
                {"error": "Token Error", "message": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            # Provide clear message for invalid credentials
            return Response(
                {"error": "Login Failed", "message": "Invalid username or password. Please try again."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_sitemap(request):
    """
    Returns a structured map of available API endpoints, report downloads, and public web routes.
    """
    return Response({
        "Public Web Routes": {
            "root": "/",
            "kiosk": "/kiosk/",
            "admin_login": "/admin/login/"
        },
        "API Endpoints": {
            "token_obtain": "/api/token/",
            "token_refresh": "/api/token/refresh/",
            "token_verify": "/api/token/verify/",
            "sitemap": "/api/sitemap/"
        },
        "Admin & Staff Endpoints": {
            "api_admin": "/admin/",
            "live_dashboard": "/dashboard/",
            "reports_dashboard": "/admin/reports/",
            "entry_exit_report": "/admin/reports/entry-exit/",
            "book_issues_report": "/admin/reports/book-issues/",
            "overdue_report": "/admin/reports/overdue-students/"
        }
    }, status=status.HTTP_200_OK)
