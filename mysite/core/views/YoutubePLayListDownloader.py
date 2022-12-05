from .imports import *
class PlaylistDownloader(APIView):
    def post(self,request,*args,**kwargs):
        p = Playlist('https://www.youtube.com/watch?v=IWokdGbPk50&list=PLasCX3wfxLR0OmydLRqU1kwPL5IYhtK5E&index=1')
        data={}
        i=0
        for video in p.videos:
            Url1080p=video.streams.filter(resolution='1080p',file_extension='mp4').first().url
            data[f'videoNO_{i}_Url1080p']=Url1080p
            Url720p=video.streams.filter(resolution='720p',file_extension='mp4').first().url
            data[f'videoNO_{i}_Url720p']=Url720p
            Url480p=video.streams.filter(resolution='480p',file_extension='mp4').first().url
            data[f'videoNO_{i}_Url480p']=Url480p
            Url360p=video.streams.filter(resolution='360p',file_extension='mp4').first().url
            data[f'videoNO_{i}_Url360p']=Url360p
            Url240p=video.streams.filter(resolution='240p',file_extension='mp4').first().url
            data[f'videoNO_{i}_Url240p']=Url240p
            Url144p=video.streams.filter(resolution='144p',file_extension='mp4').first().url
            data[f'videoNO_{i}_Url144p']=Url144p
            audio=video.streams.filter(only_audio=True).desc().first().url   
            data[f'videoNO_{i}_Audio']=audio
            i=i+1
        return Response(data)