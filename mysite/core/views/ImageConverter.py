from .imports import *
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
        if request.data['image']:
            imageName=request.data['image'].name
            inComingImageFile=request.data['image']
            InComingFileExtension=imageName[imageName.rindex('.'):]
            image=Image.open(inComingImageFile)
        else:
            return Response({'detail':'please provide a image you want to convert.'})
        inComingPurpose=""
        if request.data['convert_to']:
            convertToFileExtension=request.data['convert_to']
        elif request.data['purpose']:
            inComingPurpose=request.data['purpose']
        else:
            return Response({'detail':'please provide a image you want to convert.'})
        randomString=f"{datetime.datetime.now().date()}_{str(datetime.datetime.now().time()).replace('.','').replace(':','')}"
        basePath=Path(__file__).resolve().parent.parent.parent
        imagePath=f"{basePath}\media\\"
        if  inComingPurpose=='resize' and inComingImageFile:
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            width=request.data['width']
            height=request.data['height']
            RGBImage=image.resize((width,height))
            RGBImage.save(f"{imagePath}{randomImageName}{InComingFileExtension}")
            domain=request.get_host()
            storagePathFromDomain=f"http://{domain}/media/"
            data={'convertedFromExtension':InComingFileExtension,
                'convertedImage':f'{storagePathFromDomain}{randomImageName}{InComingFileExtension}',  
                }
            return self.return_response(data=data)
        if inComingPurpose=='crop' and inComingImageFile :
            randomImageName=f"image_{randomString}_{self.generate_random_string()}"
            # RGBImage=image.convert('RGB')
            width, height = image.size
            if request.data['x_axis'] and request.data['y_axis'] and request.data['width'] and request.data['height']:
                x_axis = request.data['x_axis']
                y_axis = request.data['y_axis']
                xPlusWidth = request.data['width']+x_axis
                yPlusHeight = request.data['height']+y_axis
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
                    basePath=Path(__file__).resolve().parent.parent.parent
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
                    basePath=Path(__file__).resolve().parent.parent.parent
                    path=f"{basePath}\media\\"
                    instance.delete()
                    if convertedFromExtension=='.webp' and convertedToFileExtension==".gif":
                        os.remove(f'{path}{fileNameWithoutExtension}{convertedFromExtension}')
                    try:
                        os.remove(f'{path}{ImageName}')
                    except FileNotFoundError:
                        continue
                        
                return Response({'detail':'All instanses deleted'})
            else:
                return Response({'detail':'all instances are already deleted'})
        return Response({"detail":"Something Went Wrong...."})