# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para rtve
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[mitele.py] get_video_url(page_url='%s')" % page_url)

    # Extrae codigo fuente de la web
    html_code = urllib2.urlopen(page_url).read()

    #Se obtiene el host del servicio con la info del video
    url_info = html_code[html_code.find('"host":"') + 8:]
    url_info = url_info[:url_info.find('"')]
    url_info = url_info.replace("\\","")

    logger.info("[mitele.py] url_info=" + url_info )

    #Se obtiene el id para la busqueda de url tokenizada
    xml_info = urllib2.urlopen(url_info).read()
    id_token=re.findall(re.compile(ur'<link.*?="0".*?>([^<]+)'),xml_info)[0]
    '''
    EJEMPLO: 'http://www.mitele.es/programas-tv/sopa-de-gansos/temporada-1/sopa-de-gansos-instant-6/'
    <link end="0" start="0">
    /nogeo/ms/QQ/msQQlXWAy8yCPNjFJX6VA1/SqHWM8PTK4833tKHuC4az.1100.mp4
    </link>
    '''
    logger.info("[mitele.py] id_token=" + id_token );

    #Se obtiene el elemento json con la url del video
    json_url = urllib2.urlopen('http://token.mitele.es/?id=' + id_token).read()
    url = json_url[json_url.find('"tokenizedUrl":"') + 16:]
    url = url[:url.find('"')]
    url = url.replace("\\","")
    logger.info("[mitele.py] url=" + url )

    video_urls = []
    video_urls.append( [ "[mitele]" , url ] )

    for video_url in video_urls:
        logger.info("[mitele.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
