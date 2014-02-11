# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para mega.co.nz
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def test_video_exists( page_url ):
    logger.info("[mega.py] test_video_exists(page_url='%s')" % page_url)
    
    #if "megacrypter.com" in page_url:
    #    return False,"Los enlaces protegidos con megacrypter.com<br/>no están soportados (todavía)."

    return True,""

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[mega.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    if not "megacrypter.com" in page_url:
        url_service2 = ""
        url_service1 = ""
        
        url_service1 = page_url
        if not url_service1.startswith("https://"):
            url_service1 = "https://mega.co.nz/" + url_service1

        title_for_mega = "Pelisalacarta%20video"
        
        url = "plugin://plugin.video.mega/?url="+page_url+"&action=stream"
        video_urls.append(["[mega add-on]",url])
        
    	#GENERA LIK MEGASTREAMER
        url_service1 = url_service1.replace("https://mega.co.nz/#!","http://megastreamer.net/mega_stream.php?url=https%3A%2F%2Fmega.co.nz%2F%23%21")
        url_service1 = url_service1.replace("!","%21")
        url_service1 = url_service1 + "&mime=vnd.divx"
        logger.info("[mega.py] megastreamer.net url="+url_service1)
        video_urls.append(["[megastreamer.net]",url_service1])

        #GENERA LINK MEGA-STREAM
        url_service2 = page_url.replace("https://mega.co.nz/#!","")
        url_service2 = url_service2.replace("!","&key=")
        url_service2 = "http://mega-stream.me/stream.php?ph="+url_service2
        logger.info("[mega.py] mega-stream url="+url_service2)
        video_urls.append(["[mega-stream.me]",url_service2])
    else:
        video_urls.append(["[megacrypter]",page_url])

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []
    
    #https://mega.co.nz/#!TNBl0CbR!S0GFTCVr-tM_cPsgkw8Y-0HxIAR-TI_clqys
    patronvideos  = '(mega.co.nz/\#\![A-Za-z0-9\-\_]+\![A-Za-z0-9\-\_]+)'
    logger.info("[mega.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        
        url = "https://"+match
        if url not in encontrados:
            logger.info(" url="+url)
			#GENERA LINK DE MEGA-STREAM PARA SABER EL TIPO DE FICHERO
            url_filetype = url.replace("!","%21")
            url_filetype = url_filetype.replace("/","%2F")
            url_filetype = url_filetype.replace(":","%3A")
            url_filetype = url_filetype.replace("#","%23")
            url_filetype = "http://mega-stream.me/?l="+url_filetype
            data_type = scrapertools.cache_page(url_filetype)
            patrontype  = '<title>MEGA-STREAM.ME -(.*?)</title>'
            matches_type = re.compile(patrontype,re.DOTALL).findall(data_type)
            if len(matches_type)>0:
               titulo = matches_type[0]
               titulo = titulo[-3:]+"]"+titulo
            
            devuelve.append( [ titulo , url , 'mega' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)    
    
    #http://megacrypter.com/!Ct72v-LoJ_LOdZtVwDOwq70La7A44OJ3PgB0d_YbWaoToZpkfGrd8lqceD8YKgqZRqCJlFKC-XbwMQl1VpcUmiQB0mTAH73mg4jb5E_X8JD_ByS68grzsl3uv3oTazxg!2e20cad2
    patronvideos  = '(megacrypter.com/\![A-Za-z0-9\-\_\!]+)'
    logger.info("[mega.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[megacrypter]"
        url = "http://"+match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'mega' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)    

    return devuelve