# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para mail.ru
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsontools

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[mailru.py] get_video_url(page_url='%s')" % (page_url))

    video_urls = []

    ## Carga la página
    ## Nueva url al final de los datos
    data = scrapertools.cache_page(page_url)

    ## Carga los nuevos datos de la nueva url
    #<a href="http://r.mail.ru/clb15944866/my.mail.ru/mail/gottsu04/video/_myvideo/709.html?from=watchonmailru" class="b-player__button" target="_blank">Watch video</a>
    url = scrapertools.get_match(data,'<a href="([^"]+)" class="b-player__button" target="_blank">Watch video</a>')
    data = scrapertools.cache_page(url)

    ## API ##
    ## Se necesita la id del vídeo para formar la url de la API
    #<link rel="image_src" href="http://filed9-14.my.mail.ru/pic?url=http%3A%2F%2Fvideoapi.my.mail.ru%2Ffile%2Fsc03%2F3450622080461046469&mw=&mh=&sig=5d50e747aa59107d805263043e3efe64" />
    id_api_video = scrapertools.get_match(data,'sc\d+%2F([^&]+)&mw')
    url = "http://videoapi.my.mail.ru/videos/" + id_api_video + ".json"
    ## Carga los datos y los headers
    data, headers = scrapertools.read_body_and_headers(url)
    data = jsontools.load_json( data )

    ## La cookie video_key necesaria para poder visonar el video
    for cookie in headers:
        if 'set-cookie' in cookie: break
    cookie_video_key = scrapertools.get_match(cookie[1], '(video_key=[a-f0-9]+)')

    ## Formar url del video + cookie video_key
    media_url = data['videos'][0]['url'] + "|Cookie=" + cookie_video_key

    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:] + " [mail.ru]", media_url ] )

    for video_url in video_urls:
        logger.info("[mail.ru] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    logger.info("[mailru.py] find_videos") #(data='%s')" % (data))
    encontrados = set()
    devuelve = []

    # http://videoapi.my.mail.ru/videos/embed/mail/bartos1100/_myvideo/1136.html
    patronvideos  = 'videoapi.my.mail.ru/videos/embed/mail/([a-zA-Z0-9]+)/_myvideo/(\d+).html'
    logger.info("[mailru.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[mail.ru]"
        url = "http://videoapi.my.mail.ru/videos/embed/mail/"+match[0]+"/_myvideo/"+match[1]+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'mailru' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve
