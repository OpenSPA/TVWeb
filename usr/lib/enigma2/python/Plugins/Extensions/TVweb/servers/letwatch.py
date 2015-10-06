# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para letwatch
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsunpack

def test_video_exists( page_url ):
    logger.info("pelisalacarta.servers.letwatch test_video_exists(page_url='%s')" % page_url)
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.letwatch url="+page_url)
    if not "embed" in page_url:
      page_url = page_url.replace("http://letwatch.to/","http://letwatch.to/embed-") + ".html"
    
    data = scrapertools.cache_page( page_url )

    data = scrapertools.find_single_match(data,"<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
    logger.info("data="+data)
    data = jsunpack.unpack(data)
    logger.info("data="+data)

    # Extrae la URL
    #{label:"240p",file:"http://188.240.220.186/drjhpzy4lqqwws4phv3twywfxej5nwmi4nhxlriivuopt2pul3o4bkge5hxa/video.mp4"}
    video_urls = []
    media_urls = scrapertools.find_multiple_matches(data,'\{file\:"([^"]+)",label\:"([^"]+)"\}')
    video_urls = []
    for media_url,label in media_urls:
        video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" ("+label+") [letwatch]",media_url])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    #logger.info("data="+data)
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    #letwatch.us/embed-e47krmd6vqo1
    patronvideos  = 'letwatch.(?:us|to)/embed-([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.letwatch find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[letwatch]"
        url = "http://letwatch.to/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'letwatch' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
    
    #letwatch.us/e47krmd6vqo1
    patronvideos  = 'letwatch.(?:us|to)/([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.letwatch find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[letwatch]"
        url = "http://letwatch.to/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'letwatch' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
    return devuelve

def test():

    video_urls = get_video_url("http://letwatch.to/embed-e47krmd6vqo1.html")

    return len(video_urls)>0