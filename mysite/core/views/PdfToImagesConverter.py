from .imports import *
class PdfToImage(generics.ListCreateAPIView,generics.DestroyAPIView,generics.RetrieveAPIView):
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
    def get(self,request,*args,**kwargs):
        pk=kwargs.get('pk')
        if pk is not None:
            return self.retrieve(request,*args,**kwargs)
        return self.list(request,*args,**kwargs)
    def post(self,request,*args,**krargs):
        imageName=request.data['image'].name
        inComingImageFile=request.data['image']
        InComingFileExtension=imageName[imageName.rindex('.'):]
        convertToFileExtension=request.data['convert_to']
        randomString=f"{datetime.datetime.now().date()}_{str(datetime.datetime.now().time()).replace('.','').replace(':','')}"
        basePath=Path(__file__).resolve().parent.parent.parent
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
        return Response({'detail':'something went Wrong'})
    def delete(self,request,*args,**kwargs):
            if kwargs:
                id=kwargs['pk']
                if (type(id)==type(1)):
                    instance=get_object_or_404(PdfToImageModel, pk=id)
                    if instance:
                        FolderName=instance.folderName
                        basePath=Path(__file__).resolve().parent.parent.parent
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
                        basePath=Path(__file__).resolve().parent.parent.parent
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