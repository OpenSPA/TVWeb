# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para dibujos.tv
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[dibujostv.py] get_video_url(page_url='%s')" % page_url)
    
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:11.0) Gecko/20100101 Firefox/11.0"
    REFERER = ""
    
    # Descarga la página
    # http://series.dibujos.tv/monster-high/01-el-canto-del-lobo-288.html
    headers = []
    headers.append([ "User-Agent",USER_AGENT ])
    data = scrapertools.cache_page(page_url , headers=headers)
    #logger.info("data="+data)

    '''
    var idv = "288";var width = "590";var height = "333";var rnd = (new String(Math.random())).substring(2,8) + (((new Date()).getTime()) & 262143);document.write('<scri' + 'pt language="JavaScript1.1" type="text/javascript" src="http://www.dibujos.tv/embed/?rnd='+rnd +'&idv='+idv+'&width='+width+'&height='+height+'&userid=">
    '''
    patron = 'var idv = "([^"]+)";var width = "([^"]+)";var height = "([^"]+)"'
    matches = re.findall(patron,data,re.DOTALL)
    if len(matches)==0:
        return []

    id_video = matches[0][0]
    width = matches[0][1]
    height = matches[0][2]
    import random
    aleatorio = random.randrange(100000000000, 999999999999)

    # Descarga el embed
    # http://www.dibujos.tv/embed/?rnd=420932199606&idv=288&width=590&height=333&userid=
    url = "http://www.dibujos.tv/embed/?rnd="+str(aleatorio)+"&idv="+id_video+"&width="+width+"&height="+height+"&userid="
    #url = "http://www.dibujos.tv/embed/?rnd=010383106912&idv=288&width=590&height=333&userid="
    headers.append([ "Referer",page_url ])
    data = scrapertools.cache_page(url,headers=headers)
    logger.info("data="+data)
    '''
    <param name="movie" value="http://www.dibujos.tv/swf/embed_mt.swf?ruta=http://www.dibujos.tv/xmlv2/embed.php?id=288|capt1_590_333.jpg|590|333|1|||0|&rnd=82880">
    document.write('<param name="movie" value="http://www.dibujos.tv/swf/embed_mt.swf?ruta=http://www.dibujos.tv/xmlv2/embed.php?id=288|capt1_590_333.jpg|590|333|1|||0|&rnd=82880">');
    document.write('<param name="allowScriptAccess" value="always" />');
    document.write('<param name="allowDomain" value="always" />');
    document.write('<param name="allowFullScreen" value="true" />');
    document.write('<param name="wmode" value="transparent" />');
    document.write('<embed name="player_flash" src="http://www.dibujos.tv/swf/embed_mt.swf?ruta=http://www.dibujos.tv/xmlv2/embed.php?id=288|capt1_590_333.jpg|590|333|1|||0|&rnd=126191" width="590" height="333"
    '''
    patron = '"http://www.dibujos.tv/swf/embed_mt.swf\?ruta\=([^"]+)"'
    matches = re.findall(patron,data,re.DOTALL)
    if len(matches)==0:
        return []
    
    url = matches[0]

    #http://www.dibujos.tv/xmlv2/embed.php?id=288|capt1_590_333.jpg|590|333|1|||0|&rnd=126191
    data = scrapertools.cache_page(url)
    logger.info("data="+data)
    patron = '<url_video><\!\[CDATA\[([^\]]+)\]\]></url_video>'
    matches = re.findall(patron,data,re.DOTALL)
    if len(matches)==0:
        return []
    
    url = matches[0]
    logger.info("url="+url)

    video_urls = []
    video_urls.append( [ "" , url ] )

    for video_url in video_urls:
        logger.info("[dibujostv.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '(http://series.dibujos.tv/.*?.html)'
    logger.info("[dibujostv.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[dibujostv]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'dibujostv' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve

