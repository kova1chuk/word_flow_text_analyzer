from rest_framework import serializers


class EPubUploadSerializer(serializers.Serializer):
    """Serializer for the EPUB file upload."""
    file = serializers.FileField(
        help_text="The .epub file to be processed."
    )

    class Meta:
        fields = ('file',)


class SubtitleUploadSerializer(serializers.Serializer):
    """Serializer for subtitle file uploads (SRT, VTT, TXT)."""
    file = serializers.FileField(
        help_text="The subtitle file to analyze (SRT, VTT, TXT)"
    )

    class Meta:
        fields = ('file',)
