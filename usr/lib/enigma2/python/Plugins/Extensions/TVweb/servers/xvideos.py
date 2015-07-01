# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para xvideos
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
from core import logger
from core import scrapertools

def get_video_url(page_url, video_password):
    video_urls = []
    data = scrapertools.downloadpage(page_url)
    patronurl = "flv_url=([^&]+)&"
    matches = re.compile(patronurl,re.DOTALL).findall(data)
    if len(matches)>0:
      video_urls.append( ["xvideos",urllib.unquote_plus(matches[0])])
    return video_urls
    
def find_videos(data):
    devuelve = []
    patronvideos  = 'src="http://flashservice.xvideos.com/embedframe/([0-9]+)" '
    logger.info("[xvideos.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    for match in matches:
        url = "http://www.xvideos.com/video"+match
        titulo = "[xvideos]"
        devuelve.append( [ titulo , url , 'xvideos'] )
    return devuelve