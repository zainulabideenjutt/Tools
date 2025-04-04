from rest_framework import generics, status
from .serializers import ImagesToPDFSerializer
from .models import ImagesToPDFModel
import pythoncom
from PIL import Image
import tempfile
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files import File
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.utils import timezone
from pathlib import Path

from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.exceptions import APIException
from rest_framework.parsers import MultiPartParser, FormParser

import os
import shutil
import datetime
import uuid
import random
import string
import logging
import traceback

import fitz
import webp
from PIL import Image, ImageFilter
from fpdf import FPDF
import yt_dlp
from spellchecker import SpellChecker
from docx2pdf import convert

logger = logging.getLogger(__name__)

class BaseAPIException(APIException):
    def __init__(self, detail=None, code=None):
        super().__init__(detail, code)
        logger.error(f"{self.__class__.__name__}: {detail}\n{traceback.format_exc()}")

class FileProcessingError(BaseAPIException):
    status_code = 500
    default_detail = 'An error occurred while processing the file.'

class InvalidFileError(BaseAPIException):
    status_code = 400
    default_detail = 'Invalid file format or content.'

class FileSizeError(BaseAPIException):
    status_code = 400
    default_detail = 'File size exceeds the maximum allowed limit.'

class ProcessingLimitError(BaseAPIException):
    status_code = 400
    default_detail = 'Processing limit exceeded.'
# from pdf2image import convert_from_path
# from pdf2docx import Converter, parse

# Import your serializers and models
from .serializers import (
    PdfToImagesSerializer,
    WordToPDFSerializer,
    ImageConverterSerializer,
    ImagesToPDFSerializer,
    YouTubeDownloaderSerializer
)
from .models import (
    PdfToImagesModel,
    WordToPDF,
    ImageConverterModel,
    ImagesToPDFModel,
    YouTubeDownloaderModel
)



# ------------------------ ImageConverter ------------------------
class ImageConverter(generics.ListCreateAPIView):
    """Handle image format conversion operations.
    
    Supports converting images between different formats including JPG, PNG, WEBP, etc.
    Includes proper error handling and input validation.
    """
    queryset = ImageConverterModel.objects.all()
    serializer_class = ImageConverterSerializer
    parser_classes = (MultiPartParser, FormParser)
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif'}
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

    def post(self, request, *args, **kwargs):
        try:
            serializer = ImageConverterSerializer(data=request.data)
            if not serializer.is_valid():
                logger.error(f"Invalid serializer data: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            original_images = serializer.validated_data.get('original_images', [])
            convert_to = serializer.validated_data.get('convert_to')
            if convert_to not in self.SUPPORTED_FORMATS:
                raise InvalidFileError(f"Invalid target format. Supported formats: {', '.join(self.SUPPORTED_FORMATS)}")

            converted_images = []
            for original_image in original_images:
                try:
                    # Generate unique filename
                    image_name = os.path.splitext(os.path.basename(original_image.name))[0]
                    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                    converted_image_name = f"{image_name}_{random_string}_Converted_To_{convert_to[1:].upper()}{convert_to}"

                    # Process image conversion
                    image = Image.open(original_image)
                    img_content = ContentFile(b'')

                    if convert_to in ['.jpg', '.jpeg']:
                        rgb_image = image.convert('RGB')
                        rgb_image.save(img_content, format='JPEG', quality=90)
                    else:
                        image.save(img_content, format=convert_to[1:].upper())

                    # Create instance for each image
                    instance = ImageConverterModel.objects.create()
                    instance.original_image.save(original_image.name, original_image)
                    instance.converted_image.save(converted_image_name, img_content, save=True)
                    logger.info(f"Successfully converted image {original_image.name} to {convert_to} format")

                    converted_images.append({
                        "id": instance.id,
                        "original_image": request.build_absolute_uri(instance.original_image.url),
                        "converted_image": request.build_absolute_uri(instance.converted_image.url)
                    })

                except Exception as e:
                    logger.error(f"Error processing image {original_image.name}: {str(e)}")
                    # Clean up the current instance if it exists
                    if 'instance' in locals():
                        instance.delete()

            if not converted_images:
                raise FileProcessingError("Failed to convert any images")

            return Response(converted_images, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Unexpected error in image conversion: {str(e)}")
            return Response({"error": str(e)}, status=getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR))

    def delete(self, request, *args, **kwargs):
        # Delete all instances and their associated images
        instances = ImageConverterModel.objects.all()
        for instance in instances:
            # Delete original image file
            instance.original_image.delete(save=False)
            # Delete converted image file
            instance.converted_image.delete(save=False)
            instance.delete()  # Delete model instance

        return Response({"message": "Images deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ------------------------ RetrieveDestroyImage ------------------------
class RetrieveDestroyImage(generics.RetrieveDestroyAPIView):
    queryset = ImageConverterModel.objects.all()
    serializer_class = ImageConverterSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()  # Get the object instance

        # Delete the original and converted images if they exist
        if instance.original_image:
            instance.original_image.delete(save=False)
        if instance.converted_image:
            instance.converted_image.delete(save=False)

        # Now delete the instance from the database
        instance.delete()

        return Response({"message": "All images deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# ------------------------ ImagesToPDFView ------------------------
class YouTubeDownloaderView(generics.ListCreateAPIView):
    serializer_class = YouTubeDownloaderSerializer
    queryset = YouTubeDownloaderModel.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Initialize yt-dlp with options
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract video information
                info = ydl.extract_info(serializer.validated_data['video_url'], download=False)
                
                # Prepare download options
                download_options = {}
                
                # Add video formats
                formats = info.get('formats', [])
                resolutions = ['1080p', '720p', '480p', '360p', '240p', '144p']
                for resolution in resolutions:
                    height = int(resolution[:-1])
                    matching_format = next(
                        (f for f in formats 
                         if f.get('height') == height 
                         and f.get('ext') == 'mp4' 
                         and f.get('acodec') != 'none'),
                        None
                    )
                    if matching_format:
                        key = f'Url{resolution}'
                        download_options[key] = matching_format['url']
                
                # Add audio format
                audio_format = next(
                    (f for f in formats if f.get('acodec') != 'none' and f.get('vcodec') == 'none'),
                    None
                )
                if audio_format:
                    download_options['Audio'] = audio_format['url']

                # Save to model
                instance = serializer.save(
                    title=info.get('title'),
                    download_options=download_options,
                    status='completed'
                )

                return Response(
                    self.get_serializer(instance).data,
                    status=status.HTTP_201_CREATED
                )

        except Exception as e:
            # Save error state
            instance = serializer.save(
                status='failed',
                error_message=str(e)
            )
            return Response(
                self.get_serializer(instance).data,
                status=status.HTTP_400_BAD_REQUEST
            )



# ------------------------ ImagesToPDFView ------------------------
class ImagesToPDFView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ImagesToPDFSerializer

    def post(self, request, *args, **kwargs):
        images = request.FILES.getlist('images')
        if not images:
            return Response(
                {'error': 'Please provide at least one image'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create a new conversion instance
        conversion = ImagesToPDFModel.objects.create()
        
        try:
            # Save images temporarily and store their paths
            image_paths = []
            stored_images = []
            for image in images:
                # Generate a unique filename
                ext = os.path.splitext(image.name)[1].lower()
                filename = f'{uuid.uuid4()}{ext}'
                temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', filename)
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                
                # Save the image
                with open(temp_path, 'wb+') as destination:
                    for chunk in image.chunks():
                        destination.write(chunk)
                image_paths.append(temp_path)
                
                # Store image information
                stored_images.append({
                    'name': image.name,
                    'size': image.size,
                    'type': image.content_type,
                    'path': temp_path
                })

            # Update status and store image information
            conversion.status = 'processing'
            conversion.images = stored_images
            conversion.save()

            # Create PDF from images
            output_filename = f'converted_{uuid.uuid4()}.pdf'
            output_path = os.path.join(settings.MEDIA_ROOT, 'converted_pdfs', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Use PIL to convert images to PDF
            images_to_convert = [Image.open(path) for path in image_paths]
            first_image = images_to_convert[0]
            images_to_convert = images_to_convert[1:]

            first_image.save(
                output_path,
                'PDF',
                resolution=100.0,
                save_all=True,
                append_images=images_to_convert
            )

            # Clean up temporary files
            for path in image_paths:
                try:
                    os.remove(path)
                except Exception:
                    pass

            # Update conversion instance
            with open(output_path, 'rb') as pdf_file:
                conversion.converted_pdf.save(output_filename, File(pdf_file))
            conversion.status = 'completed'
            conversion.save()

            # Return the download URL
            serializer = self.serializer_class(
                conversion, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            conversion.status = 'failed'
            conversion.error_message = str(e)
            conversion.save()
            return Response(
                {'error': 'Failed to convert images to PDF', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ------------------------ PdfToImagesView ------------------------
class PDFToImagesView(generics.ListCreateAPIView):
    queryset = PdfToImagesModel.objects.all()
    serializer_class = PdfToImagesSerializer
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            instance = serializer.save()
            
            try:
                # Open PDF document
                pdf_document = fitz.open(instance.document.path)
                instance.page_count = len(pdf_document)
                instance.status = 'processing'
                instance.save()

                converted_images = []
                
                # Create directory for converted images
                output_dir = os.path.join('media', 'converted_images', timezone.now().strftime('%Y/%m/%d'))
                os.makedirs(output_dir, exist_ok=True)

                # Convert each page to image
                for page_num in range(len(pdf_document)):
                    page = pdf_document[page_num]
                    pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # 300 DPI
                    
                    # Generate unique filename
                    image_filename = f"page_{page_num + 1}_{uuid.uuid4().hex[:6]}.png"
                    image_path = os.path.join(output_dir, image_filename)
                    
                    # Save image
                    pix.save(image_path)
                    
                    # Store image information
                    converted_images.append({
                        'page': page_num + 1,
                        'path': image_path,
                        # add host before /media/converted_images/{timezone.now().strftime('%Y/%m/%d')}/{image_filename}
                        'url': f"{request.build_absolute_uri('/')}media/converted_images/{timezone.now().strftime('%Y/%m/%d')}/{image_filename}"
                    })

                # Update instance with converted images data
                instance.converted_images = converted_images
                instance.status = 'completed'
                instance.save()

                # Return response with image URLs
                return Response({
                    'id': instance.id,
                    'status': 'completed',
                    'page_count': instance.page_count,
                    'images': [img['url'] for img in converted_images]
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                logger.error(f"Error converting PDF: {str(e)}")
                instance.status = 'failed'
                instance.error_message = str(e)
                instance.save()
                raise FileProcessingError(f"Error converting PDF: {str(e)}")

        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
            return Response({"message": "PDF and converted images deleted successfully"}, 
                          status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



# ------------------------ RetriveDestroyPdfToImagesView ------------------------
class RetriveDestroyPdfToImagesView(generics.RetrieveDestroyAPIView):
    queryset = PdfToImagesModel.objects.all()
    serializer_class = PdfToImagesSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        deleted_files = []

        if instance.document:
            pdf_name = os.path.basename(instance.document.name)
            deleted_files.append(instance.document.path)
            instance.document.delete(save=False)

            img_folder_path = instance.document.storage.path(
                os.path.join("converted_images", f"{pdf_name[:-4]}_images")
            )
            try:
                if os.path.isdir(img_folder_path):
                    shutil.rmtree(img_folder_path)
                    deleted_files.append(img_folder_path)
                    print(f"Deleted folder: {img_folder_path}")
                else:
                    print(f"Folder not found: {img_folder_path}")
            except Exception as e:
                print(f"Error deleting folder {img_folder_path}: {e}")

        instance.delete()

        return Response({
            "message": "Record and associated files deleted successfully.",
            "deleted_files": deleted_files
        }, status=status.HTTP_204_NO_CONTENT)


# ------------------------ WordManager ------------------------
class WordManager(APIView):
    def post(self, request, *args, **kwargs):
        purpose = request.query_params.get('purpose')
        if purpose == 'wordcount':
            words = request.query_params.get('words')
            words_count = len(words.split())
            return Response({'wordCount': words_count})
        if purpose == 'lowertouppercase':
            words = request.query_params.get('words')
            upperCaseWords = words.upper()
            return Response({'UpperCase': upperCaseWords})
        if purpose == 'spellingcheck':
            spell = SpellChecker()
            words = request.query_params.get('words').split()
            wordlist = words
            misspelled = spell.unknown(wordlist)
            misspelledWithIndex = []
            corrected = []
            candidates = []
            correctedString = []
            for word in misspelled:
                misspelledWithIndex.append(wordlist.index(word))
                misspelledWithIndex.append(word)
                corrected.append(wordlist.index(word))
                corrected.append(spell.correction(word))
                candidates.append(wordlist.index(word))
                candidates.append(word)
                candidates.append(spell.candidates(word))
            index = -1
            for word in wordlist:
                index = index + 1
                for misspell in misspelled:
                    index = index + 1
                    if word == misspell:
                        correctedString.append(corrected[index])
                    else:
                        correctedString.append(word)
            if correctedString:
                # Note: Adjust join logic as needed
                correctedString = " ".join(correctedString)
            return Response({
                'Missplled': misspelledWithIndex,
                'Most Likely Words': corrected,
                'Candidates Words': candidates,
                'corrected string': correctedString
            })


# ------------------------ WordtoPDF ------------------------
class WordtoPDFView(generics.CreateAPIView):
    serializer_class = WordToPDFSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            pythoncom.CoInitialize()
            instance = serializer.save()
            instance.status = 'processing'
            instance.save()

            # Convert Word to PDF using python-docx-to-pdf
            word_path = instance.document.path
            pdf_path = word_path.rsplit('.', 1)[0] + '.pdf'

            try:
                from docx2pdf import convert
                convert(word_path, pdf_path)

                with open(pdf_path, 'rb') as pdf_file:
                    instance.converted_pdf.save(
                        os.path.basename(pdf_path),
                        ContentFile(pdf_file.read()),
                        save=False
                    )
                instance.status = 'completed'
                instance.save()

                # Return serialized data instead of file
                serializer = self.get_serializer(instance, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)

            except Exception as e:
                instance.status = 'failed'
                instance.error_message = str(e)
                instance.save()
                raise

            finally:
                # Cleanup temporary PDF file
                if os.path.exists(pdf_path):
                    os.remove(pdf_path)
                    pythoncom.CoUninitialize()

        except Exception as e:
            return Response(
                {'error': 'Failed to convert Word to PDF', 'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    

# ------------------------ PlaylistDownloader ------------------------
class PlaylistDownloader(APIView):
    def post(self, request, *args, **kwargs):
        data = {}
        link = request.query_params.get('playlist_link')
        i = 0
        if link != "":
            p = Playlist(link)
            for video in p.videos:
                Url1080p = video.streams.filter(
                    resolution='1080p', file_extension='mp4').first().url
                data[f'videoNO_{i}_Url1080p'] = Url1080p
                Url720p = video.streams.filter(
                    resolution='720p', file_extension='mp4').first().url
                data[f'videoNO_{i}_Url720p'] = Url720p
                Url480p = video.streams.filter(
                    resolution='480p', file_extension='mp4').first().url
                data[f'videoNO_{i}_Url480p'] = Url480p
                Url360p = video.streams.filter(
                    resolution='360p', file_extension='mp4').first().url
                data[f'videoNO_{i}_Url360p'] = Url360p
                Url240p = video.streams.filter(
                    resolution='240p', file_extension='mp4').first().url
                data[f'videoNO_{i}_Url240p'] = Url240p
                Url144p = video.streams.filter(
                    resolution='144p', file_extension='mp4').first().url
                data[f'videoNO_{i}_Url144p'] = Url144p
                audio = video.streams.filter(
                    only_audio=True).desc().first().url
                data[f'videoNO_{i}_Audio'] = audio
                i = i + 1
        return Response(data)


# ------------------------ VideoDownloader ------------------------
class VideoDownloader(APIView):
    """Handle YouTube video download operations.
    
    Provides URLs for different video resolutions and audio formats.
    Includes proper error handling and input validation.
    """
    SUPPORTED_RESOLUTIONS = ['1080p', '720p', '480p', '360p', '240p', '144p']

    def validate_youtube_url(self, url):
        """Validate YouTube URL format."""
        if not url:
            raise InvalidFileError("YouTube URL is required.")
        if 'youtube.com' not in url and 'youtu.be' not in url:
            raise InvalidFileError("Invalid YouTube URL format.")

    def get_video_streams(self, yt, resolution):
        """Get video stream for specific resolution with error handling."""
        try:
            stream = yt.streams.filter(
                resolution=resolution,
                file_extension='mp4'
            ).first()
            return stream.url if stream else None
        except Exception as e:
            logger.warning(f"Could not get {resolution} stream: {str(e)}")
            return None

    def post(self, request, *args, **kwargs):
        try:
            link = request.query_params.get('video_link')
            self.validate_youtube_url(link)

            try:
                yt = YouTube(link)
                data = {}

                # Get video streams for all resolutions
                for resolution in self.SUPPORTED_RESOLUTIONS:
                    url = self.get_video_streams(yt, resolution)
                    if url:
                        data[f'Url{resolution}'] = url

                # Get audio stream
                try:
                    audio_stream = yt.streams.filter(only_audio=True).desc().first()
                    if audio_stream:
                        data['Audio'] = audio_stream.url
                except Exception as e:
                    logger.error(f"Error getting audio stream: {str(e)}")

                if not data:
                    raise FileProcessingError("No available streams found for this video.")

                logger.info(f"Successfully retrieved streams for video: {link}")
                return Response(data, status=status.HTTP_200_OK)

            except Exception as e:
                logger.error(f"Error processing YouTube video: {str(e)}")
                raise FileProcessingError(f"Error processing YouTube video: {str(e)}")

        except Exception as e:
            logger.error(f"Error in video download: {str(e)}")
            return Response(
                {"error": str(e)},
                status=getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )


# ------------------------ AudioDownloader ------------------------
class AudioDownloader(APIView):
    """Handle YouTube audio download operations.
    
    Provides URL for the highest quality audio stream.
    Includes proper error handling and input validation.
    """
    def validate_youtube_url(self, url):
        """Validate YouTube URL format."""
        if not url:
            raise InvalidFileError("YouTube URL is required.")
        if 'youtube.com' not in url and 'youtu.be' not in url:
            raise InvalidFileError("Invalid YouTube URL format.")

    def post(self, request, *args, **kwargs):
        try:
            link = request.query_params.get('video_link')
            self.validate_youtube_url(link)

            try:
                yt = YouTube(link)
                audio_stream = yt.streams.filter(only_audio=True).desc().first()

                if not audio_stream:
                    raise FileProcessingError("No audio stream available for this video.")

                logger.info(f"Successfully retrieved audio stream for video: {link}")
                return Response(
                    {"Audio": audio_stream.url},
                    status=status.HTTP_200_OK
                )

            except Exception as e:
                logger.error(f"Error processing YouTube video: {str(e)}")
                raise FileProcessingError(f"Error processing YouTube video: {str(e)}")

        except Exception as e:
            logger.error(f"Error in audio download: {str(e)}")
            return Response(
                {"error": str(e)},
                status=getattr(e, 'status_code', status.HTTP_500_INTERNAL_SERVER_ERROR)
            )
