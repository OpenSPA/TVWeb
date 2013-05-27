# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Conector para telefe
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("[telefe.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    # Descarga la página del vídeo
    data = scrapertools.cache_page(page_url)

    # Prueba primero con telefónica
    try:
        rtmpUrl = scrapertools.get_match(data,"var rtmpUrl \= \['(rtmp\://[^']+)'")
        streamName = scrapertools.get_match(data,"var streamName \= '(mp4[^']+)'")

        video_url = rtmpUrl+"/"+streamName
        video_urls.append( [ "[telefe]" , video_url ] )

        logger.info("[telefe.py] Encontrado vídeo en formato Telefónica: "+video_url)
    
    except:

        # Descarga el descriptor del vídeo
        # El vídeo:
        # <script type="text/javascript" src="http://flash.velocix.com/c1197/legacy/UAAA1582_X264_480x360.mp4?format=jscript2&protocol=rtmpe&vxttoken=00004EAA82A8000000000289A60672657573653D32EBF4321F280103EC9B2025F74095B4E74A0E459A" ></script>
        # El anuncio:
        # <script type="text/javascript" src="http://flash.velocix.com/bt/145e8eae1563f092fbdf905113f7c213ebefd8e6/flash?format=jscript2&protocol=rtmpte&vxttoken=00004EAA693D0000000002897CEF72657573653D320830AA52351D57C26FFD6E55F9183C6342438DEB" ></script>
        patron  = '<script type="text/javascript" src="(http://flash.velocix.com/[^"]+)" ></script>'
        matches = re.compile(patron,re.DOTALL).findall(data)
        scrapertools.printMatches(matches)

        if len(matches)>0:
            logger.info("[telefe.py] Encontrado vídeo en formato Velocix")
            page_url2 = matches[0]
            data2 = scrapertools.cache_page(page_url2)
            print("data2="+data2)
            '''
            var streamName = "mp4:bt-145e8eae1563f092fbdf905113f7c213ebefd8e6";
            var rtmpUrl = [];
            rtmpUrl.push("rtmpte://201.251.164.11/flash?vxttoken=00004EAA693D0000000002897CEF72657573653D320830AA52351D57C26FFD6E55F9183C6342438DEB");
            rtmpUrl.push("rtmpte://201.251.118.11/flash?vxttoken=00004EAA693D0000000002897CEF72657573653D320830AA52351D57C26FFD6E55F9183C6342438DEB");
            '''
            patron = 'streamName \= "([^"]+)"'
            matches = re.compile(patron,re.DOTALL).findall(data2)
            streamName = matches[0]
    
            patron = 'rtmpUrl\.push\("([^"]+)"\)'
            matches = re.compile(patron,re.DOTALL).findall(data2)
            if len(matches)>0:
                videourl = matches[0]+"/"+streamName
            
                logger.info(videourl)
                video_urls.append( [ "[telefe]" , videourl ] )
        else:
            logger.info("[telefe.py] NO encontrado vídeo")

    for video_url in video_urls:
        logger.info("[telefe.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # divxstage http://www.divxstage.net/video/2imiqn8w0w6dx"
    patronvideos  = 'http://www.divxstage.[\w]+/video/([\w]+)'
    logger.info("[telefe.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[telefe]"
        url = "http://www.divxstage.net/video/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'divxstage' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve
