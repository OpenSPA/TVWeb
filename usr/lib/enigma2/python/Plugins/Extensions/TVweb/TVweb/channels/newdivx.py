# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para newdivx.net by Bandavi
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "newdivx"
__category__ = "F,D"
__type__ = "generic"
__title__ = "NewDivx"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[newdivx.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Novedades", action="peliculas", url="http://www.newdivx.net"))
    itemlist.append( Item(channel=__channel__, title="Categorías", action="categorias", url="http://www.newdivx.net"))
    itemlist.append( Item(channel=__channel__, title="Buscar...", action="search") )
    return itemlist

def search(item,texto):
    #POST http://www.newdivx.net/
    #do=search&subaction=search&story=brave&x=0&y=0
    logger.info("[newdivx.py] search")
    if item.url=="":
        item.url="http://www.newdivx.net/"
    texto = texto.replace(" ","+")
    item.extra = "do=search&subaction=search&story="+texto+"&x=0&y=0"
    return peliculas(item)

def peliculas(item):
    logger.info("[newdivx.py] peliculas")
    itemlist=[]

    # Descarga la página
    if item.extra!="":
        data = scrapertools.cachePage( item.url , item.extra )
    else:
        data = scrapertools.cachePage( item.url )

    # Patron de las entradas
    patronvideos = '<a href="([^"]+)"[^<]+<img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    # Añade las entradas encontradas
    for url,thumbnail,title in matches:
        scrapedtitle = title
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    #Extrae la marca de siguiente página
    #<span>1</span> <a href="http://www.newdivx.net/peliculas-online/animacion/page/2/">2</a>
    patronvideos  = '</span> <a href="(http://www.newdivx.net.*?page/[^"]+)"'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedtitle = "Página siguiente >>"
        scrapedurl = matches[0]
        scrapedthumbnail = ""
        scrapedplot = ""
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

def categorias(item):
    logger.info("[newdivx.py] categorias")
    itemlist=[]

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <a href="#" class="fist-level-link">Category</a>
    <div class="hidden-menu">
    <div class="hidden-menu-block">
    <a href="/accion/">Acci&oacute;n</a>
    <a href="/adolescencia/">Adolescencia</a>
    <li><a href="/animacion/">Animaci&oacute;n</a></li>
    <li><a href="/aventuras/">Aventura</a></li>
    <li><a href="/belico/">Belico</a></li>
    <li><a href="/ciencia-ficcion/">C. Ficci&oacute;n</a></li>
    <li><a href="/clasico/">Clasico</a></li>
    <li><a href="/comedia/">Comedia</a></li>
    <li><a href="/drama/">Drama</a></li>
    <li><a href="/fantastico/">Fantastico</a></li>
    <li><a href="/intriga/">Intriga</a></li>
    <li><a href="/infantil/">Infantil</a></li>
    <li><a href="/musical/">Musical</a></li>
    <li><a href="/terror/">Terror</a></li>
    <li><a href="/thriller/">Thriller</a></li>
    <li><a href="/western/">Western</a> </li>
    <li><a href="/documentales/">Documentales</a></li>
    <li>   <a href="/sport/">Sport</a> </li>
    <li> <a href="/series/">Series</a> </li>
    <li> <a href="/estrenos/">Estrenos</a></li>
    <li><a href="/peliculas-vos/"><b>En VOS</b></a></li>
    <li><a href="/latino/"><b>En Latino</b></a></li>
    <li> <a href="/hd/"><b>En HD</b></a></li>
    '''
    data = scrapertools.get_match(data,'<a href="#" class="fist-level-link">Category</a>[^<]+<div class="hidden-menu">[^<]+<div class="hidden-menu-block">(.*?)</li>')
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    # Añade las entradas encontradas
    for url,title in matches:
        scrapedtitle = title
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    peliculas_items = peliculas(mainlist_items[0])
    bien = False
    for pelicula_item in peliculas_items:
        mirrors = servertools.find_video_items( item=pelicula_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien
