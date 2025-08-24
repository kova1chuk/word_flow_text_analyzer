import os
import logging
import tempfile
import uuid
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from ..lib.image_processor import ImageProcessor, OCREngine
from ..models import ImageAnalysisResult, ImageAnalysisSession
from ..serializers import BatchImageAnalysisRequestSerializer, ImageAnalysisSessionSerializer
from django.db import models

logger = logging.getLogger(__name__)


class BatchImageAnalysisView(APIView):
    """View for batch processing multiple images"""

    @swagger_auto_schema(
        operation_description="Process multiple images in batch with OCR, language detection, and word validation",
        request_body=BatchImageAnalysisRequestSerializer,
        responses={
            202: openapi.Response(
                description="Batch processing started",
                examples={
                    "application/json": {
                        "success": True,
                        "session_id": "uuid-string",
                        "message": "Batch processing started",
                        "total_images": 5
                    }
                }
            ),
            400: openapi.Response(
                description="Bad request - invalid parameters or files",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Invalid request parameters"
                    }
                }
            )
        }
    )
    def post(self, request):
        """Start batch processing of multiple images"""
        try:
            # Validate request
            serializer = BatchImageAnalysisRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get validated data
            images = serializer.validated_data['images']
            engine_name = serializer.validated_data.get(
                'engine', 'google_vision')  # Default to Google Vision
            preprocess = serializer.validated_data.get('preprocess', True)
            validate_words = serializer.validated_data.get(
                'validate_words', True)
            session_name = serializer.validated_data.get(
                'session_name', f'Batch_{uuid.uuid4().hex[:8]}')

            # Validate engine
            try:
                engine = OCREngine(engine_name.lower())
            except ValueError:
                return Response({
                    'success': False,
                    'error': f'Invalid OCR engine. Available engines: {[str(e.value) for e in OCREngine]}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Create session
            session = ImageAnalysisSession.objects.create(
                session_id=str(uuid.uuid4()),
                total_images=len(images),
                ocr_engine=engine.value,
                preprocess_enabled=preprocess,
                word_validation_enabled=validate_words
            )

            # Start background processing
            self._process_batch_async(
                session, images, engine, preprocess, validate_words)

            return Response({
                'success': True,
                'session_id': session.session_id,
                'message': 'Batch processing started',
                'total_images': len(images),
                'session': ImageAnalysisSessionSerializer(session).data
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Batch processing failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _process_batch_async(self, session: ImageAnalysisSession, images: List,
                             engine: OCREngine, preprocess: bool, validate_words: bool):
        """Process images in background using ThreadPoolExecutor"""
        def process_single_image(image_file):
            """Process a single image and return result"""
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image_file.name)[1]) as temp_file:
                    for chunk in image_file.chunks():
                        temp_file.write(chunk)
                    temp_file_path = temp_file.name

                try:
                    # Create processor
                    processor = self._create_processor_with_credentials(engine)

                    # Process image
                    result = processor.process_image(
                        image_path=temp_file_path,
                        engine=engine,
                        preprocess=preprocess,
                        validate_words=validate_words
                    )

                    # Get summary
                    summary = processor.get_processing_summary(result)

                    # Save result to database
                    analysis_result = ImageAnalysisResult.objects.create(
                        image_name=image_file.name,
                        image_size=image_file.size,
                        content_type=image_file.content_type,
                        extracted_text=result.text,
                        detected_language=result.language,
                        confidence_score=result.confidence,
                        ocr_engine=result.engine,
                        processing_time=result.processing_time,
                        total_words=summary['total_words'],
                        valid_words=summary['valid_words'],
                        invalid_words=summary['invalid_words'],
                        accuracy_percentage=summary['accuracy_percentage'],
                        word_details=[
                            {
                                'text': word.text,
                                'confidence': word.confidence,
                                'bounding_box': word.bounding_box,
                                'is_valid': word.is_valid,
                                'suggestions': word.suggestions,
                                'language': word.language
                            }
                            for word in result.words
                        ]
                    )

                    # Update session progress
                    session.processed_images += 1
                    session.successful_images += 1
                    session.save()

                    logger.info(
                        f"Successfully processed image {image_file.name} in session {session.session_id}")
                    return {'success': True, 'image_name': image_file.name, 'result_id': analysis_result.id}

                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_file_path)
                    except OSError:
                        logger.warning(
                            f"Could not delete temporary file: {temp_file_path}")

            except Exception as e:
                logger.error(
                    f"Failed to process image {image_file.name}: {str(e)}")
                session.processed_images += 1
                session.failed_images += 1
                session.save()
                return {'success': False, 'image_name': image_file.name, 'error': str(e)}

        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=min(4, len(images))) as executor:
            # Submit all images for processing
            future_to_image = {
                executor.submit(process_single_image, image): image
                for image in images
            }

            # Process completed futures
            for future in as_completed(future_to_image):
                try:
                    result = future.result()
                    if result['success']:
                        logger.info(
                            f"Image {result['image_name']} processed successfully")
                    else:
                        logger.warning(
                            f"Image {result['image_name']} failed: {result['error']}")
                except Exception as e:
                    logger.error(
                        f"Unexpected error in batch processing: {str(e)}")

        # Mark session as completed
        session.mark_completed()
        logger.info(f"Batch processing session {session.session_id} completed")


class BatchImageAnalysisStatusView(APIView):
    """View for checking batch processing status"""

    @swagger_auto_schema(
        operation_description="Get the status of a batch image processing session",
        manual_parameters=[
            openapi.Parameter(
                'session_id',
                openapi.IN_QUERY,
                description="Session ID to check status for",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Session status retrieved successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "session_id": "uuid-string",
                            "status": "processing",
                            "progress": {
                                "total": 5,
                                "processed": 3,
                                "successful": 2,
                                "failed": 1
                            }
                        }
                    }
                }
            ),
            404: openapi.Response(
                description="Session not found",
                examples={
                    "application/json": {
                        "success": False,
                        "error": "Session not found"
                    }
                }
            )
        }
    )
    def get(self, request):
        """Get the status of a batch processing session"""
        try:
            session_id = request.query_params.get('session_id')
            if not session_id:
                return Response({
                    'success': False,
                    'error': 'Session ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get session
            try:
                session = ImageAnalysisSession.objects.get(
                    session_id=session_id)
            except ImageAnalysisSession.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Session not found'
                }, status=status.HTTP_404_NOT_FOUND)

            # Get session data
            session_data = ImageAnalysisSessionSerializer(session).data

            return Response({
                'success': True,
                'data': session_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Failed to get session status: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Failed to get session status: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BatchImageAnalysisResultsView(APIView):
    """View for retrieving batch processing results"""

    @swagger_auto_schema(
        operation_description="Get results from a completed batch image processing session",
        manual_parameters=[
            openapi.Parameter(
                'session_id',
                openapi.IN_QUERY,
                description="Session ID to get results for",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'format',
                openapi.IN_QUERY,
                description="Output format (json, summary)",
                type=openapi.TYPE_STRING,
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Results retrieved successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "data": {
                            "session_summary": {...},
                            "results": [...]
                        }
                    }
                }
            )
        }
    )
    def get(self, request):
        """Get results from a completed batch processing session"""
        try:
            session_id = request.query_params.get('session_id')
            output_format = request.query_params.get('format', 'json')

            if not session_id:
                return Response({
                    'success': False,
                    'error': 'Session ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get session
            try:
                session = ImageAnalysisSession.objects.get(
                    session_id=session_id)
            except ImageAnalysisSession.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Session not found'
                }, status=status.HTTP_404_NOT_FOUND)

            # Check if session is completed
            if session.status != 'completed':
                return Response({
                    'success': False,
                    'error': f'Session is not completed yet. Current status: {session.status}'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Get results
            results = ImageAnalysisResult.objects.filter(
                created_at__gte=session.started_at,
                created_at__lte=session.completed_at
            ).order_by('created_at')

            if output_format == 'summary':
                # Return summary only
                response_data = {
                    'session_summary': ImageAnalysisSessionSerializer(session).data,
                    'results_count': results.count(),
                    'overall_accuracy': results.aggregate(
                        avg_accuracy=models.Avg('accuracy_percentage')
                    )['avg_accuracy'] or 0.0
                }
            else:
                # Return full results
                from ..serializers import ImageAnalysisResultSerializer
                response_data = {
                    'session_summary': ImageAnalysisSessionSerializer(session).data,
                    'results': ImageAnalysisResultSerializer(results, many=True).data
                }

            return Response({
                'success': True,
                'data': response_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(
                f"Failed to get session results: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'error': f'Failed to get session results: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _create_processor_with_credentials(self, engine: OCREngine) -> ImageProcessor:
        """Create an ImageProcessor with Google Cloud credentials"""
        try:
            # Check for Google Cloud credentials in settings or environment
            google_credentials = getattr(
                settings, 'GOOGLE_CLOUD_CREDENTIALS_PATH', None)

            # Create processor with Google credentials
            processor = ImageProcessor(
                preferred_engine=engine,
                google_credentials_path=google_credentials
            )

            return processor

        except Exception as e:
            logger.warning(
                f"Could not create processor with Google credentials: {e}")
            # Fallback to basic processor
            return ImageProcessor(preferred_engine=engine)
