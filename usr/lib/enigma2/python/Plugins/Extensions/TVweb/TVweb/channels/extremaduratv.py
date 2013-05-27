# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Extremadura TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "extremaduratv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[extremaduratv.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Informativos"   , action="programas"    , url="http://www.canalextremadura.es/alacarta/tv/programas/informativos", category="informativos") )
    itemlist.append( Item(channel=CHANNELNAME, title="Programas"      , action="programas"    , url="http://www.canalextremadura.es/alacarta/tv/programas/programas", category="programas") )
    itemlist.append( Item(channel=CHANNELNAME, title="Deportes"       , action="programas"    , url="http://www.canalextremadura.es/alacarta/tv/programas/deportes", category="deportes") )
    itemlist.append( Item(channel=CHANNELNAME, title="Archivo"        , action="archivo"      , url="http://www.canalextremadura.es/alacarta/tv/programas/archivo", category="programas") )

    return itemlist

def programas(item):
    logger.info("[extremaduratv.py] programas")
    itemlist = []

    # Descarga la página
    '''
    <div class="programa-alacarta">
    <a href="/alacarta/tv/programas/programas/4432/dehesa-brava" title="Título del enlace">
    \<img src="http://www.canalextremadura.es/sites/default/files/imagecache/alacarta_listado_programas/logo_28_fuego.jpg" alt="Ver ficha del programa" title="Ver ficha del programa"  class="imagecache imagecache-alacarta_listado_programas imagecache-default imagecache-alacarta_listado_programas_default" width="225" height="140" />
    \</a>        <div class="titulo"><a href="/alacarta/tv/programas/programas/4432/dehesa-brava" title="Título del enlace">Dehesa Brava</a></div>
    </div>
    '''
    data = scrapertools.cachePage(item.url)
    patron  = '<div class="programa-alacarta">[^<]+'
    patron += '<a href="([^"]+)"[^<]+<img src="([^"]+)"[^<]+</a>[^<]+<div class="titulo"><a[^>]+>([^<]+)</a></div>'
    matches = re.findall(patron,data,re.DOTALL)

    for url,thumbnail,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, show=scrapedtitle) )

    return itemlist

def archivo(item):
    logger.info("[extremaduratv.py] archivo")
    itemlist = []

    # Descarga la página
    '''
    <div class="programa-alacarta">
    <a href="/alacarta/tv/programas/programas/1934/extremadura-desde-el-aire" title="Título del enlace">
    \<a href="/tv/cultura/extremadura-desde-el-aire" class="imagecache imagecache-alacarta_categorias_programas_archivo imagecache-linked imagecache-alacarta_categorias_programas_archivo_linked">
    \<img src="http://www.canalextremadura.es/sites/default/files/imagecache/alacarta_categorias_programas_archivo/extremadura_desde_el_aire_.jpg" as_programas_archivo" width="75" height="46" />
    \</a></a>        <div class="titulo"><a href="/alacarta/tv/programas/programas/1934/extremadura-desde-el-aire" title="Título del enlace">Extremadura desde el Aire</a></div>
    '''
    data = scrapertools.cachePage(item.url)
    patron  = '<div class="programa-alacarta">[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<a[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a></a>[^<]+<div class="titulo"><a[^>]+>([^<]+)</a></div>'
    matches = re.findall(patron,data,re.DOTALL)

    for url,thumbnail,titulo in matches:
        scrapedtitle = titulo
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, show=scrapedtitle) )

    return itemlist

def episodios(item):
    logger.info("[extremaduratv.py] episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <div class="views-field-field-video-imagen-fid" >     
    <a href="/alacarta/tv/videos/nada-corriente-080312" class="imagecache imagecache-alacarta_listado_programas imagecache-linked imagecache-alacarta_listado_programas_linked">
    \<img src="http://www.canalextremadura.es/sites/default/files/imagecache/alacarta_listado_programas/PROG00069417_2.jpg"programas" width="225" height="140" />
    \</a><span class="video">video</span>        </div>
    <div class="views-field-title" >     
    Nada Corriente (08/03/12)        </div>
    '''
    
    '''
    <div class="views-field-field-video-imagen-fid" >     
    <a href="/alacarta/tv/videos/karts-en-talavera-260312" class="imagecache imagecache-alacarta_listado_programas imagecache-linked imagecache-alacarta_listado_programas_linked">
    \<img src="http://www.canalextremadura.es/sites/default/files/imagecache/alacarta_listado_programas/AHORAEXTREMADURA-Karts%20en%20Talavera_2.jpg"40" />
    \</a> <span class="video">video</span>        </div>
    <div class="views-field-title" >     
    Karts en Talavera (26/03/12)        </div>
    '''
    patron  = '<div class="views-field-field-video-imagen-fid[^>]+>[^<]+'
    patron += '<a href="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a>\s*<span class="video">video</span>[^<]+</div>[^<]+'
    patron += '<div class="views-field-title[^>]+>([^<]+)</div>'
    matches = re.findall(patron,data,re.DOTALL)

    for url,thumbnail,titulo in matches:
        scrapedtitle = titulo.strip()
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="extremaduratv" , url=scrapedurl, thumbnail = scrapedthumbnail, show=item.show, folder=False) )

    patron = '<li class="pager-next"><a href="([^"]+)" title="Ir a la p'
    matches = re.findall(patron,data,re.DOTALL)

    for url in matches:
        scrapedurl = urlparse.urljoin(item.url,url)
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios" , url=scrapedurl, show=item.show) )


    return itemlist
