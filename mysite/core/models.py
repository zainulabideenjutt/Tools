from django.db import models

# Create your models here.
class ConverterModel(models.Model):
    file=models.FileField()
    ConvertedFile=models.TextField(null=True,blank=True,default="")
    
class ImageConverterModel(models.Model):
    original_image = models.ImageField(upload_to='original_images/', blank=True, null=True)
    converted_image = models.ImageField(upload_to='converted_images/', blank=True, null=True)
    
class PdfToImageModel(models.Model):
    folderName=models.TextField(null=True,blank=True,default="")
    Image=models.TextField(null=True,blank=True,default="")

class ImagesToPdf(models.Model):
    pdfName=models.TextField(null=True,blank=True,default="")


    
