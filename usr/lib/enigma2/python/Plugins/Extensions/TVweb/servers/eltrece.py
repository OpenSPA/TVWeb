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

    #http://www.eltrecetv.com.ar/cqc-2013/21-de-enero-cqc_066584
    '''
    iMac-de-Jesus:rtmpdump $ ./rtmpdump-2.4 -r "rtmp://10.vod.eltrecetv.com.ar/vod/13tv" --playpath "mp4:13tv/2014/01/22/CQC-210114-360.mp4" --app "vod/13tv" --swfUrl "http://static.eltrecetv.com.ar/sites/all/libraries/jwplayer/player-licensed.swf" --pageUrl "http://www.eltrecetv.com.ar/cqc-2013/21-de-enero-cqc_066584" -o out.mp4
    '''
    data = scrapertools.cache_page(page_url)

    '''
    <div id="video-b905578722aaa39b7d6481976f5af95c" class="video-eltrece"  data-levels='[{"bitrate":"600","file":"13tv\/2012\/12\/15\/Sos_Mi_H_14-12-12M500.mp4","width":"564"},{"bitrate":"1300","file":"13tv\/2012\/12\/15\/Sos_Mi_H_14-12-12M720.mp4","width":"564"}]' data-mobile='13tv/2012/12/15/Sos_Mi_H_14-12-12M240.mp4' data-autoplay="false" data-type="rtmp" data-image="http://cdn.eltrecetv.com.ar/sites/default/files/styles/564x317/public/showmatch_15_.jpg" width="564" height="317" data-width="564" data-height="317"><img typeof="foaf:Image" src="http://cdn.eltrecetv.com.ar/sites/default/files/styles/564x317/public/showmatch_15_.jpg" width="564" height="317" alt="" title="" /></div>
    '''

    video_urls = []

    fullurl = "rtmp://10.vod.eltrecetv.com.ar/vod/13tv"
    app = "vod/13tv"
    swfurl = "http://static.eltrecetv.com.ar/sites/all/libraries/jwplayer/player-licensed.swf"

    data_mobile = scrapertools.get_match(data,"data-mobile\='([^']+)'")
    logger.info("data_mobile="+data_mobile)
    playpath = "mp4:"+data_mobile
    url = fullurl + " app=" + app + " swfUrl=" + swfurl + " playpath=" + playpath + " pageUrl="+page_url
    extension = "rtmp"
    video_urls.append( [ extension+" (para móviles) [eltrece]" , url ] )

    data_level = scrapertools.get_match(data,"data-levels\='(.*?)'")
    data_level = data_level.replace("\\","")
    logger.info("data_level="+data_level)
    patron = '"bitrate"\:"(\d+)","file"\:"([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data_level)

    for bitrate,fileurl in matches:
        logger.info("bitrate="+bitrate+", url="+fileurl)
        playpath = "mp4:"+fileurl
        url = fullurl + " app=" + app + " swfUrl=" + swfurl + " playpath=" + playpath + " pageUrl="+page_url
        extension = "rtmp"
        
        video_urls.append( [ extension+" ("+bitrate+" Kbps) [eltrece]" , url ] )

    for video_url in video_urls:
        logger.info("[eltrece.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve

