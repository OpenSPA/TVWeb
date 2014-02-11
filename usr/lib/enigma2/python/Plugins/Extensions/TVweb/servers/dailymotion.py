# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para dailymotion
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Basado en el resolver hecho por Shailesh Ghimire para su plugin "canadanepal"
# http://code.google.com/p/canadanepal-xbmc-plugin/source/browse/script.module.urlresolver/lib/urlresolver/plugins/dailymotion.py?name=Version_0.0.1
#------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.dailymotion get_video_url(page_url='%s')" % page_url)
    video_urls = []
    
    data = scrapertools.cache_page(page_url)
    data = scrapertools.get_match(data,'<param name="flashvars" value="(.*?)"')
    #logger.info("pelisalacarta.dailymotion data="+data)

    #logger.info("data="+data)
    sequence = scrapertools.get_match(data,"sequence=(.*?)$")
    #logger.info("pelisalacarta.dailymotion sequence="+sequence)

    sequence = urllib.unquote(sequence)
    #logger.info("pelisalacarta.dailymotion sequence="+sequence)

    mediaurl = scrapertools.get_match(sequence,'"video_url"\:"([^"]+)"')
    #logger.info("pelisalacarta.dailymotion mediaurl="+mediaurl)

    mediaurl = urllib.unquote(mediaurl)
    logger.info("pelisalacarta.dailymotion mediaurl="+mediaurl)

    video_urls.append( [ "mp4 [dailymotion]", mediaurl ] )

    for video_url in video_urls:
        logger.info("pelisalacarta.dailymotion %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://www.dailymotion.com/embed/video/xrva9o
    # http://www.dailymotion.com/swf/video/xocczx
    patronvideos  = 'dailymotion.com/(?:embed|swf)/video/([a-z0-9]+)'
    logger.info("pelisalacarta.dailymotion find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[dailymotion]"
        url = "http://www.dailymotion.com/video/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'dailymotion' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    # http://www.dailymotion.com/video/xrva9o
    patronvideos  = 'dailymotion.com/video/([a-z0-9]+)'
    logger.info("pelisalacarta.dailymotion find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[dailymotion]"
        url = "http://www.dailymotion.com/video/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'dailymotion' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():
    video_urls = get_video_url("http://www.dailymotion.com/video/xrva9o")
    if len(video_urls)==0:
        return false

    # FLV (No soportado)
    #video_urls = get_video_url("http://www.dailymotion.com/video/xnu7n")
    #if len(video_urls)==0:
    #    return false;

    return True