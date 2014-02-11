# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para TV3
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("[tv3.py] get_video_url(page_url='%s')" % page_url)

    video_urls = []
    try:
        # --------------------------------------------------------
        # Saca el codigo de la URL y descarga
        # --------------------------------------------------------
        patron = "/videos/(\d+)/"
        matches = re.compile(patron,re.DOTALL).findall(page_url)
        scrapertools.printMatches(matches)
        codigo = matches[0]
    
        # Prueba con el modo 1
        url = geturl4(codigo)
        if url=="" or url == None:
            url = geturl3(codigo)
        if url=="" or url == None:
            url = geturl1(codigo)
        if url=="" or url == None:
            url = geturl2(codigo)
        
        if url=="" or url == None:
            return []
        
        if url.startswith("http"):
            video_urls.append( [ "HTTP [tv3]" , url ] )
        else:
            #url = "rtmp://mp4-500-str.tv3.cat/ondemand/mp4:g/tvcatalunya/3/1/1269579524113.mp4"
            patron = "rtmp\:\/\/([^\/]+)\/ondemand\/mp4\:(g\/.*?mp4)"
            matches = re.compile(patron,re.DOTALL).findall(url)
            media = matches[0][1]
            
            videourl = "http://mp4-medium-dwn.media.tv3.cat/" + media
            video_urls.append( [ "HTTP [tv3]" , videourl ] )
    except:  
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line ) 
                
    for video_url in video_urls:
        logger.info("[tv3.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

def geturl1(codigo):
    #http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID=1594629&QUALITY=H&FORMAT=FLVGES&RP=www.tv3.cat&rnd=796474
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=FLV&rnd=481353"
    logger.info("[tv3.py] geturl1 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
        url = matches[0]
        url = url.replace('rtmp://flv-500-str.tv3.cat/ondemand/g/','http://flv-500.tv3.cat/g/')
    return url

def geturl2(codigo):
    #http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID=1594629&QUALITY=H&FORMAT=FLVGES&RP=www.tv3.cat&rnd=796474
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=FLVGES&RP=www.tv3.cat&rnd=796474"
    logger.info("[tv3.py] geturl2 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
        url = matches[0]
        url = url.replace('rtmp://flv-es-500-str.tv3.cat/ondemand/g/','http://flv-500-es.tv3.cat/g/')
    return url

def geturl3(codigo):
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=MP4"
    logger.info("[tv3.py] geturl3 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
        url = matches[0]
        #url = url.replace('rtmp://flv-es-500-str.tv3.cat/ondemand/g/','http://flv-500-es.tv3.cat/g/')
    return url

def geturl4(codigo):
    dataurl = "http://www.tv3.cat/su/tvc/tvcConditionalAccess.jsp?ID="+codigo+"&QUALITY=H&FORMAT=MP4GES&RP=www.tv3.cat"
    logger.info("[tv3.py] geturl4 dataurl="+dataurl)
        
    data = scrapertools.cachePage(dataurl)
    
    patron = "(rtmp://[^\?]+)\?"
    matches = re.compile(patron,re.DOTALL).findall(data)
    url = ""
    if len(matches)>0:
        url = matches[0]
        #url = url.replace('rtmp://flv-es-500-str.tv3.cat/ondemand/g/','http://flv-500-es.tv3.cat/g/')
    return url

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '(http://www.crtv3.es/tv3/a-carta/([a-z0-9\-]+)'
    logger.info("[tv3.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[tv3]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'tv3' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve

