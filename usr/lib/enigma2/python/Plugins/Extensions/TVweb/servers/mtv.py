# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para mtv
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.mtv get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page("http://web.pydowntv.com/api?url="+page_url)
    url = scrapertools.get_match(data,'"url_video"\: \["([^"]+)"\]')

    video_urls = []
    video_urls.append( [ "[mtv]" , url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.mtv %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
