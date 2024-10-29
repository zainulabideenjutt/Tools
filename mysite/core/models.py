from django.db import models

# Create your models here.
class ConverterModel(models.Model):
    file=models.FileField()
    ConvertedFile=models.TextField(null=True,blank=True,default="")
    
class ImageConverterModel(models.Model):
    original_image = models.ImageField(upload_to='original_images/', blank=True, null=True)
    converted_image = models.ImageField(upload_to='converted_images/', blank=True, null=True)

class PdfToImagesModel(models.Model):
    document = models.FileField(upload_to='documents/', blank=True, null=True)  # Accepts PDF
    converted_images = models.JSONField(blank=True, null=True)  # Stores URLs of converted images

class ImagesToPdf(models.Model):
    pdfName=models.TextField(null=True,blank=True,default="")


    
