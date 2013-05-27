# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Giralda TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import os
import sys

import urlparse,re
import urllib
import datetime

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = True
CHANNELNAME = "giraldatv"

def isGeneric():
    return True

# Entry point
def mainlist(item):
    item.url = "http://gdata.youtube.com/feeds/api/users/giraldatv/playlists?v=2&start-index=1&max-results=30"
    return youtube_playlists(item)

# Show all YouTube playlists for the selected channel
def youtube_playlists(item):
    logger.info("giraldatv.youtube_playlists ")
    itemlist=[]

    # Fetch video list from YouTube feed
    data = scrapertools.cache_page( item.url )
    logger.info("data="+data)
    
    # Extract items from feed
    pattern = "<entry(.*?)</entry>"
    matches = re.compile(pattern,re.DOTALL).findall(data)
    
    for entry in matches:
        logger.info("entry="+entry)
        
        # Not the better way to parse XML, but clean and easy
        title = scrapertools.find_single_match(entry,"<titl[^>]+>([^<]+)</title>")
        plot = scrapertools.find_single_match(entry,"<media\:descriptio[^>]+>([^<]+)</media\:description>")
        thumbnail = scrapertools.find_single_match(entry,"<media\:thumbnail url='([^']+)'")
        url = scrapertools.find_single_match(entry,"<content type\='application/atom\+xml\;type\=feed' src='([^']+)'/>")

        # Appends a new item to the xbmc item list
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="youtube_videos" , url=url, thumbnail=thumbnail, plot=plot , folder=True) )
    return itemlist

# Show all YouTube videos for the selected playlist
def youtube_videos(item):
    logger.info("giraldatv.youtube_videos ")
    itemlist=[]

    # Fetch video list from YouTube feed
    data = scrapertools.cache_page( item.url )
    logger.info("data="+data)
    
    # Extract items from feed
    pattern = "<entry(.*?)</entry>"
    matches = re.compile(pattern,re.DOTALL).findall(data)
    
    for entry in matches:
        logger.info("entry="+entry)
        
        # Not the better way to parse XML, but clean and easy
        title = scrapertools.find_single_match(entry,"<titl[^>]+>([^<]+)</title>")
        title = title.replace("Disney Junior España | ","")
        plot = scrapertools.find_single_match(entry,"<summa[^>]+>([^<]+)</summa")
        thumbnail = scrapertools.find_single_match(entry,"<media\:thumbnail url='([^']+)'")
        video_id = scrapertools.find_single_match(entry,"http\://www.youtube.com/watch\?v\=([0-9A-Za-z_-]{11})")
        url = video_id

        # Appends a new item to the xbmc item list
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="youtube", url=url, thumbnail=thumbnail, plot=plot , folder=False) )
    return itemlist


# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    items_mainlist = mainlist(Item())
    
    items_programas = disneyweb(items_mainlist[0])
    if len(items_programas)==0:
        return False

    items_videos = play(items_programas[0])
    if len(items_videos)==0:
        return False

    for youtube_item in items_mainlist[1:]:
        items_videos = youtube_videos(youtube_item)
        if len(items_videos)==0:
            return False

    return bien