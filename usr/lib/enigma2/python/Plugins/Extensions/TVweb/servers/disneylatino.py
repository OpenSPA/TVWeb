# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para disney latino
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("servers.disneylatino get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)
    data = scrapertools.find_single_match(data,'<script type="text/javascript">this.Grill.Grill.burger\=(.*?)\:\(function\(\)')
    data_json = jsontools.load_json(data)

    calidades = data_json["stack"][0]["data"][0]["flavors"]
    for calidad in calidades:
        title = calidad["width"]+"x"+calidad["height"]+" (Formato "+calidad["format"].upper()+" a "+str(calidad["bitrate"])+"Kbps)"
        url = calidad["url"]
        thumbnail = ""
        plot = ""

        if calidad["format"]=="unknown-3gp":
            video_urls.reverse()
            video_urls.append( [ title+" [disneylatino]" , url ] )
            video_urls.reverse()
        else:
            video_urls.append( [ title+" [disneylatino]" , url ] )

    for video_url in video_urls:
        logger.info("servers.disneylatino %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

