from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns =[
    # path("",views.png),
    # path("pdftoword",views.PDFToWord.as_view()),
    
    path("bmptojpg",views.BmpToJpg.as_view()),
    path("wordtopdf",views.WordtoPDF.as_view()),
    path("<int:pk>/wordtopdfdelete",views.WordToPDFDelete.as_view()),
    path("<int:pk>/bmptojpgdelete",views.BmpToJpgDelete.as_view())
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)