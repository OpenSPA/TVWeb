# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para pelis24
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "pelis24"
__category__ = "F,S"
__type__ = "xbmc"
__title__ = "Pelis24"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[pelis24.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Novedades"     , action="peliculas", url="http://pelis24.com/index.php"))
    itemlist.append( Item(channel=__channel__, title="Estrenos" , action="peliculas", url="http://pelis24.com/estrenos/"))
    itemlist.append( Item(channel=__channel__, title="Recientes" , action="peliculas", url="http://pelis24.com/index.php?do=lastnews"))
    itemlist.append( Item(channel=__channel__, title="HD 720p" , action="peliculas", url="http://pelis24.com/hd/"))
    itemlist.append( Item(channel=__channel__, title="HD 480p" , action="peliculas", url="http://pelis24.com/peliculas480p/"))
    itemlist.append( Item(channel=__channel__, title="Peliculas en Castellano" , action="peliculas", url="http://pelis24.com/pelicula-ca/"))
    itemlist.append( Item(channel=__channel__, title="Peliculas 3D" , action="peliculas", url="http://pelis24.com/pelicula-3d"))
    return itemlist

def peliculas(item):
    logger.info("[pelis24.py] peliculas")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    
    bloque = scrapertools.get_match(data,"<div id='dle-content'>(.*?<span class=\"thide pnext\">Siguiente</span></a>)")
    #<a href="http://www.pelis24.com/peliculas/11010-fast-furious-5-a-todo-gas-5-espanol-online.html">
    #<img style="display:none;visibility:hidden;" data-cfsrc="http://imgs24.com/images/l15963435d.jpg" width="145" height="211" alt="Rápidos y furiosos 5 / A todo gas 5 (2011)" title="Rápidos y furiosos 5 / A todo gas 5 (2011)"/>
    #<noscript><img src="http://imgs24.com/images/l15963435d.jpg" width="145" height="211" alt="Rápidos y furiosos 5 / A todo gas 5 (2011)" title="Rápidos y furiosos 5 / A todo gas 5 (2011)"/></noscript></a>&nbsp;&nbsp;

    patron = '<a href="([^"]+)"[^<]+<img[^<]+<noscript[^<]+<img src="([^"]+)" width="[^"]+" height="[^"]+" alt="[^"]+" title="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        scrapedplot = ""
        title = unicode( scrapedtitle, "iso-8859-1" , errors="replace" ).encode("utf-8")

        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )


    # Extrae el paginador
    patronvideos  = '<a href="([^"]+)"><span class="thide pnext">Siguiente</span></a>'
    
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title="Página siguiente >>" , url=scrapedurl , folder=True) )

    return itemlist


# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    novedades_items = peliculas(mainlist_items[0])
    bien = False
    for novedades_item in novedades_items:
        mirrors = servertools.find_video_items( item=novedades_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien
