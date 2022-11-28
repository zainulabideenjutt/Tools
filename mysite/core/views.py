from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from docx2pdf import convert
# from pdf2docx import Converter
# from pdf2docx import parse
from pathlib import Path
from rest_framework import status
from .serializers import ConverterSerializer,ImageConverterSerializer
from .models import ConverterModel,ImageConverterModel
from rest_framework import generics
import os
from PIL import Image
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404
# Create your views here.
class BmpToJpgDelete(APIView):
    def delete(self, request, *args, **kwargs):
        if (type(kwargs['pk'])==type(1)):
            id=kwargs['pk']
            instance=get_object_or_404(ImageConverterModel, pk=id)
            if instance:
                imagePathFromDomain=instance.convertedImage
                domain=request.get_host()
                storagePathFromDomain=f"http://{domain}/media/"
                ImageName=imagePathFromDomain.removeprefix(storagePathFromDomain)
                basePath=Path(__file__).resolve().parent.parent
                path=f"{basePath}\media\\"
                instance.delete()
                os.remove(f'{path}{ImageName}')
                return Response({'detail':'deleted '})
            return Response({'detail':"instance doesnot exist"})
        return Response({"detail":"Please Provide the Id of object you want to delete"})
class BmpToJpg(generics.ListCreateAPIView):
    queryset=ImageConverterModel.objects.all()
    serializer_class=ImageConverterSerializer
    def post(self,request,*args,**kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        filePathFromDomain=serializer.data['image']
        print(filePathFromDomain)
        domain=request.get_host()
        storagePathFromDomain=f"http://{domain}/media/"
        Filename=filePathFromDomain.removeprefix(storagePathFromDomain)
        basePath=Path(__file__).resolve().parent.parent
        path=f"{basePath}\media\\"
        jpgImageName=Filename.replace('.bmp',".jpg")
        image=Image.open(f'{path}{Filename}')
        image.save(f"{path}{jpgImageName}",'JPEG')
        imagequery = ImageConverterModel.objects.get(id=serializer.data['id'])
        imagequery.convertedImage= f"{storagePathFromDomain}{jpgImageName}"
        imagequery.save()
        serializer = self.get_serializer(imagequery)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

class WordtoPDF(generics.ListCreateAPIView):
    queryset=ConverterModel.objects.all()
    serializer_class=ConverterSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        filePathFromDomain=serializer.data['file']
        domain=request.get_host()
        storagePathFromDomain=f"http://{domain}/media/"
        Filename=filePathFromDomain.removeprefix(storagePathFromDomain)
        basePath=Path(__file__).resolve().parent.parent
        path=f"{basePath}\media\\"
        convert(f'{path}{Filename}')
        pdfName=Filename.replace('.docx',".pdf")
        wordfilequery = ConverterModel.objects.get(id=serializer.data['id'])
        wordfilequery.pdfFile= f"{storagePathFromDomain}{pdfName}"
        wordfilequery.save()
        serializer = self.get_serializer(wordfilequery)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
# class PDFToWord(generics.ListCreateAPIView):
#     queryset= ConverterModel.objects.all()
#     serializer_class=ConverterSerializer
#     def post(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         filePathFromDomain=serializer.data['file']
#         domain=request.get_host()
#         storagePathFromDomain=f"http://{domain}/media/"
#         Filename=filePathFromDomain.removeprefix(storagePathFromDomain)
#         basePath=Path(__file__).resolve().parent.parent
#         path=f"{basePath}\media\\"
#         cv = Converter(f'{path}{Filename}')
#         pdfName=Filename.replace(".pdf",'.docx')
#         cv.convert(f'{path}{pdfName}',multi_processing=True,cpu_count=4,start=0,end=None)
#         cv.close()
#         wordfilequery =ConverterModel.objects.get(id=serializer.data['id'])
#         wordfilequery.pdfFile=f"{storagePathFromDomain}{pdfName}"
#         wordfilequery.save()
#         serializer =self.get_serializer(wordfilequery)
#         headers =self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
class WordToPDFDelete(APIView):
    def delete(self, request, *args, **kwargs):
        if (type(kwargs['pk'])==type(1)):
            id=kwargs['pk']
            instance=get_object_or_404(ConverterModel, pk=id)
            if instance:
                pdfName = f"{instance.file.name.removesuffix('.docx')}.pdf"
                basePath=Path(__file__).resolve().parent.parent
                path=f"{basePath}\media\\"
                instance.delete()
                os.remove(f'{path}{pdfName}')
                return Response({'detail':'deleted '})
            return Response({'detail':"instance doesnot exist"})
        return Response({"detail":"Please Provide the Id of object you want to delete"})
        
    
