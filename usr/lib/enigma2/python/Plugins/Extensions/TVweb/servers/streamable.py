# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para streamable
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsunpack

def test_video_exists( page_url ):
    logger.info("streamable test_video_exists(page_url='%s')" % page_url)
    
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("streamable get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)


    # Extrae la URL
    data = scrapertools.find_single_match(data,'<embed(.*?)</embed>')
    data = scrapertools.find_single_match(data,'setting=(.*?)"')
    import base64
    info_url= base64.b64decode(data)
    data = scrapertools.cache_page(info_url)
    vcode = scrapertools.find_single_match(data,'"vcode":"(.*?)",')
    st = scrapertools.find_single_match(data,'"st":(.*?),')
    media_url = "http://video.streamable.ch/s?v="+vcode+"&t="+st
    filename= scrapertools.get_header_from_response(media_url,header_to_get="content-disposition")
    filename = scrapertools.find_single_match(filename,'filename="(.*?)"')
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(filename)[-4:]+" [streamable]",media_url])

    for video_url in video_urls:
        logger.info("[streamable.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://powvideo.net/embed-sbb9ptsfqca2
    patronvideos  = 'http://www.streamable.ch/video/([a-z0-9]+)'
    logger.info("streamable find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[streamable]"
        url = "http://www.streamable.ch/video/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'streamable' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve

def test():
    video_urls = get_video_url("http://www.streamable.ch/video/zC87XnmL4")

    return len(video_urls)>0