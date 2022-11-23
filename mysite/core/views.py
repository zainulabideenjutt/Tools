from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from docx2pdf import convert
from pathlib import Path
from rest_framework import status
from .serializers import WordToPDFSerializer
from .models import WordToPDFModel
from rest_framework import generics
from django.conf import settings
import sys
import os
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.core.files.temp import NamedTemporaryFile
from django.core import files
from django.shortcuts import get_object_or_404
# Create your views here.
# def stem(name):
#         """The final path component, minus its last suffix."""
#         i = name.rfind('.')
#         if 0 < i < len(name) - 1:
#             return name[:i]
#         else:
#             return name

# @api_view(['GET', 'POST'])
# def png(request):
#     if request.method=="POST":
#         # file=request.data['file']
#         # print(dir(file))
#         # pdf=convert(file)
#         myfile = request.FILES['file']
#         fs = FileSystemStorage()
#         filename = fs.save(myfile.name, myfile)
#         # fs.delete(filename) 
#         basePath=Path(__file__).resolve().parent.parent
#         FilePath=f"{basePath}/uploads/"
#         convert(f"{FilePath}{filename}")
#         pdfname=f"{stem(filename)}.pdf"
#         pdfpath=f"{FilePath}{stem(filename)}.pdf"
#         with open(pdfpath) as pdf:
#             pdf.close()
#         fs.delete(filename)
#         fs.delete(pdfname)
        
        # fs.delete(filename)
        # word = win32com.client.Dispatch("Word.Application")
        # wdFormatPDF = 17
        # f = file.file
        # pdf=f.SaveAs(str(file), FileFormat=wdFormatPDF)
        # print(pdf)
        # converted_file=convert(file)
        # print(converted_file)
    #     return HttpResponse(pdf,content_type='application/pdf')
    # return Response({"message": "Hello, world!"})

class WordtoPDF(generics.ListCreateAPIView):
    queryset=WordToPDFModel.objects.all()
    serializer_class=WordToPDFSerializer
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
        wordfilequery = WordToPDFModel.objects.get(id=serializer.data['id'])
        wordfilequery.pdfFile= f"{storagePathFromDomain}{pdfName}"
        wordfilequery.save()
        serializer = self.get_serializer(wordfilequery)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
class WordToPDFDelete(APIView):
    def delete(self, request, *args, **kwargs):
        if (type(kwargs['pk'])==type(1)):
            id=kwargs['pk']
            instance=get_object_or_404(WordToPDFModel, pk=id)
            if instance:
                pdfName = f"{instance.file.name.removesuffix('.docx')}.pdf"
                basePath=Path(__file__).resolve().parent.parent
                path=f"{basePath}\media\\"
                instance.delete()
                os.remove(f'{path}{pdfName}')
                return Response({'detail':'deleted '})
            return Response({'detail':"instance doesnot exist"})
        return Response({"detail":"Please Provide the Id of object you want to delete"})
        
    

# class WordtoPDF(APIView):
#     def post(self, request, *args, **kwargs):

#         word_temp_file = NamedTemporaryFile()
#         in_memory_word_file =request.data['file'].read()
#         word_temp_file.write(in_memory_word_file)
#         # for block in in_memory_image.iter_content():
#         #     # If no more file then stop
#         #     if not block:
#         #         break
#         #     # Write image block to temporary file
#         #     image_temp_file.write(block)
#         # word_temp_file.flush()
#         temp_file = files.File(word_temp_file,name=f"{request.data['file'].name}")
#         print(dir(temp_file))
#         print(temp_file.name)
#         path=default_storage.save("media.docx", temp_file)
#         print(path)
#         # word = win32com.client.Dispatch("Word.Application")
#         # wdFormatPDF = 17
#         # convert(f"E:\small tools\mysite\media\{temp_file}")
#         # doc = word.Documents.Open(str(docx_filepath))
#         # path = doc.save('asad.pdf ',FileFormat=wdFormatPDF)
#         # convert(f"E:\small tools\mysite\media\{path}.docx")
#         # doc = word.Document.Open(path)
#         # doc.SaveAs(str(f"asad.pdf"), FileFormat=wdFormatPDF)
#         return Response({"hello":"world This is Post Method"})
#     def get(self, request, *args, **kwargs):
#         return Response({"hello":"world This is Get Method"})