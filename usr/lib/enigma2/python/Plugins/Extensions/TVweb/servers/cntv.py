# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para cntv
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import re, sys
import urlparse, urllib, urllib2

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="" , video_password="" ):
    logger.info("tvalacarta.servers.cntv get_video_url(page_url='%s')" % page_url)

    data = scrapertools.cache_page(page_url)
    video_id = scrapertools.find_single_match(data,'"videoCenterId","([a-z0-9]+)"')
    logger.info("tvalacarta.servers.cntv video_id="+video_id)

    # Formato noticias
    if video_id!="":
        metadata_url = "http://vdn.apps.cntv.cn/api/getHttpVideoInfo.do?pid="+video_id+"&tz=-1&from=000spanish&url="+page_url+"&idl=32&idlr=32&modifyed=false"
        data = scrapertools.cache_page(metadata_url)
        logger.info(data)
    
        video_url = scrapertools.find_single_match(data,'"hls_url"\:"([^"]+)"')
        logger.info("video_url="+video_url)
    
    # Formato programas
    else:
        video_id = scrapertools.find_single_match(data,'"videoCenterId","(.*?)"')
        video_url = "http://asp.v.cntv.cn/hls/"+matches[0]+"/main.m3u8"

    video_urls = []
    if video_url.endswith(".m3u8"):
        '''
        #EXT-X-STREAM-INF:PROGRAM-ID=1, BANDWIDTH=204800, RESOLUTION=240x180
        /asp/hls/200/0303000a/3/default/269599f209024eb482ac0b12b1861d31/200.m3u8
        '''
        data_calidades = scrapertools.cache_page(video_url)
        patron_calidades = "BANDWIDTH=(\d+), RESOLUTION=([a-z0-9]+)\s*(.*?.m3u8)"
        matches = re.compile(patron_calidades,re.DOTALL).findall(data_calidades)

        if len(matches)>0:
            for bitrate,resolucion,calidad_url in matches:
                esta_url = urlparse.urljoin(video_url,calidad_url)
                try:
                    kb = " "+str(int(bitrate)/1024)+"Kbps "
                except:
                    kb = ""
                video_urls.append([ resolucion + kb + '('+scrapertools.get_filename_from_url(esta_url)[-4:] + ') [cntv]' , esta_url])
        else:
            video_urls.append([ '('+scrapertools.get_filename_from_url(video_url)[-4:] + ') [cntv]' , video_url])

    else:
        video_urls.append([ '('+scrapertools.get_filename_from_url(video_url)[-4:] + ') [cntv]' , video_url])

    for video_url in video_urls:
        logger.info("tvalacarta.servers.cntv %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    logger.info("tvalacarta.servers.cntv find_videos")

    encontrados = set()
    devuelve = []

    return devuelve

def test():
    video_urls = get_video_url("http://espanol.cntv.cn/program/ArteCulinarioChino/20130806/102791.shtml")
    return len(video_urls)>0
