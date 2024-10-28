from django.urls import path
from .views.YoutubeVideoDownloader import VideoDownloader
from .views.YoutubePLayListDownloader import PlaylistDownloader
from .views.ImagesToPdfConverter import ImagesToPdf
from .views.PdfToImagesConverter import PdfToImage
from .views.WordsManager import WordManager
from .views.ImageConverter import ImageConverter,RetriveSingleImage
from .views.WordToPdf import WordtoPDF
from django.conf import settings
from django.conf.urls.static import static
urlpatterns =[
    path("youtubeplaylistdownloader",PlaylistDownloader.as_view()),
    path("youtubedownloader",VideoDownloader.as_view()),
    path("images-to-pdf-converter",ImagesToPdf.as_view()),
    path("<int:pk>/images-to-pdf-converter",ImagesToPdf.as_view()),
    path("<int:pk>/pdf-to-images-converter",PdfToImage.as_view()),
    path("pdf-to-images-converter",PdfToImage.as_view()),
    path("word-manager",WordManager.as_view()),
    path("image-converter",ImageConverter.as_view()),
    path("image-converter/<int:pk>",RetriveSingleImage.as_view()),
    path("word-to-pdf",WordtoPDF.as_view()),
    path("<int:pk>/word-to-pdf",WordtoPDF.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)