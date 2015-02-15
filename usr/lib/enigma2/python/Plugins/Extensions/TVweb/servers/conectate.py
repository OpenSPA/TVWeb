# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para conectate
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("tvalacarta.servers.conectate get_video_url(page_url='%s')" % page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)

    rec_id = scrapertools.get_match(data,'"rec_id"\:(\d+)')
    #"streaming_hd":{"file_id":"85c105c6-2920-4c3a-9efd-4511cb3924ef","file_name":"PA-PP-27660.mp4","file_size":"97985552"}
    patron = '"([^"]+)"\:\{"file_id"\:"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    encontrados = set()
    for file_type,file_id in matches:
        if file_id not in encontrados:
            video_urls.append( [ file_type+" [conectate]" , "http://repositoriovideo-download.educ.ar/repositorio/Video/ver?rec_id="+rec_id+"&file_id="+file_id ] )
            encontrados.add(file_id)

    for video_url in video_urls:
        logger.info("tvalacarta.servers.conectate %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
