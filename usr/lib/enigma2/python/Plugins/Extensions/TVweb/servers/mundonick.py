# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para MundoNick
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[mundonick.py] get_video_url(page_url='%s')" % page_url)
    
    data = scrapertools.cachePage(page_url)

    #logger.info(data)
    '''
    if data.find('video/x-flv')<0:
        finalurl=re.compile('<src>(.+?)</src>\n</rendition>\n<rendition cdn=".+?" duration=".+?" bitrate=".+?" width=".+?" height=".+?"\ntype="video/mp4">').findall(data)[-1]
        logger.info("finalurl: " + finalurl)
    else:
        swap=re.compile('<src>(.+?)</src>\n</rendition>\n<rendition cdn=".+?" duration=".+?" bitrate=".+?" width=".+?" height=".+?"\ntype="video/x-flv">').findall(data)
        if not swap: swap=re.compile('<src>(.+?)</src>').findall(data)
        logger.info("swap: " + swap[0])
    '''
    video_urls = []

    import xml.etree.ElementTree as xmlet
    root = xmlet.fromstring(data)
    swfUrl = 'http://media.mtvnservices.com/player/release/?v=3.16.2&geo=VE'

    for rendition in root.findall('.//rendition'):
        src        = rendition.find('src').text
        #duration  = int(rendition.get('duration')) / 60
        #width     = rendition.get('width')
        #height    = rendition.get('height')    
        type       = rendition.get('type').split("/")[1]
        resolution = rendition.get('width') + 'x' + rendition.get('height')        
        #bitrate   = rendition.get('bitrate')
        
        if type.startswith("x-"):
            type = type[2:]
        type = type.upper()
            
        label = " (%s a %s) [mundonick]" % (type,resolution)
        logger.info("label: " + label)
		
        video = src + " swfurl=" + swfUrl + " swfvfy=true"
       
        video_urls.append( [ label , video  ])
        
    for video_url in video_urls:
        logger.info(str(video_url))

    return video_urls