from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class HealthCheckView(APIView):
    """
    Health check endpoint to verify API status
    """

    @swagger_auto_schema(
        operation_description="Check the health status of the API",
        operation_summary="Health check",
        responses={
            200: openapi.Response(
                description="API is healthy",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Health status"
                        ),
                        'message': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Health message"
                        ),
                        'version': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="API version"
                        )
                    }
                ),
                examples={
                    "application/json": {
                        "status": "healthy",
                        "message": "Word Flow Text Analyzer API is running",
                        "version": "v1.0.0"
                    }
                }
            )
        },
        tags=['Health'],
        operation_id='health_check'
    )
    def get(self, request):
        return Response({
            'status': 'healthy',
            'message': 'Word Flow Text Analyzer API is running',
            'version': 'v1.0.0'
        })
