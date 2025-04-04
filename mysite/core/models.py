from django.db import models
from django.core.validators import FileExtensionValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
import os

def validate_file_size(value):
    max_size = 10 * 1024 * 1024  # 10MB
    if value.size > max_size:
        raise ValidationError(f'File size cannot exceed {max_size/1024/1024}MB')

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class WordToPDF(BaseModel):
    document = models.FileField(
        upload_to='word_documents/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(allowed_extensions=['doc', 'docx']),
            validate_file_size
        ],
        help_text='Upload Word document for conversion (supported formats: DOC, DOCX)'
    )
    converted_pdf = models.FileField(
        upload_to='converted_pdfs/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text='Stores the converted PDF file'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)

    def delete(self, *args, **kwargs):
        if self.document:
            self.document.delete(save=False)
        if self.converted_pdf:
            self.converted_pdf.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Word to PDF Conversion {self.id} - {self.status}"
class ImageConverterModel(BaseModel):
    original_image = models.ImageField(
        upload_to='original_images/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'gif', 'webp', 'tiff', 'bmp', 'jpg', 'jpeg']),
            validate_file_size
        ],
        help_text='Upload original image for conversion (supported formats: PNG, GIF, WEBP, TIFF, BMP, JPG)'
    )
    converted_image = models.ImageField(
        upload_to='converted_images/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text='Stores the converted image'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)

    def delete(self, *args, **kwargs):
        if self.original_image:
            self.original_image.delete(save=False)
        if self.converted_image:
            self.converted_image.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Image Conversion {self.id} - {self.status}"

class PdfToImagesModel(BaseModel):
    document = models.FileField(
        upload_to='documents/%Y/%m/%d/',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf']),
            validate_file_size
        ],
        help_text='Upload PDF document for conversion (max size: 10MB)'
    )
    converted_images = models.JSONField(
        blank=True,
        null=True,
        help_text='Stores URLs and metadata of converted images'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.document:
            self.document.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"PDF to Images {self.id} - {self.status}"

class ImagesToPDFModel(BaseModel):
    images = models.JSONField(
        blank=True,
        null=True,
        help_text='Stores URLs and metadata of uploaded images'
    )
    converted_pdf = models.FileField(
        upload_to='converted_pdfs/%Y/%m/%d/',
        null=True,
        blank=True,
        help_text='Stores the converted PDF file'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)

    def delete(self, *args, **kwargs):
        if self.converted_pdf:
            self.converted_pdf.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Images to PDF {self.id} - {self.status}"
class YouTubeDownloaderModel(BaseModel):
    video_url = models.URLField(
        max_length=512,
        help_text='YouTube video URL to download'
    )
    title = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text='Title of the YouTube video'
    )
    download_options = models.JSONField(
        blank=True,
        null=True,
        help_text='Available download options with quality and format'
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"YouTube Download {self.id} - {self.status}"



    
