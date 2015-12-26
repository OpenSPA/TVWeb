# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para vimple.ru
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[vimple.ru] get_video_url(page_url=%s)" % page_url)

    media_url = scrapertools.get_match(
        re.sub(
            r'\t|\n|\r|\s',
            '',
            scrapertools.cache_page(page_url)
        ),
        '"video"[^,]+,"url":"([^"]+)"'
    ).replace('\\','')

    media_url+= "|Cookie=" + \
        scrapertools.get_match(
            config.get_cookie_data(),
            '.vimple.ru.*?(UniversalUserID\t[a-f0-9]+)'
        ).replace('\t', '=')

    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" [vimple.ru]",media_url])

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.vimpleru %s - %s" % (video_url[0],video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://player.vimple.ru/iframe/21ff2440e9174286ad8c22cd2efb94d2
    patronvideos  = 'vimple.ru/iframe/([a-f0-9]+)'
    logger.info("[vimple.ru] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[vimpleru]"
        url = "http://player.vimple.ru/iframe/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'vimpleru' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
