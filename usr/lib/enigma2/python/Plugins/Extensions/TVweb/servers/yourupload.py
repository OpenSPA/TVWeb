# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para yourupload
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.52 Safari/537.17"

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.yourupload get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    url = scrapertools.find_single_match(data,"file\: '([^']+)'")

    headers = []
    headers.append([ "User-Agent", USER_AGENT] )
    headers.append([ "Referer", page_url])
    headers.append([ "X-Requested-With" , "ShockwaveFlash/19.0.0.185"])

    media_url = scrapertools.get_header_from_response(url,headers=headers,header_to_get="location")
    logger.info("pelisalacarta.servers.mp4upload media_url="+media_url)
    media_url = media_url.replace("?null&start=0","")
    logger.info("pelisalacarta.servers.mp4upload media_url="+media_url)
    #media_url = media_url + "|" + urllib.urlencode({'User-Agent' : USER_AGENT})

    video_urls = []
    video_urls.append([scrapertools.get_filename_from_url(url)[-4:]+" [yourupload]",media_url])

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.yourupload %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    encontrados.add("http://www.yourupload.com/embed/embed")
    devuelve = []

    #http://www.yourupload.com/embed/2PU6jqindD1Q
    patronvideos  = 'yourupload.com/embed/([A-Za-z0-9]+)'
    logger.info("pelisalacarta.servers.yourupload find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[yourupload]"
        url = "http://www.yourupload.com/embed/"+match
        if url not in encontrados and match!="embed":
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'yourupload' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    #http://embed.yourupload.com/2PU6jqindD1Q
    patronvideos  = 'embed.yourupload.com/([A-Za-z0-9]+)'
    logger.info("pelisalacarta.servers.yourupload find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[yourupload]"
        url = "http://www.yourupload.com/embed/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'yourupload' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve

def test():
    video_urls = get_video_url("http://www.yourupload.com/embed/2PU6jqindD1Q")

    return len(video_urls)>0