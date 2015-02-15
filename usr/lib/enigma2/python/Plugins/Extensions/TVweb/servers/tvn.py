# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para tvn.cl
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os
import random

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("tvalacarta.servers.tvn get_video_url(page_url='%s')" % page_url)
    video_urls = []

    # Lee la página del vídeo
    data = scrapertools.cache_page(page_url)

    # Compone la URL
    #AutoStart:true,
    #Url:'/programas/cumbresdelmundo/2012/videos/cumbres_100313_c.mp4',
    stream = scrapertools.get_match(data,"AutoStart:true,\s+Url\:'([^']+)'")
    #http://wow3.tvn.cl:1935/mediacache/_definst_/mp4://programas/cumbresdelmundo/2012/videos/cumbres_100313_c.mp4/playlist.m3u8
    #url = "http://wow3.tvn.cl:1935/mediacache/_definst_/mp4:/"+stream+"/playlist.m3u8"
    #http://edge-30-tvn.edge.mdstrm.com/mediacache/_definst_/mp4://teleseries/elamorlomanejoyo/videos/cap44-elamorlomanejoyo-capitulo.mp4/playlist.m3u8
    url = "http://edge-30-tvn.edge.mdstrm.com/mediacache/_definst_/mp4:/"+stream+"/playlist.m3u8"
    logger.info("url="+url)

    video_urls.append( [ "[tvn.cl]" , url ] )

    for video_url in video_urls:
        logger.info("tvalacarta.servers.tvn %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

