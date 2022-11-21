from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from docx2pdf import convert
from pathlib import Path
from rest_framework import status
from .serializers import WordToPDFSerializer
from .models import WordToPDFModel
from rest_framework import generics
import sys
import os
import comtypes.client
from django.core.files.storage import FileSystemStorage
# Create your views here.
def stem(name):
        """The final path component, minus its last suffix."""
        i = name.rfind('.')
        if 0 < i < len(name) - 1:
            return name[:i]
        else:
            return name

@api_view(['GET', 'POST'])
def png(request):
    if request.method=="POST":
        # file=request.data['file']
        # print(dir(file))
        # pdf=convert(file)
        myfile = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        # fs.delete(filename) 
        basePath=Path(__file__).resolve().parent.parent
        FilePath=f"{basePath}/uploads/"
        convert(f"{FilePath}{filename}")
        pdfname=f"{stem(filename)}.pdf"
        pdfpath=f"{FilePath}{stem(filename)}.pdf"
        with open(pdfpath) as pdf:
            pdf.close()
        fs.delete(filename)
        fs.delete(pdfname)
        
        # fs.delete(filename)
        # word = win32com.client.Dispatch("Word.Application")
        # wdFormatPDF = 17
        # f = file.file
        # pdf=f.SaveAs(str(file), FileFormat=wdFormatPDF)
        # print(pdf)
        # converted_file=convert(file)
        # print(converted_file)
        return HttpResponse(pdf,content_type='application/pdf')
    return Response({"message": "Hello, world!"})

class WordtoPDF(generics.ListCreateAPIView,generics.RetrieveAPIView):
    queryset=WordToPDFModel.objects.all()
    serializer_class=WordToPDFSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # getting the file name without extension
        # i = name.rfind('.')
        # if 0 < i < len(name) - 1:
        #     name= name[:i]
        # else:
        #     name=name
        # print(name)
        # wdFormatPDF = 17
        # word = comtypes.client.CreateObject('Word.Application')
        # doc = word.Documents.Open(serializer.validated_data['file'].name)
        # doc.SaveAs(f"{name}.pdf", FileFormat=wdFormatPDF)
        # doc.Close()
        # word.Quit()
        serializer.save()
        name=serializer.data['file']
        i = name.find('media/')+6
        if 0 < i < len(name) + 1:
            name= name[i:]
        else:
            name=name
        basePath=Path(__file__).resolve().parent.parent
        path=f"{basePath}\media\\"
        convert(f'{path}{name}')
        i = name.rfind('.')
        if 0 < i < len(name) - 1:
            name= name[:i]
        else:
            name=name
        pdfName=f'{name}.pdf'
        wordfilequery = WordToPDFModel.objects.get(id=serializer.data['id'])
        wordfilequery.pdfFile= f"http://127.0.0.1:8000/media/{pdfName}"
        wordfilequery.save()
        serializer = self.get_serializer(wordfilequery)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        