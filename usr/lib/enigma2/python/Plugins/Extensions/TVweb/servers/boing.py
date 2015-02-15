# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para boing
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("servers.tvalacarta get_video_url(page_url='%s')" % page_url)
    
    # Descarga la página
    # http://www.boing.es/serie/video/la-verdad
    data = scrapertools.cache_page(page_url)
    player_id = scrapertools.get_match( data,'<param name="playerID" value="([^"]+)"' )
    logger.info("servers.tvalacarta player_id="+player_id)
    publisher_id = scrapertools.get_match( data,'<param name="publisherID" value="([^"]+)"' )
    logger.info("servers.tvalacarta publisher_id="+publisher_id)
    video_id = scrapertools.get_match( data,'<param name="videoId" value="([^"]+)"' )
    logger.info("servers.tvalacarta video_id="+video_id)
    
    #http://i.cdn.turner.com/tbseurope/big/Boing_ES_16_9/thumbs/SP_SA_JOHNYT0045_01.jpg
    thumbnail = scrapertools.get_match( data , '(http\://i.cdn.turner.com/.*?.jpg)' )
    logger.info("servers.tvalacarta thumbnail="+thumbnail)
    
    #http://ht.cdn.turner.com/tbseurope/big/Boing_ES/videos/SP_SA_GERSTI0017_01.mp4
    video = thumbnail
    video = video.replace("i.cdn","ht.cdn")
    video = video.replace("/thumbs/","/videos/")
    video = video.replace(".jpg",".mp4")
    logger.info("servers.tvalacarta video="+video)

    #http://ht.cdn.turner.com/tbseurope/big/Boing_ES_16_9/videos/SP_SA_FLASH%230076_01.mp4?videoId=3831924019001&lineUpId=&pubId=41801939001&playerId=1156722107001&affiliateId=
    url = video+"?videoId="+video_id+"&lineUpId=&pubId="+publisher_id+"&playerId="+player_id+"&affiliateId="
    logger.info("url="+url)

    video_urls = []
    video_urls.append( [ "(mp4) [boing]" , url ] )

    for video_url in video_urls:
        logger.info("servers.tvalacarta %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

