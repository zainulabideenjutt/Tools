import webp
from rest_framework.decorators import api_view
from PIL import ImageFilter
import shutil
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from docx2pdf import convert
import datetime
import uuid
import string
import random
import io
import os
from pdf2image import convert_from_path
from django.core.files.storage import default_storage
# from pdf2docx import Converter
# from pdf2docx import parse
from pathlib import Path
from rest_framework import status
from .serializers import ConverterSerializer,ImageConverterSerializer,PdfToImageSerializer,PdfToOnlyImageSerializer
from .models import ConverterModel,ImageConverterModel,PdfToImageModel
from rest_framework import generics
from PIL import Image
from django.shortcuts import get_object_or_404
# Create your views here.
class PdfToImage(generics.ListCreateAPIView,generics.DestroyAPIView):
    queryset=PdfToImageModel.objects.all()
    serializer_class=PdfToImageSerializer
    def generate_random_string(self,string_length=6):
        """Returns a random string of length string_length."""
        random = str(uuid.uuid4()) # Convert UUID format to a Python string.
        random = random.upper() # Make all characters uppercase.
        random = random.replace("-","") # Remove the UUID '-'.
        return random[0:string_length] # Return the random string.
    def return_response(self,**data):
            serializer = self.get_serializer(data=data['data'])
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def post(self,request,*args,**krargs):
        imageName=request.data['image'].name
        inComingImageFile=request.data['image']
        InComingFileExtension=imageName[imageName.rindex('.'):]
        convertToFileExtension=request.data['convert_to']
        randomString=f"{datetime.datetime.now().date()}_{str(datetime.datetime.now().time()).replace('.','').replace(':','')}"
        basePath=Path(__file__).resolve().parent.parent
        imagePath=f"{basePath}\media\\"
        if convertToFileExtension=='.jpg' and InComingFileExtension=='.pdf':
            randomDirectoryName=f"{self.generate_random_string()}_{randomString}"
            os.mkdir(f'{imagePath}{randomDirectoryName}')
            pdfName=default_storage.save(f"{randomDirectoryName}\{imageName}",inComingImageFile)
            print(randomDirectoryName)
            images = convert_from_path(f"{imagePath}{pdfName}")
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data= {
            "folderName": randomDirectoryName,
            "Image": ""
            }
            if len(images)<=5:
                for i in range(len(images)):
                    # for multiple images
                        randomImageName=f"image_{randomString}_{self.generate_random_string()}"
                        images[i].save(f'{imagePath}{randomDirectoryName}\{randomImageName}.jpg', 'JPEG')
                        data["Image"]=f"{storagePathFromDomain}{randomDirectoryName}/{randomImageName}.jpg"
                        serializer = self.get_serializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
            else:
                for i in range(5):
                    # for multiple images
                        randomImageName=f"image_{randomString}_{self.generate_random_string()}"
                        images[i].save(f'{imagePath}{randomDirectoryName}\{randomImageName}.jpg', 'JPEG')
                        data["Image"]=f"{storagePathFromDomain}{randomDirectoryName}/{randomImageName}.jpg"
                        serializer = self.get_serializer(data=data)
                        serializer.is_valid(raise_exception=True)
                        serializer.save()
                qs=PdfToImageModel.objects.filter(folderName=randomDirectoryName)
                serializer = PdfToOnlyImageSerializer(qs,many=True)
                headers = self.get_success_headers(serializer.data)
                serializer.data.append({'message':"You cannot convert more than 5 pages"})
                return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
            qs=PdfToImageModel.objects.filter(folderName=randomDirectoryName)
            serializer = PdfToOnlyImageSerializer(qs,many=True)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def delete(self,request,*args,**kwargs):
            if kwargs:
                id=kwargs['pk']
                if (type(id)==type(1)):
                    instance=get_object_or_404(PdfToImageModel, pk=id)
                    if instance:
                        FolderName=instance.folderName
                        basePath=Path(__file__).resolve().parent.parent
                        path=f"{basePath}\media\\"
                        instance.delete()
                        try:
                            shutil.rmtree(path+FolderName)
                        except FileNotFoundError:
                            return Response({'detail':f"{FolderName} is not Available in Your Files"},status=status.HTTP_404_NOT_FOUND)
                        return Response({'detail':'Image and Instance Has been Deleted'},status=status.HTTP_204_NO_CONTENT)
                return Response({'detail':"instance doesnot exist"})
            if not kwargs:
                qs=PdfToImageModel.objects.all()
                if qs:
                    for instance in qs :
                        FolderName=instance.folderName
                        basePath=Path(__file__).resolve().parent.parent
                        path=f"{basePath}\media\\"
                        instance.delete()
                        try:
                            shutil.rmtree(path+FolderName)
                        except FileNotFoundError:
                            continue
                            
                    return Response({'detail':'All instanses deleted'})
                else:
                    return Response({'detail':'all instances are already deleted'})
            return Response({"detail":"Something Went Wrong...."})
                
            
class WordManager(APIView):
    def post(self,request,*args,**kwargs):
        if request.data['purpose']=='wordcount':
            words=request.data['words']
            print(request.data)
            words_count=len(words.split())
            return Response({'wordCount':words_count})
        if request.data['purpose']=='lowertouppercase':
            words=request.data['words']
            upperCaseWords=words.upper()
            return Response({'UpperCase':upperCaseWords})
class ImageConverter(generics.ListCreateAPIView,generics.RetrieveAPIView):
    queryset=ImageConverterModel.objects.all()
    serializer_class=ImageConverterSerializer
    def generate_random_string(self,string_length=6):
        """Returns a random string of length string_length."""
        random = str(uuid.uuid4()) # Convert UUID format to a Python string.
        random = random.upper() # Make all characters uppercase.
        random = random.replace("-","") # Remove the UUID '-'.
        return random[0:string_length] # Return the random string.
    def return_response(self,**data):
            serializer = self.get_serializer(data=data['data'])
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    def post(self,request,*args,**kwargs):
        imageName=request.data['image'].name
        inComingImageFile=request.data['image']
        InComingFileExtension=imageName[imageName.rindex('.'):]
        if InComingFileExtension!='.pdf':
            image=Image.open(inComingImageFile)
        convertToFileExtension=request.data['convert_to']
        randomString=f"{datetime.datetime.now().date()}_{str(datetime.datetime.now().time()).replace('.','').replace(':','')}"
        basePath=Path(__file__).resolve().parent.parent
        imagePath=f"{basePath}\media\\"
        if convertToFileExtension=='resize' :
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            RGBImage=image.resize((300,300))
            RGBImage.save(f"{imagePath}{randomImageName}{InComingFileExtension}")
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{InComingFileExtension}',  
                }
            return self.return_response(data=data)
        if convertToFileExtension=='crop' :
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            # RGBImage=image.convert('RGB')
            width, height = image.size
            x_axis = 1645
            y_axis = 672
            xPlusWidth = 2605+x_axis
            yPlusHeight = 1325+y_axis
            if x_axis < width and y_axis<height and  xPlusWidth>width-x_axis and yPlusHeight>height-y_axis :
                RGBImage=image.crop((x_axis,y_axis,xPlusWidth,yPlusHeight))
                RGBImage.save(f"{imagePath}{randomImageName}{InComingFileExtension}")
                domain=request.get_host()
                storagePathFromDomain=f"http://{domain}/media/"
                data={'convertedFromExtension':InComingFileExtension,
                    'convertedImage':f'{storagePathFromDomain}{randomImageName}{InComingFileExtension}',  
                    }
                return self.return_response(data=data)
            else:
                return Response({'detail':'something went wrong with coordinates'})
        if convertToFileExtension=='.png' and InComingFileExtension=='.gif':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            RGBImage=image.convert('RGB')
            RGBImage.save(f"{imagePath}{randomImageName}{convertToFileExtension}",format='png')
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
        if convertToFileExtension=='.png' and InComingFileExtension=='.jpg':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            RGBImage=image.convert('RGB')
            RGBImage.save(f"{imagePath}{randomImageName}{convertToFileExtension}",format='png')
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
        if convertToFileExtension=='.gif' and InComingFileExtension=='.webp':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            image.save(f"{imagePath}{randomImageName}{InComingFileExtension}")
            image=webp.load_images(f"{imagePath}{randomImageName}{InComingFileExtension}")
            im1 = image[0].filter(ImageFilter.DETAIL)
            im1=im1.filter(ImageFilter.MinFilter(1))
            im1.save(f"{imagePath}{randomImageName}{convertToFileExtension}", 'gif', 
                            save_all=True,lossless=True,append_images=image[0:],
                            quality=100,allow_mixed=True,minimize_size=False,method=6,
                            kmax = 1)
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
        if convertToFileExtension=='.gif' and InComingFileExtension=='.jpg':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            RGBImage=image.convert('RGB')
            RGBImage.save(f"{imagePath}{randomImageName}{convertToFileExtension}",format='gif')
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
        if convertToFileExtension=='.webp' and InComingFileExtension=='.jpg':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            RGBImage=image.convert('RGB')
            RGBImage.save(f"{imagePath}{randomImageName}{convertToFileExtension}",format='webp')
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
        if convertToFileExtension=='.png' and InComingFileExtension=='.webp':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            RGBImage=image.convert('RGB')
            RGBImage.save(f"{imagePath}{randomImageName}{convertToFileExtension}",format='png')
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
        if convertToFileExtension=='.jpg' and InComingFileExtension=='.webp':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            RGBImage=image.convert('RGB')
            RGBImage.save(f"{imagePath}{randomImageName}{convertToFileExtension}",format='JPEG')
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
            
        if  convertToFileExtension=='.jpg' and InComingFileExtension=='.tiff':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            RGBImage=image.convert('RGB')
            RGBImage.save(f"{imagePath}{randomImageName}{convertToFileExtension}",format='JPEG')
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
        if  convertToFileExtension=='.png' and InComingFileExtension=='.tiff':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            RGBImage=image.convert('RGB')
            RGBImage.save(f"{imagePath}{randomImageName}{convertToFileExtension}",format='PNG')
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
        if  convertToFileExtension=='.jpg' and InComingFileExtension=='.png':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            RGBImage=image.convert('RGB')
            RGBImage.save(f"{imagePath}{randomImageName}{convertToFileExtension}",format='JPEG')
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
        if convertToFileExtension=='.jpg' and InComingFileExtension=='.bmp':
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            image.save(f"{imagePath}{randomImageName}{convertToFileExtension}",format='JPEG')
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{convertToFileExtension}',  
                  }
            return self.return_response(data=data)
        return Response({'detail':'please provide a a valid file path you want to convert to'})
    def delete(self, request, *args, **kwargs):
        if kwargs:
            id=kwargs['pk']
            if (type(id)==type(1)):
                instance=get_object_or_404(ImageConverterModel, pk=id)
                if instance:
                    imagePathFromDomain=instance.convertedImage
                    domain=request.get_host()
                    storagePathFromDomain=f"http://{domain}/media/"
                    ImageName=imagePathFromDomain.removeprefix(storagePathFromDomain)
                    convertedFromExtension=instance.convertedFromExtension
                    convertedToFileExtension=ImageName[ImageName.rindex('.'):]
                    fileNameWithoutExtension=ImageName[:ImageName.rindex('.')]
                    basePath=Path(__file__).resolve().parent.parent
                    path=f"{basePath}\media\\"
                    instance.delete()
                    print(convertedFromExtension=='.webp' and convertedToFileExtension==".gif")
                    if convertedFromExtension=='.webp' and convertedToFileExtension==".gif":
                        os.remove(f'{path}{fileNameWithoutExtension}{convertedFromExtension}')
                    try:
                        os.remove(f'{path}{ImageName}')
                    except FileNotFoundError:
                        return Response({'detail':f"{ImageName} is not Available in Your Files"},status=status.HTTP_404_NOT_FOUND)
                    return Response({'detail':'Image and Instance Has been Deleted'},status=status.HTTP_204_NO_CONTENT)
            return Response({'detail':"instance doesnot exist"})
        if not kwargs:
            qs=ImageConverterModel.objects.all()
            if qs:
                for instance in qs :
                    imagePathFromDomain=instance.convertedImage
                    domain=request.get_host()
                    storagePathFromDomain=f"http://{domain}/media/"
                    ImageName=imagePathFromDomain.removeprefix(storagePathFromDomain)
                    convertedFromExtension=instance.convertedFromExtension
                    convertedToFileExtension=ImageName[ImageName.rindex('.'):]
                    fileNameWithoutExtension=ImageName[:ImageName.rindex('.')]
                    basePath=Path(__file__).resolve().parent.parent
                    path=f"{basePath}\media\\"
                    instance.delete()
                    if convertedFromExtension=='.webp' and convertedToFileExtension==".gif":
                        os.remove(f'{path}{fileNameWithoutExtension}{convertedFromExtension}')
                    try:
                        os.remove(f'{path}{ImageName}')
                    except FileNotFoundError:
                        return Response({'detail':f"{ImageName} is not Available in Your Files"},status=status.HTTP_404_NOT_FOUND)
                        
                return Response({'detail':'All instanses deleted'})
            else:
                return Response({'detail':'all instances are already deleted'})
        return Response({"detail":"Something Went Wrong...."})


        
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

        
    
