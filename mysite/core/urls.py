from django.urls import path
from .views import png
from django.conf import settings
from django.conf.urls.static import static
urlpatterns =[
    path("",png)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)