from django.urls import path
from .views import ImagesToPDFView,RetriveDestroyPdfToImagesView,PDFToImagesView,WordManager,ImageConverter,RetrieveDestroyImage,WordtoPDFView,YouTubeDownloaderView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns =[
    # path("youtubeplaylistdownloader",PlaylistDownloader.as_view()),
    # path("youtubedownloader",VideoDownloader.as_view()),
    path("youtubedownloader",YouTubeDownloaderView.as_view()),
    path("images-to-pdf-converter",ImagesToPDFView.as_view()),
    path("<int:pk>/images-to-pdf-converter",ImagesToPDFView.as_view()),
    path("pdf-to-images-converter/<int:pk>",RetriveDestroyPdfToImagesView.as_view()),
    path("pdf-to-images-converter",PDFToImagesView.as_view()),
    path("word-manager",WordManager.as_view()),
    path("image-converter",ImageConverter.as_view()),
    path("image-converter/<int:pk>",RetrieveDestroyImage.as_view()),
    path("word-to-pdf",WordtoPDFView.as_view()),
    # path("<int:pk>/word-to-pdf",WordtoPDF.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) 