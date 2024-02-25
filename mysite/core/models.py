from django.db import models

# Create your models here.
class ConverterModel(models.Model):
    file=models.FileField()
    ConvertedFile=models.TextField(null=True,blank=True,default="")
    
class ImageConverterModel(models.Model):
    # image=models.ImageField()
    convertedFromExtension=models.TextField(null=True,blank=True,default='')
    convertedImage=models.TextField(null=True,blank=True,default="")
class PdfToImageModel(models.Model):
    folderName=models.TextField(null=True,blank=True,default="")
    Image=models.TextField(null=True,blank=True,default="")

class ImagesToPdf(models.Model):
    pdfName=models.TextField(null=True,blank=True,default="")


    
