# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para realvid
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsunpack

def test_video_exists( page_url ):
    logger.info("[realvid.py] test_video_exists(page_url='%s')" % page_url)
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[realvid.py] url="+page_url)
    if not "embed" in page_url:
      page_url = page_url.replace("http://realvid.net/","http://realvid.net/embed-") + ".html"
    data = scrapertools.cache_page( page_url )
    media_url = scrapertools.get_match(data,'file: "([^"]+)",')
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" [realvid]",media_url])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    patronvideos  = 'http://realvid.net/embed-([a-z0-9A-Z]+)'
    logger.info("[realvid.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[realvid]"
        url = "http://realvid.net/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'realvid' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    patronvideos  = 'http://realvid.net/([a-z0-9A-Z]+)'
    logger.info("[realvid.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[realvid]"
        url = "http://realvid.net/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'realvid' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
    return devuelve

def test():

    video_urls = get_video_url("http://realvid.net/embed-m4snvxoc2tsn.html")

    return len(video_urls)>0