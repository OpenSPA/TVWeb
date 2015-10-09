# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para serviporno
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "serviporno"
__category__ = "F"
__type__ = "generic"
__title__ = "serviporno"
__language__ = "ES"
__adult__ = "true"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[serviporno.py] mainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, action="videos"      , title="Útimos videos" , url="http://www.serviporno.com/"))
    itemlist.append( Item(channel=__channel__, action="videos"      , title="Más vistos"    , url="http://www.serviporno.com/mas-vistos/"))
    itemlist.append( Item(channel=__channel__, action="videos"      , title="Más votados"   , url="http://www.serviporno.com/mas-votados/"))
    itemlist.append( Item(channel=__channel__, action="categorias"  , title="Categorias"    , url="http://www.serviporno.com/categorias/"))
    itemlist.append( Item(channel=__channel__, action="chicas"      , title="Chicas"        , url="http://www.serviporno.com/pornstars/"))
    itemlist.append( Item(channel=__channel__, action="tags"        , title="Tags"          , url="http://www.serviporno.com/tags/"))
    itemlist.append( Item(channel=__channel__, action="search"      , title="Buscar"        , url="http://www.serviporno.com/search/?q="))
    return itemlist

def search(item,texto):
    logger.info("[serviporno.py] search")
    texto = texto.replace(" ", "+")
    item.url = item.url + texto
    return videos(item)

def videos(item):
    logger.info("[serviporno.py] videos")
    itemlist = []
    data = scrapertools.downloadpage(item.url)
    patron = '<a href="([^"]+)">[^<]{1}<img src="([^"]+)" data-src="[^"]+" alt="[^"]+" id=\'[^"]+\' class="thumbs-changer" data-thumbs-prefix="[^"]+" height="150px" width="175px" border=0 />[^<]{1}</a>[^<]{1}<h4><a href="[^"]+">([^"]+)</a></h4>[^<]{1}'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,thumbnail, title  in matches:
        url = urlparse.urljoin( "http://www.serviporno.com" , url )
        plot=""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")            
        itemlist.append( Item(channel=__channel__, action='play', title=title , url=url , thumbnail=thumbnail , plot=plot) )
        
    #Paginador
    patron = '<a href="([^<]+)">Siguiente &raquo;</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)  
    if len(matches) >0:
      url = "http://www.serviporno.com"+matches[0]
      itemlist.append( Item(channel=__channel__, action="videos", title="Página Siguiente" , url=url , thumbnail="" , folder=True) )
      
    return itemlist

def chicas(item):
    logger.info("[serviporno.py] chicas")
    itemlist = []
    data = scrapertools.downloadpage(item.url)
    patron ='<div class="box-chica">[^<]{1}<a href="([^"]+)" title="">[^<]{1}<img class="img" src=\'([^"]+)\' width="175" height="150" border=\'0\' alt="[^"]+"/>[^<]{1}</a>[^<]{1}<h4><a href="[^"]+" title="">([^"]+)</a></h4>[^<]{1}<div class="vistas"><small class="sprite ico-vistas"></small>[^"]+</div>[^<]{1}<a class="total-videos" href="[^"]+" title="">([^"]+)</a>[^<]{1}<div class="clear"></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,thumbnail, title, videos  in matches:
        url = urlparse.urljoin( "http://www.serviporno.com" , url )
        title = title +" ("+videos+")"
        itemlist.append( Item(channel=__channel__, action='videos', title=title , url=url , thumbnail=thumbnail , plot="") )
    return itemlist
    
def tags(item):
    logger.info("[serviporno.py] tags")
    itemlist = []
    data = scrapertools.downloadpage(item.url)
    patron ='<li>[^<]{1}<small class="ico-tag-small sprite"></small>[^<]{1}<a href="([^"]+)" title="[^"]+">([^"]+)</a>[^<]{1}</li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,title in matches:
        url = urlparse.urljoin( "http://www.serviporno.com" , url )
        itemlist.append( Item(channel=__channel__, action='videos', title=title , url=url , thumbnail="" , plot="") )
    return itemlist
    
def categorias(item):
    logger.info("[serviporno.py] categorias")
    itemlist = []
    data = scrapertools.downloadpage(item.url)
    patron = '<div class="box-escena">[^<]{1}<a href="([^"]+)"><img src="([^"]+)" alt="Webcam" height="150" width="175" border=0 /></a>[^<]{1}<h4><a href="[^"]+">([^"]+)</a></h4>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for url,thumbnail, title  in matches:
        url = urlparse.urljoin( "http://www.serviporno.com" , url )
        itemlist.append( Item(channel=__channel__, action='videos', title=title , url=url , thumbnail=thumbnail , plot="") )
    return itemlist

def play(item):
    logger.info("[serviporno.py] play")
    itemlist=[]
    data = scrapertools.downloadpage(item.url)
    url= scrapertools.get_match(data,'},[^<]{21}{[^<]{25}url: \'([^"]+)\',[^<]{25}framesURL:' )
    itemlist.append( Item(channel=__channel__, action="play", server="directo", title=item.title , url=url , thumbnail=item.thumbnail , plot=item.plot , folder=False) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True

    # mainlist
    mainlist_itemlist = mainlist(Item())
    video_itemlist = videos(mainlist_itemlist[0])
    
    # Si algún video es reproducible, el canal funciona
    for video_item in video_itemlist:
        play_itemlist = play(video_item)

        if len(play_itemlist)>0:
            return True

    return False