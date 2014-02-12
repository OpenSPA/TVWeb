# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para Shurweb
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "shurweb"
__category__ = "F,S,D,A"
__type__ = "generic"
__title__ = "Shurweb"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[shurweb.py] getmainlist")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Peliculas"                , action="menupeliculas", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Series"                   , action="menuseries"   , url="http://www.shurweb.es/shurseries/", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    #itemlist.append( Item(channel=__channel__, title="Animacion"                , action="series"       , url="http://www.shurweb.es/animacion/", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Documentales"             , action="peliculas"    , url="http://www.shurweb.es/videoscategory/documentales/", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    #itemlist.append( Item(channel=__channel__, title="Buscar"                   , action="search") )
    return itemlist

def menupeliculas(item):
    logger.info("[shurweb.py] menupeliculas")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Novedades"                    , action="novedades_peliculas"    , url="http://www.shurweb.es/", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Películas - A-Z"              , action="menupelisaz", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Películas - Decadas"          , action="menupelisanos", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Películas - Animación"        , action="peliculas"   , url="http://www.shurweb.es/videoscategory/animacion/", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg") )
    return itemlist

def menuseries(item):
    logger.info("[shurweb.py] menuseries")
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Últimos episodios"        , action="novedades_series"    , url="http://www.shurweb.es/", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Series - A-Z"              , action="menuseriesaz", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Todas las series"         , action="series"   , url="http://www.shurweb.es/shurseries/", fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg") )
    return itemlist

def menupelisaz(item):
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="#"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/numbers/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="A"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/a/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="B"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/b/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="C"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/c/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="D"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/d/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="E"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/e/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="F"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/f/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="G"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/g/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="H"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/h/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="I"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/i/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="J"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/j/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="K"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/k/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="L"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/l/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="M"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/m/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="N"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/n/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="O"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/o/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="P"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/p/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Q"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/q/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="R"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/r/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="S"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/s/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="T"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/t/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="U"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/u/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="V"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/v/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="W"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/w/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="X"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/x/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Y"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/y/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Z"        , action="peliculas"   , url="http://www.shurweb.es/lista-de-peliculas/z/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    return itemlist

def menuseriesaz(item):
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="#"        , action="series"   , url="http://www.shurweb.org/series/numbers_series/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="A"        , action="series"   , url="http://www.shurweb.org/series/a/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="B"        , action="series"   , url="http://www.shurweb.org/series/b/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="C"        , action="series"   , url="http://www.shurweb.org/series/c/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="D"        , action="series"   , url="http://www.shurweb.org/series/d/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="E"        , action="series"   , url="http://www.shurweb.org/series/e/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="F"        , action="series"   , url="http://www.shurweb.org/series/f/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="G"        , action="series"   , url="http://www.shurweb.org/series/g/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="H"        , action="series"   , url="http://www.shurweb.org/series/h/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="I"        , action="series"   , url="http://www.shurweb.org/series/i/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="J"        , action="series"   , url="http://www.shurweb.org/series/j/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="K"        , action="series"   , url="http://www.shurweb.org/series/k/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="L"        , action="series"   , url="http://www.shurweb.org/series/l/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="M"        , action="series"   , url="http://www.shurweb.org/series/m/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="N"        , action="series"   , url="http://www.shurweb.org/series/n/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="O"        , action="series"   , url="http://www.shurweb.org/series/o/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="P"        , action="series"   , url="http://www.shurweb.org/series/p/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Q"        , action="series"   , url="http://www.shurweb.org/series/q/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="R"        , action="series"   , url="http://www.shurweb.org/series/r/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="S"        , action="series"   , url="http://www.shurweb.org/series/s/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="T"        , action="series"   , url="http://www.shurweb.org/series/t/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="U"        , action="series"   , url="http://www.shurweb.org/series/u/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="V"        , action="series"   , url="http://www.shurweb.org/series/v/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="W"        , action="series"   , url="http://www.shurweb.org/series/w/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="X"        , action="series"   , url="http://www.shurweb.org/series/x/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Y"        , action="series"   , url="http://www.shurweb.org/series/y/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Z"        , action="series"   , url="http://www.shurweb.org/series/z/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    return itemlist

def menupelisanos(item):
    itemlist = []
    itemlist.append( Item(channel=__channel__, title="10's"        , action="peliculas"   , url="http://www.shurweb.es/videoscategory/10s/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="00's"        , action="peliculas"   , url="http://www.shurweb.es/videoscategory/00s/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="90's"        , action="peliculas"   , url="http://www.shurweb.es/videoscategory/90s/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="80's"        , action="peliculas"   , url="http://www.shurweb.es/videoscategory/80s/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="70's"        , action="peliculas"   , url="http://www.shurweb.es/videoscategory/70s/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="60's"        , action="peliculas"   , url="http://www.shurweb.es/videoscategory/60s/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    itemlist.append( Item(channel=__channel__, title="Antiguas"        , action="peliculas"   , url="http://www.shurweb.es/videoscategory/antiguas/",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    return itemlist

# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item,texto,categoria=""):
    logger.info("[shurweb.py] "+item.url+" search "+texto)
    itemlist = []
    url = item.url
    texto = texto.replace(" ","+")
    logger.info("categoria: "+categoria+" url: "+url)
    try:
        item.url = "http://www.shurweb.es/?s=%s"
        item.url = item.url % texto
        itemlist.extend(buscador(item))
        return itemlist
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def buscador(item,paginacion=True):
    logger.info("[shurweb.py] peliculas")
    url = item.url
    # Descarga la página
    data = scrapertools.cachePage(url)
    # Extrae las entradas
    patronvideos = '<a href="([^"]+)" style="display:none;" rel="nofollow"><img src="([^"]+)" width="100" height="144" border="0" alt="" /><br/><br/>[^<]+<b>([^<]+)</b></a>[^<]+<a href="([^"]+)">([^#]+)#888"><b>([^<]+)</b>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:
        if match[5] == 'Peliculas' or match[5] == 'Series':
            scrapedtitle =  match[2]
            scrapedtitle = scrapertools.entityunescape(scrapedtitle)
            fulltitle = scrapedtitle
            scrapedplot = ""
            scrapedurl = match[3]
            scrapedthumbnail = match[1]
            if DEBUG: logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
            itemlist.append( Item(channel=__channel__, action='findvideos', title=scrapedtitle , fulltitle=fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=scrapedtitle , context="4|5") )

    return itemlist

def series(item,paginacion=True):
    logger.info("[shurweb.py] series")
    url = item.url

    # Descarga la página
    data = scrapertools.cachePage(url)
    patron  = '<li class="clearfix"[^<]+'
    patron += '<a class="video_thumb" href="([^"]+)" rel="bookmark" title="([^"]+)"[^<]+'
    patron += '<img width="[^"]+" height="[^"]+" src="([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []

    for url,title,thumbnail in matches:
        scrapedtitle = title.replace("&amp;","&")
        fulltitle = scrapedtitle
        scrapedplot = ""
        scrapedurl = url
        scrapedthumbnail = thumbnail
        if DEBUG: logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action='episodios', title=scrapedtitle , fulltitle=fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=scrapedtitle , viewmode="movie", show=scrapedtitle, context="4|5",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg") )

    try:
    	matches = re.compile('<a class="next page-numbers" href="([^"]+)">', re.S).findall(data)
    	if len(matches)>0:
        	itemlist.append( Item(channel=__channel__, action='series', title='!Página siguiente' , fulltitle='!Página siguiente' , url=matches[0] , thumbnail="" , plot="" , fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg") )
    except:
	pass

    return itemlist

def episodios(item):
    logger.info("[shurweb.py] episodios")
    url = item.url
    # Descarga la página
    data = scrapertools.cachePage(url)
    item = detalle_programa(item,data)
    # Extrae las entradas
    '''
    <li>
    <div class="video">
    <a class="video_title" href="http://www.shurweb.es/videos/alcatraz-1x10/">Alcatraz 1x10</a>
    </div>
    </li>
    '''
    patron  = '<li[^<]+'
    patron += '<div class="video"[^<]+'
    patron += '<a class="video_title" href="([^"]+)">([^<]+)</a>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    itemlist = []
    for url,title in matches:
        scrapedtitle = title
        fulltitle = scrapedtitle
        scrapedplot = item.plot
        scrapedurl = url
        scrapedthumbnail = item.thumbnail
        if DEBUG: logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action='findvideos', title=scrapedtitle , fulltitle=fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=scrapedtitle , show=item.show, context="4|5",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg", viewmode="movie_with_plot") )

    if config.get_platform().startswith("xbmc") or config.get_platform().startswith("boxee"):
        itemlist.append( Item(channel=item.channel, title="Añadir esta serie a la biblioteca de XBMC", url=item.url, action="add_serie_to_library", extra="episodios", show=item.show) )
        itemlist.append( Item(channel=item.channel, title="Descargar todos los episodios de la serie", url=item.url, action="download_all_episodes", extra="episodios", show=item.show))

    return itemlist

def detalle_programa(item,data=""):
    logger.info("[shurweb.py] detalle_programa")

    # Descarga la página
    url = item.url
    if data=="":
        data = scrapertools.cache_page(url)

    # Obtiene el thumbnail
    try:
        item.thumbnail = scrapertools.get_match(data,'<div class="serie_thumb"><img src="([^"]+)"/>')
    except:
        pass

    plot = scrapertools.get_match(data,'<div class="synopsis clearfix">(.*?)</div>')
    plot = re.compile("<strong>Idiom[^<]+</strong>[^<]+<br />",re.DOTALL).sub("",plot)
    plot = re.compile("<strong>Calid[^<]+</strong>[^<]+<br />",re.DOTALL).sub("",plot)
    plot = re.compile("Sinopsis\:",re.DOTALL).sub("",plot)
    item.plot = scrapertools.htmlclean(plot).strip()

    try:
        item.title = scrapertools.get_match(data,'<h1 class="cat_head">([^<]+)</h1>').strip()
    except:
        pass

    return item

def novedades_peliculas(item):
    logger.info("[shurweb.py] novedades_peliculas")
    url = item.url
    # Descarga la página
    data = scrapertools.cachePage(url)
    data = scrapertools.get_match(data,'pelis[^<]+<ul class="categories_list">(.*?)</ul>')

    return peliculas(item,data=data)

def novedades_series(item):
    logger.info("[shurweb.py] novedades_series")
    url = item.url
    # Descarga la página
    data = scrapertools.cachePage(url)
    data = scrapertools.get_match(data,'series[^<]+<ul class="categories_list">(.*?)</ul')

    return peliculas(item,data=data)

def peliculas(item,paginacion=True,data=None):
    logger.info("[shurweb.py] peliculas")
    url = item.url

    # Descarga la página
    if data is None:
        data = scrapertools.cachePage(url)

    itemlist = []

    '''
    <li class="clearfix">
    <a class="video_thumb" href="http://www.shurweb.es/videos/elysium/" rel="bookmark" title="Elysium">
    <img width="123" height="100" src="http://www.shurweb.es/wp-content/uploads/2013/11/elysium-movie-1920x1440.jpg" class=" wp-post-image" alt="elysium-movie-1920x1440"/>
    <span class="time"> 109min </span>
    </a>
    <p class="title"><a href="http://www.shurweb.es/videos/elysium/" rel="bookmark" title="Elysium">Elysium</a></p>
     
    <p></p>
    </li>
    '''
    # Extrae las entradas
    patronvideos = '<a class="video_thumb" href="([^"]+)" rel="bookmark" title="([^"]+)">.*?<img.*?src="([^"]+)"'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    if len(matches) > 0:
    	for match in matches:
	        scrapedtitle =  match[1]
        	scrapedtitle = scrapertools.entityunescape(scrapedtitle)
        	fulltitle = scrapedtitle
        	scrapedplot = ""
        	scrapedurl = match[0]
        	scrapedthumbnail = match[2]
        	if DEBUG: logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        	itemlist.append( Item(channel=__channel__, action='findvideos', title=scrapedtitle , fulltitle=fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=scrapedtitle , viewmode="movie", context="4|5",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg") )

    # Formato alternativo (pagina novedades)
    patronvideos  = '<a class="video_thumb" href="([^"]+)"[^<]+'
    patronvideos += '<img src="([^"]+)" alt="([^"]+)"'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    if len(matches) > 0:
    	for match in matches:
        	scrapedtitle =  match[2]
        	scrapedtitle = scrapertools.entityunescape(scrapedtitle)
        	fulltitle = scrapedtitle
        	scrapedplot = ""
        	scrapedurl = match[0]
        	scrapedthumbnail = match[1]
        	if DEBUG: logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        	itemlist.append( Item(channel=__channel__, action='findvideos', title=scrapedtitle , fulltitle=fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=scrapedtitle , viewmode="movie", context="4|5",fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg") )

    #<span class="i_next fr" ><a href="http://www.shurweb.es/videoscategory/animacion/page/2/" >Ver Más Videos</a> </span>
    try:    
        next_page_url = scrapertools.get_match(data,'<span class="i_next fr" ><a href="([^"]+)" >Ver M')
        itemlist.append( Item(channel=__channel__, title=">> Página siguiente", action="peliculas", url=urlparse.urljoin(item.url,next_page_url),fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg"))
    except:
        pass

    try:
    	matches = re.compile("<a href='([^']+)' class='nextpostslink'>", re.S).findall(data)
    	if len(matches)>0:
        	itemlist.append( Item(channel=__channel__, action='peliculas', title='!Página siguiente' , fulltitle='!Página siguiente' , url=matches[0] , thumbnail="" , plot="" , fanart="http://pelisalacarta.mimediacenter.info/fanart/shurweb.jpg") )
    except:
	pass

    return itemlist

def peliculas_ordenadas(item):
    itemlist = peliculas(item)
    itemlist.sort(key=lambda item: item.title.lower().strip())
    return itemlist

def findvideos(item):
    logger.info("[shurweb.py] findvideos")
    itemlist=[]
    
    # Descarga la página
    data = scrapertools.cachePage(item.url)

    from servers import servertools
    itemlist.extend(servertools.find_video_items(data=data))
    for videoitem in itemlist:
        videoitem.channel=__channel__
        videoitem.action="play"
        videoitem.folder=False
        videoitem.title = "Vídeo en "+videoitem.server
        videoitem.fulltitle = item.fulltitle
        videoitem.plot = item.plot
        videoitem.thumbnail = item.thumbnail
        videoitem.viewmode = "movie_with_plot"

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    # mainlist
    mainlist_items = mainlist(Item())
    menupeliculas_items = menupeliculas(mainlist_items[0])
    peliculas_items = peliculas(menupeliculas_items[0])
    bien = False
    for pelicula_item in peliculas_items:
        mirrors = servertools.find_video_items(item=pelicula_item)
        if len(mirrors)>0:
            bien = True
            break

    return bien
