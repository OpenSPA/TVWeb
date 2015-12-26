# -*- coding: utf-8 -*-
# ------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector for vkpass.com
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# by DrZ3r0
# ------------------------------------------------------------

import re

from core import scrapertools
from core import logger


headers = [
    ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:38.0) Gecko/20100101 Firefox/38.0'],
    ['Accept-Encoding', 'gzip, deflate'],
    ['Connection', 'keep-alive']
]


def get_video_url(page_url, premium=False, user="", password="", video_password=""):
    logger.info("[vkpass.py] url=" + page_url)
    video_urls = []

    data = scrapertools.cache_page(page_url)

    referer = scrapertools.find_single_match(data, r"document\.location\.href='([^']+)'")
    headers.append(['Referer', referer])

    data = scrapertools.cache_page(page_url, headers=headers)

    # URL del vídeo
    for url, quality in re.findall(r'\{file:"([^"]+)",\s*label:"([^"]+)"', data, re.DOTALL):
        url = url.replace("%3B", ";")
        video_urls.append([quality + " [vkpass]", url])

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(text):
    encontrados = set()
    devuelve = []

    patronvideos = r'//vkpass.com/token/([^/]+)/vkphash/([^"\']+)'
    logger.info("[vkpass.py] find_videos #" + patronvideos + "#")
    
    matches = re.compile(patronvideos, re.DOTALL).findall(text)

    for media_id, vkphash in matches:
        titulo = "[vkpass]"
        url = 'http://vkpass.com/token/%s/vkphash/%s' % (media_id, vkphash)
        if url not in encontrados:
            logger.info("  url=" + url)
            devuelve.append([titulo, url, 'vkpass'])
            encontrados.add(url)
        else:
            logger.info("  url duplicada=" + url)

    return devuelve
