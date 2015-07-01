# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para meuvideos
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import unpackerjs
import string
import time

def test_video_exists( page_url ):
    logger.info("[meuvideos] test_video_exists(page_url='%s')" % page_url)
    data = SaltarPubli(page_url)
    patron ='<div id="over_player_msg">([^"]+)<span id='
    logger.info(data)
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches) >0:
      Estado = matches[0].replace("<br>", "<br/>") 
      patron = "jah\('(.*?)'\,"
      matches = re.compile(patron,re.DOTALL).findall(data)
      data = scrapertools.downloadpage(matches[0])
      Estado = Estado + " "+ scrapertools.get_match(data,"html\('(.*?)'\)")
      logger.info(Estado)
      return False, Estado
 
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[meuvideos.py] url="+page_url)
    if not "embed" in page_url:
      page_url = page_url.replace("http://meuvideos.com/","http://meuvideos.com/embed-") + ".html"

    data = scrapertools.cache_page(page_url)
    data = "eval" + scrapertools.find_single_match(data,"<script type='text/javascript'>eval(.*?)</script>") 
    data = unpackerjs.unpackjs(data)
    url = scrapertools.get_match(data, 'file:"([^"]+)"')
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(url)[-4:]+" [meuvideos]",url])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    patronvideos  = 'http://meuvideos.com/([a-z0-9]+)'
    logger.info("meuvideos find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[meuvideos]"
        url = "http://meuvideos.com/"+match
        if url not in encontrados and match!="embed":
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'meuvideos' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            

    patronvideos  = 'http://meuvideos.com/embed-([a-z0-9]+)'
    logger.info("meuvideos find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[meuvideos]"
        url = "http://meuvideos.com/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'meuvideos' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve

def test():

    video_urls = get_video_url("http://meuvideos.com/yn1rwiz0rnux")

    return len(video_urls)>0