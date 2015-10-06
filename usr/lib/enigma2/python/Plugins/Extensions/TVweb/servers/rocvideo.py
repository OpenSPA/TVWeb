# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para rocvideo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsunpack

def test_video_exists( page_url ):
    logger.info("pelisalacarta.servers.rocvideo test_video_exists(page_url='%s')" % page_url)
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.rocvideo url="+page_url)
    if not "embed" in page_url:
        page_url = page_url.replace("http://rocvideo.tv/","http://rocvideo.tv/embed-") + ".html"

    data = scrapertools.cache_page( page_url )

    data = scrapertools.find_single_match(data,"<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
    data = jsunpack.unpack(data)
    logger.info("data="+data)

    #file:"http://s1.rocvideo.tv/files/2/aqsk8q5mjcoh1d/INT3NS4HDTS-L4T.mkv.mp4
    media_url = scrapertools.get_match(data,'file:"([^"]+)"')
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" [rocvideo]",media_url])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    #http://rocvideo.net/mfhpecruzj2q
    #http://rocvideo.tv/mfhpecruzj2q
    patronvideos  = 'rocvideo.(?:tv|net)/embed-([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.rocvideo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[rocvideo]"
        url = "http://rocvideo.tv/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'rocvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    patronvideos  = 'rocvideo.(?:tv|net)/([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.rocvideo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[rocvideo]"
        url = "http://rocvideo.tv/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'rocvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():

    video_urls = get_video_url("http://rocvideo.tv/embed-7ulyffzxwpyu.html")

    return len(video_urls)>0
