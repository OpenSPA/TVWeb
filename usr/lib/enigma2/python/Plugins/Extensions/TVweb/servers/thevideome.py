# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para thevideo.me
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsunpack

def test_video_exists( page_url ):
    logger.info("pelisalacarta.servers.thevideome test_video_exists(page_url='%s')" % page_url)
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.thevideome url="+page_url)
    if not "embed" in page_url:
      page_url = page_url.replace("http://vodlocker.com/","http://vodlocker.com/embed-") + ".html"
    
    data = scrapertools.cache_page( page_url )
    media_urls = scrapertools.find_multiple_matches(data,"'label'\s*\:\s*'([^']+)'\s*\,\s*'file'\s*\:\s*'([^']+)'")
    video_urls = []

    for label,media_url in media_urls:
        video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" ("+label+") [thevideo.me]",media_url])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    patronvideos  = 'thevideo.me/embed-([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.thevideome find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[thevideo.me]"
        url = "http://thevideo.me/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'thevideome' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    patronvideos  = 'thevideo.me/([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.thevideome find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[thevideo.me]"
        url = "http://thevideo.me/embed-"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'thevideome' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
    return devuelve

def test():

    video_urls = get_video_url("http://thevideo.me/embed-dwjga2jngh0n.html")

    return len(video_urls)>0