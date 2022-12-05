from .imports import *
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
        basePath=Path(__file__).resolve().parent.parent.parent
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
                basePath=Path(__file__).resolve().parent.parent.parent
                path=f"{basePath}\media\\"
                instance.delete()
                os.remove(f'{path}{pdfName}')
                return Response({'detail':'deleted '})
            return Response({'detail':"instance doesnot exist"})
        return Response({"detail":"Please Provide the Id of object you want to delete"})