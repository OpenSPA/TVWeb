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
from core import unpackerjs

def test_video_exists( page_url ):
    logger.info("videostoring test_video_exists(page_url='%s')" % page_url)
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("videostoring get_video_url(page_url='%s')" % page_url)
    if not "embed" in page_url:
      page_url = page_url.replace("http://www.videostoring.com/","http://www.videostoring.com/embed-") + ".html"

    data = scrapertools.cache_page(page_url)
    data = scrapertools.find_single_match(data,"<script type='text/javascript'>(.*?)</script>")
    data = unpackerjs.unpackjs(data)
    
    url = scrapertools.get_match(data, '<param name="src"value="([^"]+)"/>')
    video_urls = []
    video_urls.append([scrapertools.get_filename_from_url(url)[-4:]+" [videostoring]",url])


    for video_url in video_urls:
        logger.info("[videostoring.py] %s - %s" % (video_url[0],video_url[1]))
        

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []


    patronvideos  = 'http://www.videostoring.com/([a-z0-9]+)'
    logger.info("videostoring find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[videostoring]"
        url = "http://www.videostoring.com/"+match
        if url not in encontrados and match!="embed":
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'videostoring' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            

    patronvideos  = 'http://www.videostoring.com/embed-([a-z0-9]+)'
    logger.info("videostoring find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[videostoring]"
        url = "http://www.videostoring.com/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'videostoring' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve

def test():
    video_urls = get_video_url("http://www.videostoring.com/crbt4sja1jvo")

    return len(video_urls)>0