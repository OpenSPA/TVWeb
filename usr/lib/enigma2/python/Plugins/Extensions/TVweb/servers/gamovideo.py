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
from core import jsunpack

def test_video_exists( page_url ):
    logger.info("pelisalacarta.gamovideo test_video_exists(page_url='%s')" % page_url)
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.gamovideo get_video_url(page_url='%s')" % page_url)
    if not "embed" in page_url:
      page_url = page_url.replace("http://gamovideo.com/","http://gamovideo.com/embed-") + "-640x360.html"

    data = scrapertools.cache_page(page_url)
    data = scrapertools.find_single_match(data,"<script type='text/javascript'>(.*?)</script>")
    data = jsunpack.unpack(data)
    
    host = scrapertools.get_match(data, 'image:"(http://[^/]+/)')
    flv_url = scrapertools.get_match(data, ',\{file:"([^"]+)"')
    rtmp_url = scrapertools.get_match(data, '\[\{file:"([^"]+)"')
    flv = host+flv_url.split("=")[1]+"/v.flv"

    video_urls = []
    video_urls.append([scrapertools.get_filename_from_url(flv)[-4:]+" [gamovideo]",flv])
    #video_urls.append(["RTMP [gamovideo]",rtmp_url])      

    for video_url in video_urls:
        logger.info("[gamovideo.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://gamovideo.com/auoxxtvyoy
    # http://gamovideo.com/h1gvpjarjv88
    patronvideos  = 'gamovideo.com/([a-z0-9]+)'
    logger.info("pelisalacarta.gamovideo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[gamovideo]"
        url = "http://gamovideo.com/"+match
        if url not in encontrados and match!="embed":
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'gamovideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    # http://gamovideo.com/embed-sbb9ptsfqca2-588x360.html
    patronvideos  = 'gamovideo.com/embed-([a-z0-9]+)'
    logger.info("pelisalacarta.gamovideo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[gamovideo]"
        url = "http://gamovideo.com/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'gamovideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve

def test():
    video_urls = get_video_url("http://gamovideo.com/91zidptmfqnr")

    return len(video_urls)>0