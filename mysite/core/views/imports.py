import webp
from rest_framework.decorators import api_view
from PIL import ImageFilter
import shutil
from pytube import YouTube
from pytube import Playlist
from spellchecker import SpellChecker
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from docx2pdf import convert
import datetime
import uuid
import os
from pdf2image import convert_from_path
from django.core.files.storage import default_storage
# from pdf2docx import Converter
# from pdf2docx import parse
from pathlib import Path
from rest_framework import status
from ..serializers import ConverterSerializer,ImageConverterSerializer,PdfToImageSerializer,PdfToOnlyImageSerializer,ImagesToPdfSerializer
from ..models import ConverterModel,ImageConverterModel,PdfToImageModel,ImagesToPdf as ImagestoPdfModel
from rest_framework import generics
from PIL import Image
from django.shortcuts import get_object_or_404