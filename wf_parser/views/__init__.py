from wf_parser.views.health import HealthCheckView
from wf_parser.views.epub.epub_view import EpubAnalysisView
from wf_parser.views.test import TestView
from wf_parser.views.text.text_view import TextAnalysisView
from wf_parser.views.subtitle.subtitle_view import SubtitleAnalysisView
from wf_parser.views.image import ImageAnalysisView, ImageAnalysisHealthView

__all__ = [
    'HealthCheckView',
    'EpubAnalysisView',
    'TestView',
    'TextAnalysisView',
    'SubtitleAnalysisView',
    'ImageAnalysisView',
    'ImageAnalysisHealthView'
]
