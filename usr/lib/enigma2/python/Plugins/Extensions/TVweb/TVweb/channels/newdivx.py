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
    itemlist.append( Item(channel=__channel__, title="Estrenos", action="peliculas", url="http://www.newdivx.net/estrenos/"))
    itemlist.append( Item(channel=__channel__, title="Castellano", action="peliculas", url="http://www.newdivx.net/castellano/"))
    itemlist.append( Item(channel=__channel__, title="Latino", action="peliculas", url="http://www.newdivx.net/latino/"))
    itemlist.append( Item(channel=__channel__, title="VOS", action="peliculas", url="http://www.newdivx.net/peliculas-vos/"))
    itemlist.append( Item(channel=__channel__, title="English", action="peliculas", url="http://www.newdivx.net/english/"))
    itemlist.append( Item(channel=__channel__, title="720p HD", action="peliculas", url="http://www.newdivx.net/hd/"))
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
    '''
    <div class="custom-post">
    <div class="custom-poster">
    <a href="http://www.newdivx.net/peliculas-online/drama/15496-la-ladrona-de-libros-2013.html">
    <img src="/uploads/posts/covers/887f683d64e3764f5e79f0a4cbfd4ada.jpg" alt="Ver Pelicula La ladrona de libros (2013) en Espa&ntilde;ol    Online Gratis" />
    <div class="custom-text2">La ladrona de libros (2013)</div></a>
    <div class="custom-label">DVDRip</div>
    <div class="custom-update">ESP 
    '''
    patronvideos  = '<a href="([^"]+)"[^<]+<img src="([^"]+)"[^<]+'
    patronvideos += '<div class="custom-text2">([^<]+)</div></a[^<]+'
    patronvideos += '<div class="custom-label">([^<]+)</div[^<]+'
    patronvideos += '<div class="custom-update">([^<]+)<'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    # Añade las entradas encontradas
    for url,thumbnail,title,calidad,idioma in matches:
        scrapedtitle = title
        scrapedtitle = unicode( scrapedtitle, "iso-8859-1" , errors="replace" ).encode("utf-8")
        scrapedtitle = scrapertools.htmlclean(scrapedtitle)
        scrapedtitle = scrapedtitle + " ["+calidad.strip()+"]["+idioma.strip().replace("\r","").replace("\n","")+"]"

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
    data = scrapertools.get_match(data,'li[^<]+<a href=".">Category</a[^<]+<ul>(.*?)</ul>')
    patron = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    # Añade las entradas encontradas
    for url,title in matches:
        scrapedtitle = title
        scrapedtitle = unicode( scrapedtitle, "iso-8859-1" , errors="replace" ).encode("utf-8")
        scrapedtitle = scrapertools.htmlclean(scrapedtitle)
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