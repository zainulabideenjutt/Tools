import uuid
from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from .models import (
    ImageConverterModel,
    PdfToImagesModel,
    ImagesToPDFModel,
    YouTubeDownloaderModel,
    validate_file_size,
    WordToPDF
)
from django.core.exceptions import ValidationError
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile

class ImageConverterSerializer(serializers.ModelSerializer):
    original_images = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=True,
        help_text="List of images to convert."
    )
    convert_to = serializers.ChoiceField(
        choices=[
            ('.jpg', 'JPEG'),
            ('.png', 'PNG'),
            ('.gif', 'GIF'),
            ('.webp', 'WEBP'),
            ('.tiff', 'TIFF'),
            ('.bmp', 'BMP')
        ],
        write_only=True,
        required=True,
        help_text="Choose the format to convert the images to."
    )

    class Meta:
        model = ImageConverterModel
        fields = ['id', 'original_images', 'convert_to', 'converted_image', 'status', 'error_message', 'created_at', 'updated_at']
        read_only_fields = ['converted_image', 'status', 'error_message', 'created_at', 'updated_at']

    def validate_original_images(self, values):
        if not values:
            raise serializers.ValidationError("Please provide at least one image for conversion.")

        valid_extensions = ['png', 'gif', 'webp', 'tiff', 'bmp', 'jpg', 'jpeg']
        for value in values:
            # Validate file extension
            ext = value.name.split('.')[-1].lower()
            if ext not in valid_extensions:
                raise serializers.ValidationError(
                    f"Unsupported file extension for {value.name}. Allowed extensions are: {', '.join(valid_extensions)}"
                )

            # Validate file size
            if value.size > 10 * 1024 * 1024:  # 10MB
                raise serializers.ValidationError(f"Image size for {value.name} cannot exceed 10MB.")

        return values

    def create(self, validated_data):
        convert_to = validated_data.pop('convert_to', None)
        instance = super().create(validated_data)
        return instance

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['original_image_size'] = instance.original_image.size if instance.original_image else None
        data['converted_image_size'] = instance.converted_image.size if instance.converted_image else None
        return data

class PdfToImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = PdfToImagesModel
        fields = ['id', 'document', 'converted_images', 'status', 'error_message', 'page_count', 'created_at', 'updated_at']
        read_only_fields = ['converted_images', 'status', 'error_message', 'page_count', 'created_at', 'updated_at']

    def validate_document(self, value):
        if not value:
            raise serializers.ValidationError("Please provide a PDF document for conversion.")

        if not value.name.lower().endswith('.pdf'):
            raise serializers.ValidationError("Only PDF files are allowed.")

        # Validate file size
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("PDF size cannot exceed 10MB.")

        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['document_size'] = instance.document.size if instance.document else None
        if instance.converted_images:
            data['image_count'] = len(instance.converted_images)
        return data


class ImagesToPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImagesToPDFModel
        fields = ['id', 'images', 'converted_pdf', 'status', 'error_message', 'created_at', 'updated_at']
        read_only_fields = ['converted_pdf', 'status', 'error_message', 'created_at', 'updated_at']

    def validate(self, data):
        if not self.initial_data.get('images'):
            raise serializers.ValidationError("Please provide at least one image for conversion.")

        for image in self.initial_data.getlist('images'):
            if not image.content_type.startswith('image/'):
                raise serializers.ValidationError(f"{image.name} is not a valid image file.")

            if image.size > 10 * 1024 * 1024:  # 10MB
                raise serializers.ValidationError(f"Image {image.name} size cannot exceed 10MB.")

        return data

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        
        # Add download URL for converted PDF
        if instance.converted_pdf and request:
            data['converted_pdf'] = request.build_absolute_uri(instance.converted_pdf.url)
            data['pdf_size'] = instance.converted_pdf.size 
        
        # Format images data
        if instance.images:
            formatted_images = []
            for img in instance.images:
                formatted_images.append({
                    'name': img.get('name'),
                    'size': img.get('size'),
                    'type': img.get('type')
                })
            data['images'] = formatted_images
            
        return data


class YouTubeDownloaderSerializer(serializers.ModelSerializer):
    video_url = serializers.URLField(
        max_length=512,
        required=True,
        help_text="YouTube video URL to download"
    )

    class Meta:
        model = YouTubeDownloaderModel
        fields = ['id', 'video_url', 'title', 'download_options', 'status', 'error_message', 'created_at', 'updated_at']
        read_only_fields = ['title', 'download_options', 'status', 'error_message', 'created_at', 'updated_at']

    def validate_video_url(self, value):
        if not value:
            raise serializers.ValidationError("YouTube URL is required.")
        if 'youtube.com' not in value and 'youtu.be' not in value:
            raise serializers.ValidationError("Invalid YouTube URL format.")
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Format download options for frontend consumption
        if instance.download_options:
            formatted_options = []
            for quality, info in instance.download_options.items():
                option_type = 'audio' if 'audio' in quality.lower() else 'video'
                formatted_options.append({
                    'label': quality,
                    'value': info.get('url'),
                    'type': option_type,
                    'ext': info.get('ext'),
                    'filesize': info.get('filesize')
                })
            data['download_options'] = formatted_options
        
        return data
class WordToPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = WordToPDF
        fields = ['id', 'document', 'converted_pdf', 'status', 'error_message', 'created_at', 'updated_at']
        read_only_fields = ['converted_pdf', 'status', 'error_message', 'created_at', 'updated_at']

    def validate_document(self, value):
        if not value:
            raise serializers.ValidationError("Please provide a Word document for conversion.")

        ext = value.name.split('.')[-1].lower()
        if ext not in ['doc', 'docx']:
            raise serializers.ValidationError("Only DOC and DOCX files are allowed.")

        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("Document size cannot exceed 10MB.")

        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['document_size'] = instance.document.size if instance.document else None
        return data