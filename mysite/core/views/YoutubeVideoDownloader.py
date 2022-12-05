from .imports import *
class VideoDownloader(APIView):
    def post(self,request,*args,**kwargs):
        yt = YouTube('https://www.youtube.com/watch?v=oTKtF3IzamM')
        Url1080p=yt.streams.filter(resolution='1080p',file_extension='mp4').first().url
        Url720p=yt.streams.filter(resolution='720p',file_extension='mp4').first().url
        Url480p=yt.streams.filter(resolution='480p',file_extension='mp4').first().url
        Url360p=yt.streams.filter(resolution='360p',file_extension='mp4').first().url
        Url240p=yt.streams.filter(resolution='240p',file_extension='mp4').first().url
        Url144p=yt.streams.filter(resolution='144p',file_extension='mp4').first().url
        audio=yt.streams.filter(only_audio=True).desc().first().url   
        data={'Url1080p':Url1080p,'Url720p':Url720p,'Url480p':Url480p,'Url360p':Url360p,'Url240p':Url240p,'Url144p':Url144p,'Audio':audio}
        return Response(data)