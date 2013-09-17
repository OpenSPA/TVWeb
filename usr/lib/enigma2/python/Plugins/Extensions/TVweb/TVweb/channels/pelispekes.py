# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para pelispekes
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "pelispekes"
__category__ = "F"
__type__ = "generic"
__title__ = "Pelis Pekes"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[pelispekes.py] mainlist")
    itemlist=[]

    itemlist.append( Item(channel=__channel__ , action="novedades"   , title="Novedades" , url="http://pelispekes.com/"))
    itemlist.append( Item(channel=__channel__ , action="categorias" , title="Categorias", url="http://pelispekes.com/"))
    itemlist.append( Item(channel=__channel__ , action="letras" , title="Abecedario", url="http://pelispekes.com/"))
    
    return itemlist

def novedades(item):
    logger.info("[pelispekes.py] novedades")
    itemlist = []

    # Extrae las entradas (carpetas)
    data = scrapertools.cachePage(item.url)
    patron = 'class="filmgal">(.*?)<strong>Duración: </strong>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.info("hay %d matches" % len(matches))

    for match in matches:
        '''
        <a target="_blank" href="http://www.pelispekes.com/las-aventuras-de-tiny-toons-o-como-he-disfrutado-de-mis-vacaciones/">
<img width="145" height="199" border="0" src="http://www.pelispekes.com/caratula-pekes/6823-145x199.jpg" alt="Ver pelicula Las aventuras de Tiny Toons, o cómo he disfrutado de mis vacaciones"/>
</a>
</div>
<div class="pelInfoToolTip" id="divtool6823">
<div class="divTituloTool">
<span class="titulotool"><strong>Las aventuras de Tiny Toons, o cómo he disfrutado de mis vacaciones</strong></span> <strong>(1992)</strong>
</div>
<div>
<strong>Género: </strong>1992 / Animacion / Infantil / L / T
</div>
<div class="sinopsis">
<strong>Sinopsis:</strong> Durante las vacaciones, Búster y Babs van a vivir la batalla de agua más movidita, mientras que Plucky Duck y Hamton Pig van a compartir un viaje en coche digno de las aventuras de Thelma &#038; Louise&#8230; Película directa a DVD protagonizada por los Tiny Toons, y que parodiaba una gran cantidad de películas, como [...]
</div>
<div>
        '''
        patron  = '<a target="_blank" href="(.*?)"[^<]+'
        patron += '<img width="\d+" height="\d+" border="0" src="(.*?)" alt="(.*?)".*?'
        patron += '<strong>Sinopsis:</strong>(.*?)</div>'
        matches2 = re.compile(patron,re.DOTALL).findall(match)
        logger.info("hay %d matches2" % len(matches2))

        for match2 in matches2:
            # Atributos
            scrapedurl = match2[0]
            scrapedtitle =match2[2].replace("Ver pelicula","").replace("&#8211;","")
            scrapedthumbnail = match2[1]
            scrapedplot = match2[3]
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
            itemlist.append( Item(channel=item.channel , action="findvideos"   , title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , viewmode="movie_with_plot"))
    
    # Extrae la pagina siguiente
    patron  = "class='current'>[^<]+</span><a href='([^']+)'"
    matches = re.compile(patron,re.DOTALL).findall(data)

    for match in matches:
        scrapedtitle = ">> Pagina siguiente"
        scrapedurl = match
        scrapedthumbnail = ""
        scrapeddescription = ""
	scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=item.channel , action="novedades"   , title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail, plot=scrapedplot ))

    return itemlist

def categorias(item):
    logger.info("[pelispekes.py] categorias")

    url = item.url
                
    data = scrapertools.cachePage(url)

    # Extrae las entradas (carpetas)
   
    patron = '<div id="genero">(.*?)<div class="corte"></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.info("hay %d matches" % len(matches))
    
    itemlist = []
    for match in matches:
        patron  = '<a href="(.*?)">(.*?)</a>'
        matches2 = re.compile(patron,re.DOTALL).findall(match)
        logger.info("hay %d matches2" % len(matches2))

        for match2 in matches2:
        # Atributos
            scrapedurl = "http://pelispekes.com"+match2[0]
            scrapedtitle =match2[1]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
            
            # A�ade al listado de XBMC
            itemlist.append( Item(channel=item.channel , action="novedades"   , title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail, plot=scrapedplot ))
        
    return itemlist

def letras(item):
    logger.info("[pelispekes.py] letras")

    url = item.url
                
    data = scrapertools.cachePage(url)

    # Extrae las entradas (carpetas)
   
    patron = '<div id="abecedario">(.*?)<div class="corte"></div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.info("hay %d matches" % len(matches))
    
    itemlist = []
    for match in matches:
        patron  = '<a href="(.*?)">(.*?)</a>'
        matches2 = re.compile(patron,re.DOTALL).findall(match)
        logger.info("hay %d matches2" % len(matches2))

        for match2 in matches2:
        # Atributos
            scrapedurl = "http://pelispekes.com"+match2[0]
            scrapedtitle =match2[1]
            scrapedthumbnail = ""
            scrapedplot = ""
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
            
            # A�ade al listado de XBMC
            itemlist.append( Item(channel=item.channel , action="novedades"   , title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail, plot=scrapedplot ))
        
    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    novedades_items = novedades(mainlist_items[0])
    bien = False
    for novedades_item in novedades_items:
        mirrors = servertools.find_video_items( item=novedades_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien
