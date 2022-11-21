from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework import status
from docx2pdf import convert
import aspose.words as aw
import win32com.client
from pathlib import Path
import os
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