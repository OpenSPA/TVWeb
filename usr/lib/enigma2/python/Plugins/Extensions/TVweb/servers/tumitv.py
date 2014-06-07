# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para tumi.tv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import re
import urllib

from core import scrapertools
from core import logger

# Returns an array of possible video url's from the page_url
def get_video_url( page_url , premium = False , user="" , password="" , video_password="" ):
    logger.info("pelisalacarta.tumitv get_video_url(page_url='%s')" % page_url)

    video_urls = []

    data = scrapertools.cache_page(page_url)
    url = scrapertools.get_match(data,'file\: "([^"]+)"')
    video_url = ["flv [tumi.tv]", url ]
    video_urls.append( video_url )

    for video_url in video_urls:
        logger.info("pelisalacarta.tumitv %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos de este servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    # http://www.tumi.tv/rzy0xuus6esv
    patronvideos  = 'tumi.tv/([a-z0-9]+)'
    logger.info("pelisalacarta.tumitv find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(text)

    for match in matches:
        titulo = "[tumi.tv]"
        if match!="iframe":
            url = "http://www.tumi.tv/iframe-"+match+"-600x400.html"
            if url not in encontrados:
                logger.info("  url="+url)
                devuelve.append( [ titulo , url , 'tumitv' ] )
                encontrados.add(url)
            else:
                logger.info("  url duplicada="+url)

    # http://www.tumi.tv/iframe-rzy0xuus6esv-600x400.html
    patronvideos  = 'tumi.tv/iframe-([a-z0-9]+)'
    logger.info("pelisalacarta.tumitv find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(text)

    for match in matches:
        titulo = "[tumi.tv]"
        url = "http://www.tumi.tv/iframe-"+match+"-600x400.html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'tumitv' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)


    return devuelve