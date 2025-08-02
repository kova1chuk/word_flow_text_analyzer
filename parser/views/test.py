from .base import APIView, Response, nltk


class TestView(APIView):
    """
    Test endpoint to verify API functionality
    """

    def get(self, request):
        return Response({
            'message': 'API is working correctly',
            'nltk_available': nltk.data.find('tokenizers/punkt') is not None,
            'endpoints': {
                'health': '/api/health/',
                'upload': '/api/upload/',
                'test': '/api/test/',
                'text': '/api/text/',
                'subtitle': '/api/subtitle/'
            }
        })

    def post(self, request):
        return Response({
            'message': 'POST request received successfully',
            'data': request.data if hasattr(request, 'data') else 'No data'
        })
