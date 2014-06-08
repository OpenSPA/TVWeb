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
    logger.info("extremaduratv.mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Informativos"   , action="programas"    , url="http://www.canalextremadura.es/alacarta/tv/programas/informativos", category="informativos") )
    itemlist.append( Item(channel=CHANNELNAME, title="Programas"      , action="programas"    , url="http://www.canalextremadura.es/alacarta/tv/programas/programas", category="programas") )
    itemlist.append( Item(channel=CHANNELNAME, title="Deportes"       , action="programas"    , url="http://www.canalextremadura.es/alacarta/tv/programas/deportes", category="deportes") )
    itemlist.append( Item(channel=CHANNELNAME, title="Archivo"        , action="archivo"      , url="http://www.canalextremadura.es/alacarta/tv/programas/archivo", category="programas") )

    return itemlist

def programas(item):
    logger.info("extremaduratv.programas")
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
    logger.info("extremaduratv.archivo")
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
    logger.info("extremaduratv.episodios")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Si hay algo en el contenedor izquierdo
    try:
        titulo_bloque_izquierdo = scrapertools.get_match(data,'<div class="videos-izq"><p>([^<]+)</p>')
        itemlist.append( Item(channel=CHANNELNAME, title=titulo_bloque_izquierdo , action="episodios_bloque_izquierdo", url=item.url, show=item.show, folder=True) )
        logger.info("extremaduratv.episodios SI encontrado bloque izquierdo")
    except:
        logger.info("extremaduratv.episodios NO encontrado bloque izquierdo")

    try:
        titulo_bloque_izquierdo = scrapertools.get_match(data,'<div class="videos-der"><p>([^<]+)</p>')
        itemlist.append( Item(channel=CHANNELNAME, title=titulo_bloque_izquierdo , action="episodios_bloque_derecho", url=item.url, show=item.show, folder=True) )
        logger.info("extremaduratv.episodios SI encontrado bloque derecho")
    except:
        logger.info("extremaduratv.episodios NO encontrado bloque derecho")

    return itemlist

def episodios_bloque_izquierdo(item):
    logger.info("extremaduratv.episodios_bloque_izquierdo")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<div class="contenedor-izq">(.*?)<div class="contenedor-der">')

    patron  = '<li[^<]+'
    patron += '<div class="views-field-view-node"[^<]+'
    patron += '<a href="([^"]+)">Ver video</a[^<]+</div[^<]+'
    patron += '<div class="views-field-title"[^<]+'
    patron += '<a href="[^"]+">([^<]+)</a>'

    matches = re.findall(patron,data,re.DOTALL)

    for url,titulo in matches:
        scrapedtitle = titulo.strip()
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="extremaduratv" , url=scrapedurl, thumbnail = scrapedthumbnail, show=item.show, folder=False) )

    #<li class="pager-next last"><a href="/alacarta/tv/programas/informativos/97/extremadura-noticias-1?page=1" 
    patron = '<li class="pager-next[^<]+<a href="([^"]+)"'
    matches = re.findall(patron,data,re.DOTALL)

    for url in matches:
        scrapedurl = urlparse.urljoin(item.url,url)
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios_bloque_izquierdo" , url=scrapedurl, show=item.show) )

    return itemlist

def episodios_bloque_derecho(item):
    logger.info("extremaduratv.episodios_bloque_derecho")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    '''
    <div class="contenedor-izq">
    <a href="/tv/informativos/extremadura-noticias-1" class="imagecache imagecache-programa_contenedor_alacarta imagecache-linked imagecache-programa_contenedor_alacarta_linked">
    <img src="http://www.canalextremadura.es/sites/default/files/imagecache/programa_contenedor_alacarta/extremaduranoticas_nuevo1_319.jpg" alt="Ver ficha del programa" title="Ver ficha del programa"  class="imagecache imagecache-programa_contenedor_alacarta" width="200" height="110" /></a>
    
    <div class="views_view view view-Mas-videos view-id-Mas_videos view-display-id-block_7 view-dom-id-2">
    <ul>
    <li >    
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

    #<li class="pager-next"><a href="/alacarta/tv/programas/informativos/65666/dossier-informativo?page=1" title="Go to next page" class="active">next ›</a></li>
    patron = '<li class="pager-next"><a href="([^"]+)"'
    matches = re.findall(patron,data,re.DOTALL)

    for url in matches:
        scrapedurl = urlparse.urljoin(item.url,url)
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , action="episodios_bloque_derecho" , url=scrapedurl, show=item.show) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # Todas las opciones tienen que tener algo
    items = mainlist(Item())
    for item in items:
        exec "itemlist="+item.action+"(item)"
    
        if len(itemlist)==0:
            print "La categoria '"+item.title+"' no devuelve programas"
            return False

    # El primer programa de la primera categoria tiene que tener videos
    mainlist_items = mainlist(Item())
    programas_items = programas(mainlist_items[0])
    submenu_episodios_items = episodios(programas_items[0])

    exec "episodios_itemlist="+submenu_episodios_items[0].action+"(submenu_episodios_items[0])"
    if len(episodios_itemlist)==0:
        print "El programa '"+programas_mainlist[0].title+"' no tiene videos en su seccion '"+submenu_episodios_items[0].title+"'"
        return False

    return True
