from rest_framework import serializers


class EPubUploadSerializer(serializers.Serializer):
    """Serializer for the EPUB file upload."""
    file = serializers.FileField(
        help_text="The .epub file to be processed."
    )

    class Meta:
        fields = ('file',)
