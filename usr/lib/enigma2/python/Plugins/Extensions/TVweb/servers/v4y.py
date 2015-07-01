# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para v4y
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def test_video_exists( page_url ):
    logger.info("v4y test_video_exists(page_url='%s')" % page_url)
    
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("v4y get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    #logger.info("data="+data)

    media_url = scrapertools.find_single_match(data,'file: "([^"]+)"')
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" [v4y]",media_url])

    for video_url in video_urls:
        logger.info("[v4y.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = 'http://v4y.me/([a-z0-9]+)'
    logger.info("v4y find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[v4y]"
        url = "http://v4y.me/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'v4y' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():
    video_urls = get_video_url("http://v4y.me/cum6ozi47zdr")

    return len(video_urls)>0