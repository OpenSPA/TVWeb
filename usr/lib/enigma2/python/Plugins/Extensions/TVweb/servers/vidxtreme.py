# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para vidxtreme
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsunpack

def test_video_exists( page_url ):
    logger.info("pelisalacarta.servers.vidxtreme test_video_exists(page_url='%s')" % page_url)
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.vidxtreme url="+page_url)
    if not "embed" in page_url:
        page_url = page_url.replace("http://www.vidxtreme.to/","http://www.vidxtreme.to/embed-") + ".html"

    data = scrapertools.cache_page( page_url )
    logger.info("data="+data)

    data = scrapertools.find_single_match(data,"<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
    logger.info("data="+data)

    data = jsunpack.unpack(data)
    logger.info("data="+data)

    media_urls = scrapertools.find_multiple_matches(data,'\{file\:"([^"]+)",label\:"([^"]+)"\}')
    video_urls = []
    for media_url,label in media_urls:
        video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" ("+label+") [vidxtreme]",media_url])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    patronvideos  = 'vidxtreme.to/embed-([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.vidxtreme find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[vidxtreme]"
        url = "http://www.vidxtreme.to/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vidxtreme' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    patronvideos  = 'vidxtreme.to/([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.vidxtreme find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[vidxtreme]"
        url = "http://www.vidxtreme.to/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vidxtreme' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():

    video_urls = get_video_url("http://www.vidxtreme.to/embed-kccahcsouxm0.html")

    return len(video_urls)>0
