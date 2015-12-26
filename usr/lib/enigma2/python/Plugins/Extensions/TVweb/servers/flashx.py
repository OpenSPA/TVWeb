# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para flashx
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsunpack

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.flashx url="+page_url)

    # Lo pide una vez
    headers = [['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14']]
    data = scrapertools.cache_page( page_url , headers=headers )
    #logger.info("data="+data)
    
    form_url = scrapertools.get_match(data,"<Form method=\"POST\" action='([^']+)'>")
    logger.info("pelisalacarta.servers.flashx form_url="+form_url)
    form_url = urlparse.urljoin(page_url,form_url)
    logger.info("pelisalacarta.servers.flashx form_url="+form_url)

    op = scrapertools.get_match(data,'<input type="hidden" name="op" value="([^"]+)"')
    logger.info("pelisalacarta.servers.flashx op="+op)
    
    usr_login = ""
    
    id = scrapertools.get_match(data,'<input type="hidden" name="id" value="([^"]+)"')
    logger.info("pelisalacarta.servers.flashx id="+id)

    fname = scrapertools.get_match(data,'<input type="hidden" name="fname" value="([^"]+)"')
    logger.info("pelisalacarta.servers.flashx fname="+fname)
    
    referer = scrapertools.get_match(data,'<input type="hidden" name="referer" value="([^"]*)"')
    logger.info("pelisalacarta.servers.flashx referer="+referer)
    
    hashstring = scrapertools.get_match(data,'<input type="hidden" name="hash" value="([^"]*)"')
    logger.info("pelisalacarta.servers.flashx hashstring="+hashstring)
    
    imhuman = scrapertools.get_match(data,'<input type="submit".*?name="imhuman" value="([^"]+)"').replace(" ","+")
    logger.info("pelisalacarta.servers.flashx imhuman="+imhuman)
        
    import time
    time.sleep(10)

    # Lo pide una segunda vez, como si hubieras hecho click en el banner
    #op=download1&usr_login=&id=z3nnqbspjyne&fname=Coriolanus_DVDrip_Castellano_by_ARKONADA.avi&referer=&hash=nmnt74bh4dihf4zzkxfmw3ztykyfxb24&imhuman=Continue+to+Video
    #op=download1&usr_login=&id=h6gjvhiuqfsq&fname=GENES1S.avi&referer=&hash=taee4nbdgbuwuxfguju3t6nq2gkdzs6k&imhuman=Proceed+to+video
    #op=download1&usr_login=&id=vpkvjdpkh972&fname=G4ngm4n15HDRSub.avi&referer=&hash=1357853-176-86-1437560090-ee4170e4a4eca471524f6f07eca2b7a9&imhuman=Proceed+to+video
    post = "op="+op+"&usr_login="+usr_login+"&id="+id+"&fname="+fname+"&referer="+referer+"&hash="+hashstring+"&imhuman="+imhuman
    headers.append(["Referer",page_url])
    body = scrapertools.cache_page( form_url , post=post, headers=headers )
    logger.info("body="+body)

    data = scrapertools.find_single_match(body,"<script type='text/javascript'>(eval\(function\(p,a,c,k,e,d.*?)</script>")
    logger.info("data="+data)
    data = jsunpack.unpack(data)
    logger.info("data="+data)

    # Extrae la URL
    #{file:"http://f11-play.flashx.tv/luq4gfc7gxixexzw6v4lhz4xqslgqmqku7gxjf4bk43u4qvwzsadrjsozxoa/video1.mp4"}
    video_urls = []
    media_urls = scrapertools.find_multiple_matches(data,'\{file\:"([^"]+)"')
    for media_url in media_urls:

        if not media_url.endswith("png"):
            video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" [flashx]",media_url])

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.flashx %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):

    # Añade manualmente algunos erróneos para evitarlos
    encontrados = set()
    devuelve = []

    #http://www.flashx.tv/embed-li5ydvxhg514.html
    patronvideos  = 'flashx.tv/embed-([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.flashx find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[flashx]"
        url = "http://www.flashx.tv/"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'flashx' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    #http://flashx.tv/z3nnqbspjyne
    patronvideos  = 'flashx.tv/([a-z0-9A-Z]+)'
    logger.info("pelisalacarta.servers.flashx find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[flashx]"
        url = "http://www.flashx.tv/"+match+".html"
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'flashx' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    return devuelve

def test():

    video_urls = get_video_url("http://www.flashx.tv/vpkvjdpkh972.html")

    return len(video_urls)>0