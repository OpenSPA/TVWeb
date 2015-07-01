# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para gamovideo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import unpackerjs3

def test_video_exists( page_url ):
    logger.info("youwatch test_video_exists(page_url='%s')" % page_url)
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("youwatch get_video_url(page_url='%s')" % page_url)
    if not "embed" in page_url:
      page_url = page_url.replace("http://youwatch.org/","http://youwatch.org/embed-") + ".html"

    data = scrapertools.cache_page(page_url)
    data = scrapertools.find_single_match(data,"<span id='flvplayer'></span>\n<script type='text/javascript'>(.*?)\n;</script>")
    data = unpackerjs3.unpackjs(data,0)
    url = scrapertools.get_match(data, 'file:"([^"]+)"')
    video_urls = []
    video_urls.append([scrapertools.get_filename_from_url(url)[-4:]+" [youwatch]",url])

    for video_url in video_urls:
        logger.info("[youwatch.py] %s - %s" % (video_url[0],video_url[1]))
        

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []


    patronvideos  = 'http://youwatch.org/([a-z0-9]+)'
    logger.info("youwatch find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[youwatch]"
        url = "http://youwatch.org/"+match
        if url not in encontrados and match!="embed":
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'youwatch' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            

    patronvideos  = 'http://youwatch.org/embed-([a-z0-9]+)'
    logger.info("youwatch find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[youwatch]"
        url = "http://youwatch.org/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'youwatch' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve

def test():
    video_urls = get_video_url("http://youwatch.org/crbt4sja1jvo")

    return len(video_urls)>0