# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para yaske-netutv, netutv, hqqtv waawtv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os
import base64

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[netutv.py] url="+page_url)

    headers = [ ['User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0'] ]

    ## "/netu/tv/"
    if "www.yaske.net" in page_url:


        ## Encode a la url para pasarla como valor de parámetro
        urlEncode = urllib.quote_plus(page_url)

        ## Carga los datos
        id_video = scrapertools.get_match( page_url , "embed_([A-Za-z0-9]+)")
        data = scrapertools.cache_page( page_url , headers=headers )

        headers.append(['Referer', page_url])
        try:
            ## Nueva id del video
            page_url_the_new_video_id = scrapertools.get_match( data , 'script src="([^"]+)"></script>')
            data_with_new_video_id = scrapertools.cache_page( page_url_the_new_video_id , headers=headers )

            ## Algunos enlaces necesitan el paso pervio de la siguiente línea para coseguir la id
            data_with_new_video_id = urllib.unquote( data_with_new_video_id )
            new_id_video = scrapertools.get_match( data_with_new_video_id , "var vid='([^']+)';")

            ## Petición a hqq.tv con la nueva id de vídeo
            b64_data = get_b64_data(new_id_video, headers)

            ## Doble decode y escape
            utf8 = double_b64(b64_data)
        except:
            ## Recoge los datos
            b64_data = scrapertools.get_match( data , '<script language="javascript" type="text/javascript" src="data:text/javascript;charset=utf-8;base64,([^"]+)"></script>')

            ## Doble decode y escape
            utf8 = double_b64(b64_data)

            ## Nueva id del video
            new_id_video = scrapertools.get_match( utf8 , 'value="([^"]+)"')

            ## Petición a hqq.tv con la nueva id de vídeo y recoger los datos 
            b64_data = get_b64_data(new_id_video, headers)

            ## Doble decode y escape
            utf8 = double_b64(b64_data)

        ### at ###
        match_at = '<input name="at" id="text" value="([^"]+)">'
        at = scrapertools.get_match(utf8, match_at)

        ### m3u8 ###
        ## Recoger los bytes ofuscados que contiene la url del m3u8
        b_m3u8_2 = get_obfuscated( new_id_video, at, urlEncode, headers )

        ### tb_m3u8 ###
        ## Obtener la url del m3u8
        url_m3u8 = tb(b_m3u8_2)
    else:
        ## Encode a la url para pasarla como valor de parámetro con hqq como host
        urlEncode = urllib.quote_plus( page_url.replace("netu","hqq") )

        ### at ###
        id_video = page_url.split("=")[1]

        ## Petición a hqq.tv con la nueva id de vídeo y recoger los datos 
        b64_data = get_b64_data(id_video, headers)

        ## Doble decode y escape
        utf8 = double_b64(b64_data)

        match_at = '<input name="at" id="text" value="([^"]+)">'
        at = scrapertools.get_match(utf8, match_at)

        ### b_m3u8 ###
        headers.append(['Referer', page_url])

        ## Recoger los bytes ofuscados que contiene la url del m3u8
        b_m3u8_2 = get_obfuscated( id_video, at, urlEncode, headers )

        ### tb ###
        ## Obtener la url del m3u8
        url_m3u8 = tb(b_m3u8_2)

    ### m3u8 ###
    media_url = url_m3u8

    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" [netu.tv]",media_url])

    for video_url in video_urls:
        logger.info("[netutv.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

## Encuentra vídeos del servidor en el texto pasado
def find_videos(data):

    encontrados = set()
    devuelve = []

    ## Patrones
    # http://www.yaske.net/archivos/netu/tv/embed_54b15d2d41641.html
    # http://www.yaske.net/archivos/netu/tv/embed_54b15d2d41641.html?1
    # http://hqq.tv/player/embed_player.php?vid=498OYGN19D65&autoplay=no
    # http://hqq.tv/watch_video.php?v=498OYGN19D65
    # http://netu.tv/player/embed_player.php?vid=82U4BRSOB4UU&autoplay=no
    # http://netu.tv/watch_video.php?v=96WDAAA71A8K
    # http://waaw.tv/player/embed_player.php?vid=82U4BRSOB4UU&autoplay=no
    # http://waaw.tv/watch_video.php?v=96WDAAA71A8K
    patterns = [
        '/netu/tv/embed_(.*?$)',
        'hqq.tv/[^=]+=([A-Z0-9]+)',
        'netu.tv/[^=]+=([A-Z0-9]+)',
        'waaw.tv/[^=]+=([A-Z0-9]+)',
        'netu.php\?nt=([A-Z0-9]+)'
    ]

    if '/netu/tv/embed_' in data:
        url = "http://www.yaske.net/archivos/netu/tv/embed_%s"
    else:
        url = "http://netu.tv/watch_video.php?v=%s"

    for pattern in patterns:

        logger.info("[netutv.py] find_videos #"+pattern+"#")
        matches = re.compile(pattern,re.DOTALL).findall(data)

        for match in matches:
            titulo = "[netu.tv]"
            url = url % match
            if url not in encontrados:
                logger.info("  url="+url)
                devuelve.append( [ titulo , url , 'netutv' ] )
                encontrados.add(url)
            else:
                logger.info("  url duplicada="+url)

    return devuelve

def test():

    #http://www.peliculasid.net/player/netu.php?id=NA44292KD53O
    video_urls = get_video_url("http://netu.tv/watch_video.php?v=NA44292KD53O")

    return len(video_urls)>0

## --------------------------------------------------------------------------------
## --------------------------------------------------------------------------------

## Decode
def b64(text, inverse=False):
    if inverse:
        text = text[::-1]
    return base64.decodestring(text)

## Petición a hqq.tv con la nueva id de vídeo
def get_b64_data(new_id_video, headers):
    page_url_hqq = "http://hqq.tv/player/embed_player.php?vid="+new_id_video+"&autoplay=no"
    data_page_url_hqq = scrapertools.cache_page( page_url_hqq , headers=headers )
    b64_data = scrapertools.get_match(data_page_url_hqq, 'base64,([^"]+)"')
    return b64_data

## Doble decode y unicode-escape
def double_b64(b64_data):
    b64_data_inverse = b64(b64_data)
    b64_data_2 = scrapertools.get_match(b64_data_inverse, "='([^']+)';")

    utf8_data_encode = b64(b64_data_2,True)
    utf8_encode = scrapertools.get_match(utf8_data_encode, "='([^']+)';")

    utf8_decode = utf8_encode.replace("%","\\").decode('unicode-escape')
    return utf8_decode

## Recoger los bytes ofuscados que contiene el m3u8
def get_obfuscated(id_video, at, urlEncode, headers):
    url = "http://hqq.tv/sec/player/embed_player.php?vid="+id_video+"&at="+at+"&autoplayed=yes&referer=on&http_referer="+urlEncode+"&pass="
    data = scrapertools.cache_page( url, headers=headers )

    match_b_m3u8_1 = '</div>.*?<script>document.write[^"]+"([^"]+)"'
    b_m3u8_1 = urllib.unquote( scrapertools.get_match(data, match_b_m3u8_1) )

    if b_m3u8_1 == "undefined": b_m3u8_1 = urllib.unquote( data )

    match_b_m3u8_2 = '"#([^"]+)"'
    b_m3u8_2 = scrapertools.get_match(b_m3u8_1, match_b_m3u8_2)

    return b_m3u8_2

## Obtener la url del m3u8
def tb(b_m3u8_2):
    j = 0
    s2 = ""
    while j < len(b_m3u8_2):
        s2+= "\\u0"+b_m3u8_2[j:(j+3)]
        j+= 3

    return s2.decode('unicode-escape').encode('ASCII', 'ignore')

## --------------------------------------------------------------------------------
## --------------------------------------------------------------------------------
