# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para eltrece
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("[eltrece.py] get_video_url(page_url='%s')" % page_url)

    #http://www.eltrecetv.com.ar/los-%C3%BAnicos/los-%C3%BAnicos-2012/00052062/cap%C3%ADtulo-28-los-%C3%BAnicos
    data = scrapertools.cache_page(page_url)

    '''
    <div id="video-b905578722aaa39b7d6481976f5af95c" class="video-eltrece"  data-levels='[{"bitrate":"600","file":"13tv\/2012\/12\/15\/Sos_Mi_H_14-12-12M500.mp4","width":"564"},{"bitrate":"1300","file":"13tv\/2012\/12\/15\/Sos_Mi_H_14-12-12M720.mp4","width":"564"}]' data-mobile='13tv/2012/12/15/Sos_Mi_H_14-12-12M240.mp4' data-autoplay="false" data-type="rtmp" data-image="http://cdn.eltrecetv.com.ar/sites/default/files/styles/564x317/public/showmatch_15_.jpg" width="564" height="317" data-width="564" data-height="317"><img typeof="foaf:Image" src="http://cdn.eltrecetv.com.ar/sites/default/files/styles/564x317/public/showmatch_15_.jpg" width="564" height="317" alt="" title="" /></div>
    '''

    video_urls = []

    data_mobile = scrapertools.get_match(data,"data-mobile\='13tv/([^']+)'")
    logger.info("data_mobile="+data_mobile)
    url = "http://ctv.eltrecetv.com.ar/"+data_mobile
    extension = scrapertools.get_filename_from_url(url)[-4:]
    
    video_urls.append( [ extension+" (para móviles) [eltrece]" , url ] )

    data_level = scrapertools.get_match(data,"data-levels\='(.*?)'")
    data_level = data_level.replace("\\","")
    logger.info("data_level="+data_level)
    patron = '"bitrate"\:"(\d+)","file"\:"13tv/([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data_level)

    for bitrate,fileurl in matches:
        logger.info("bitrate="+bitrate+", url="+fileurl)
        url = "http://ctv.eltrecetv.com.ar/"+fileurl
        extension = scrapertools.get_filename_from_url(url)[-4:]
        
        video_urls.append( [ extension+" ("+bitrate+" Kbps) [eltrece]" , url ] )

    for video_url in video_urls:
        logger.info("[eltrece.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

