# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Funciones para hacer canales a partir de un canal de YouTube
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
CHANNELNAME = "youtube_channel"

def isGeneric():
    return True

# Show all YouTube playlists for the selected channel
def playlists(item,channel_id):
    logger.info("youtube_channel.playlists ")
    itemlist=[]

    item.url = "http://gdata.youtube.com/feeds/api/users/"+channel_id+"/playlists?v=2&start-index=1&max-results=30"

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
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="videos" , url=url, thumbnail=thumbnail, plot=plot , folder=True) )
    return itemlist

# Show all YouTube videos for the selected playlist
def videos(item):
    logger.info("youtube_channel.videos ")
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
        plot = scrapertools.find_single_match(entry,"<summa[^>]+>([^<]+)</summa")
        thumbnail = scrapertools.find_single_match(entry,"<media\:thumbnail url='([^']+)'")
        video_id = scrapertools.find_single_match(entry,"http\://www.youtube.com/watch\?v\=([0-9A-Za-z_-]{11})")
        url = video_id

        # Appends a new item to the xbmc item list
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="play" , server="youtube", url=url, thumbnail=thumbnail, plot=plot , folder=False) )
    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test(channel_id="TelevisionCanaria"):

    # Si hay algún video en alguna de las listas de reproducción lo da por bueno
    playlist_items = playlists(Item(),channel_id)
    for playlist_item in playlist_items:
        items_videos = videos(playlist_item)
        if len(items_videos)>0:
            return True

    return False