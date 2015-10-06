# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para powvideo
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config
from core import jsunpack

def test_video_exists( page_url ):
    logger.info("pelisalacarta.powvideo test_video_exists(page_url='%s')" % page_url)
    
    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.powvideo get_video_url(page_url='%s')" % page_url)

    # Lo pide una vez
    if not "embed" in page_url:
      page_url = page_url.replace("http://powvideo.net/","http://powvideo.net/embed-") + "-640x360.html"
      
    headers = [['User-Agent','Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.8.1.14) Gecko/20080404 Firefox/2.0.0.14'],['Referer',page_url]]
    page_url= page_url.replace("embed","iframe")
    
    data = scrapertools.cache_page( page_url , headers=headers )
    #logger.info("data="+data)
    
    #Quitado porque funciona mas rapido asi y no veo necesidad de esto:
    '''
    try:
        op = scrapertools.get_match(data,'<input type="hidden" name="op" value="(down[^"]+)"')
        usr_login = ""
        id = scrapertools.get_match(data,'<input type="hidden" name="id" value="([^"]+)"')
        fname = scrapertools.get_match(data,'<input type="hidden" name="fname" value="([^"]+)"')
        referer = scrapertools.get_match(data,'<input type="hidden" name="referer" value="([^"]*)"')
        hashvalue = scrapertools.get_match(data,'<input type="hidden" name="hash" value="([^"]*)"')
        submitbutton = scrapertools.get_match(data,'<input type="submit" name="imhuman" value="([^"]+)"').replace(" ","+")

        import time
        time.sleep(30)

        # Lo pide una segunda vez, como si hubieras hecho click en el banner
        #op=download1&usr_login=&id=auoxxtvyquoy&fname=Star.Trek.Into.Darkness.2013.HD.m720p.LAT.avi&referer=&hash=1624-83-46-1377796019-c2b422f91da55d12737567a14ea3dffe&imhuman=Continue+to+Video
        #op=search&usr_login=&id=auoxxtvyquoy&fname=Star.Trek.Into.Darkness.2013.HD.m720p.LAT.avi&referer=&hash=1624-83-46-1377796398-8020e5629f50ff2d7b7de99b55bdb177&imhuman=Continue+to+Video
        post = "op="+op+"&usr_login="+usr_login+"&id="+id+"&fname="+fname+"&referer="+referer+"&hash="+hashvalue+"&imhuman="+submitbutton
        headers.append(["Referer",page_url])
        data = scrapertools.cache_page( page_url , post=post, headers=headers )
        #logger.info("data="+data)
    except:
        import traceback
        traceback.print_exc()
    '''
    # Extrae la URL
    data = scrapertools.find_single_match(data,"<script type='text/javascript'>(.*?)</script>")
    data = jsunpack.unpack(data)

    data = scrapertools.find_single_match(data,"sources\=\[([^\]]+)\]")
    data = data.replace("\\","")

    '''
    {image:image,tracks:tracks,file:'rtmp://5.39.70.113:19350/vod/mp4:01/00219/dw5tbqp6dr3i_n?h=m4ohputqpiikkfn2mda7ymaimgo5n34f7uvpizy5vkjn7ifqrv6y2y6n5y',description:'dw5tbqp6dr3i'},
    {image:image,tracks:tracks,file:'http://powvideo.net/m4ohputqpiikkfn2mda7ymaimgo5n34f7uvpizy5vkjn7ifqrv6y2y6n5y.m3u8',description:'dw5tbqp6dr3i'},{image:image,tracks:tracks,file:'http://5.39.70.113:8777/m4ohputqpiikkfn2mda7ymaimgo5n34f7uvpizy5vkjn7ifqrv6y2y6n5y/v.mp4',description:'dw5tbqp6dr3i'}
    '''
    patron = "file:'([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)
    video_urls = []
    for match in matches:
        video_urls.append( [ scrapertools.get_filename_from_url(match)[-4:]+" [powvideo]",match])

    for video_url in video_urls:
        logger.info("[powvideo.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    # http://powvideo.net/embed-sbb9ptsfqca2
    patronvideos  = 'powvideo.net/embed-([a-z0-9]+)'
    logger.info("pelisalacarta.powvideo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[powvideo]"
        url = "http://powvideo.net/"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'powvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)

    # http://powvideo.net/auoxxtvyoy
    patronvideos  = 'powvideo.net/([a-z0-9]+)'
    logger.info("pelisalacarta.powvideo find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[powvideo]"
        url = "http://powvideo.net/"+match
        if url not in encontrados and match!="embed":
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'powvideo' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
    return devuelve

def test():
    video_urls = get_video_url("http://powvideo.net/auoxxtvyquoy")

    return len(video_urls)>0