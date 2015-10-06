# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para vimple.ru
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Some code from youtube-dl project
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os
import base64
import xml.etree.ElementTree
import zlib

from core import scrapertools
from core import logger
from core import config

_VALID_URL = r'https?://(player.vimple.ru/iframe|vimple.ru)/(?P<id>[a-f0-9]{10,})'

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("pelisalacarta.servers.vimpleru page_url="+page_url)
	
    mobj = re.match(_VALID_URL, page_url)
    video_id = mobj.group('id')
    logger.info("pelisalacarta.servers.vimpleru video_id="+video_id)

    data = scrapertools.cache_page( page_url )
    logger.info("pelisalacarta.servers.vimpleru data="+data)

    cookie_data = config.get_cookie_data()
    #logger.info("pelisalacarta.servers.vimpleru cookie_data="+cookie_data)

    universalid = scrapertools.get_match(cookie_data,'UniversalUserID\s*([a-f0-9]+)')
    logger.info("universalid="+universalid)

    player_url = scrapertools.find_single_match(data,'"swfplayer"\:"([^"]+)"')
    player_url = player_url.replace("\\","")
    logger.info("pelisalacarta.servers.vimpleru player_url="+player_url)

    player = scrapertools.cache_page( player_url)
    #logger.info("pelisalacarta.servers.vimpleru player="+repr(player))

    player = zlib.decompress(player[8:])
    #logger.info("pelisalacarta.servers.vimpleru player="+repr(player))

    xml_pieces = re.findall(b'([a-zA-Z0-9 =+/]{500})', player)
    logger.info("pelisalacarta.servers.vimpleru xml_pieces="+repr(xml_pieces))
    xml_pieces = [piece[1:-1] for piece in xml_pieces]
    logger.info("pelisalacarta.servers.vimpleru xml_pieces="+repr(xml_pieces))

    xml_data = b''.join(xml_pieces)
    logger.info("pelisalacarta.servers.vimpleru xml_data="+repr(xml_data))
    xml_data = base64.b64decode(xml_data)
    logger.info("pelisalacarta.servers.vimpleru xml_data="+repr(xml_data))

    xml_data = xml.etree.ElementTree.fromstring(xml_data)
	
    video = xml_data.find('Video')
    quality = video.get('quality')
    q_tag = video.find(quality.capitalize())
    '''
    logger.info("pelisalacarta.servers.vimpleru url: " + q_tag.get('url'))
    logger.info("pelisalacarta.servers.vimpleru tbr: " +  q_tag.get('bitrate'))
    logger.info("pelisalacarta.servers.vimpleru filesize: " +  q_tag.get('filesize'))
    logger.info("pelisalacarta.servers.vimpleru format_id: " +  quality)
    logger.info("pelisalacarta.servers.vimpleru id: " +  video_id)
    logger.info("pelisalacarta.servers.vimpleru title: " +  video.find('Title').text)
    logger.info("pelisalacarta.servers.vimpleru thumbnail: " +  video.find('Poster').get('url'))
    logger.info("pelisalacarta.servers.vimpleru duration: " +  video.get('duration'))
    logger.info("pelisalacarta.servers.vimpleru webpage_url: " +  video.find('Share').get('videoPageUrl'))
    '''	
    media_url = q_tag.get('url')+"|Cookie=UniversalUserID="+universalid
    video_urls = []
    video_urls.append( [ scrapertools.get_filename_from_url(media_url)[-4:]+" [vimple.ru]",media_url])

    for video_url in video_urls:
        logger.info("pelisalacarta.servers.vimpleru %s - %s" % (video_url[0],video_url[1]))

    return video_urls


# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    devuelve = []

    # http://player.vimple.ru/iframe/3721fe74563a45c7a3fe1e6941e5cdc6
    patronvideos  = 'vimple.ru/iframe/([a-f0-9]+)'
    logger.info("pelisalacarta.vimple.ru find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[vimple.ru]"
        url = "http://player.vimple.ru/iframe/"+match
        logger.info("  url="+url)
        devuelve.append( [ titulo , url , 'vimpleru' ] )
        
    return devuelve
