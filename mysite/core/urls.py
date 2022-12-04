from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns =[
    path("youtubeplaylistdownloader",views.PlaylistDownloader.as_view()),
    path("youtubedownloader",views.VideoDownloader.as_view()),
    path("images-to-pdf",views.ImagesToPdf.as_view()),
    path("pdftoimage",views.PdfToImage.as_view()),
    path("wordmanager",views.WordManager.as_view()),
    path("image-converter",views.ImageConverter.as_view()),
    path("<int:pk>/bmptojpg",views.ImageConverter.as_view()),
    path("wordtopdf",views.WordtoPDF.as_view()),
    path("<int:pk>/wordtopdf",views.WordtoPDF.as_view()),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)