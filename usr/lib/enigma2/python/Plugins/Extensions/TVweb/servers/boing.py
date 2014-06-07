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
    logger.info("[boing.py] get_video_url(page_url='%s')" % page_url)
    
    # Descarga la página
    # http://www.boing.es/serie/geronimo-stilton/video/top-model
    data = scrapertools.cache_page(page_url)
    player_id = scrapertools.get_match( data,'<param name="playerID" value="([^"]+)"' )
    publisher_id = scrapertools.get_match( data,'<param name="publisherID" value="([^"]+)"' )
    video_id = scrapertools.get_match( data,'<param name="videoId" value="([^"]+)"' )
    
    #http://i.cdn.turner.com/tbseurope/big/Boing_ES/thumbs/SP_SA_GERSTI0018_01.jpg
    thumbnail = scrapertools.get_match( data , '(http\://i.cdn.turner.com/.*?.jpg)' )
    
    #http://ht.cdn.turner.com/tbseurope/big/Boing_ES/videos/SP_SA_GERSTI0017_01.mp4
    video = thumbnail
    video = video.replace("i.cdn","ht.cdn")
    video = video.replace("/thumbs/","/videos/")
    video = video.replace(".jpg",".mp4")

    #http://ht.cdn.turner.com/tbseurope/big/Boing_ES/videos/SP_SA_GERSTI0017_01.mp4?videoId=1542699684001&lineUpId=&pubId=41801939001&playerId=1156722107001&affiliateId=
    url = video+"?videoId="+video_id+"&lineUpId=&pubId="+publisher_id+"&playerId="+player_id+"&affiliateId="
    logger.info("url="+url)

    video_urls = []
    video_urls.append( [ "(mp4) [boing]" , url ] )

    for video_url in video_urls:
        logger.info("[boing.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

