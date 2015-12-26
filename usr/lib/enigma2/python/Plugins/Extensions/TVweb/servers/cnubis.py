# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para backin.net
# by be4t5
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.cnubis page_url="+page_url)
    video_urls = []
 
    data = scrapertools.cache_page(page_url)
    media_url = scrapertools.find_single_match(data,'file: "([^"]+)"')
    logger.info("media_url="+media_url)

    # URL del vídeo
    video_urls.append( [ ".mp4" + " [cnubis]",media_url ] )

    for video_url in video_urls:
       logger.info("pelisalacarta.servers.cnubis %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos de este servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []
	
	# https://cnubis.com/plugins/mediaplayer/site/_embed.php?u=9mk&w=640&h=320
    patronvideos  = 'cnubis.com/plugins/mediaplayer/site/_embed.php\?u\=([A-Za-z0-9]+)'
    logger.info("pelisalacarta.servers.cnubis find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(text)

    for match in matches:
        titulo = "[cnubis]"
        url = "https://cnubis.com/plugins/mediaplayer/site/_embed.php?u="+match+"&w=640&h=320"
        if url not in encontrados and id != "":
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'cnubis' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)        

    return devuelve

def test():

    video_urls = get_video_url("https://cnubis.com/plugins/mediaplayer/site/_embed.php?u=9mk&w=640&h=320")
    return len(video_urls)>0
