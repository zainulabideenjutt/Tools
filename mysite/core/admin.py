from django.contrib import admin
from . models import ConverterModel,ImageConverterModel
# Register your models here.
admin.site.register(ConverterModel)
admin.site.register(ImageConverterModel)