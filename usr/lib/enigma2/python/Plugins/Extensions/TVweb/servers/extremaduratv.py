# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para extremaduratv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("[extremaduratv.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    # Descarga la página como navegador web
    #http://www.canalextremadura.es/alacarta/tv/videos/extremadura-desde-el-aire
    #<div id="mediaplayer" rel="rtmp://canalextremadurafs.fplive.net/canalextremadura/#tv/S-B5019-006.mp4#535#330"></div>
    data = scrapertools.cachePage(page_url)
    patron  = '<div id="mediaplayer" rel="([^"]+)"></div>'
    matches = re.findall(patron,data,re.DOTALL)

    for url in matches:
        partes = url.split("#")
        url = partes[0]+partes[1]
        logger.info("url="+url)
        video_urls.append( [ "RTMP [extremaduratv]" , url.replace(" ","%20") ] )

    # Descarga la página como ipad
    headers = []
    headers.append( ["User-Agent","Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10"] )
    data = scrapertools.cachePage(page_url,headers=headers)
    logger.info("data="+data)
    patron = "<video.*?src ='([^']+)'"
    matches = re.findall(patron,data,re.DOTALL)

    for url in matches:
        video_urls.append( [ "iPhone [extremaduratv]" , url ] )

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '(http://www.canalextremadura.es/alacarta/tv/videos/([a-z0-9\-]+)'
    logger.info("[extremaduratv.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[extremaduratv]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'tvg' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve

