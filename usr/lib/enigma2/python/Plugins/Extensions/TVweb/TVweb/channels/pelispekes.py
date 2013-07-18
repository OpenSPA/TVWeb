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
        <a target="_blank" href="http://www.pelispekes.com/shin-chan-el-pequeno-samurai/">
        <img width="145" height="199" border="0" pagespeed_high_res_src="http://1-ps.googleusercontent.com/h/www.pelispekes.com/caratula-pekes/145x199x2079-145x199.jpg.pagespeed.ic.yIfp9_86mn.jpg" alt="Ver pelicula Shin chan. El pequeño samurai" src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAFA3PEY8MlBGQUZaVVBfeMiCeG5uePWvuZHI////////////////////////////////////////////////////2wBDAVVaWnhpeOuCguv/////////////////////////////////////////////////////////////////////////wAARCADHAJEDASIAAhEBAxEB/8QAGAAAAwEBAAAAAAAAAAAAAAAAAAIDAQT/xAAxEAACAgEDAwQBAwMDBQAAAAABAgARAxIhMUFRYQQTInGRMoGhQlKxFCPBQ2JyouH/xAAXAQEBAQEAAAAAAAAAAAAAAAAAAQID/8QAGxEBAQEBAAMBAAAAAAAAAAAAAAERIQIxQRL/2gAMAwEAAhEDEQA/ALCgo2HE0Fa4EwcCNRo7/wATjFIyo3IG0UrjB2AlAD3/AIiC75/iX4u0aUrgQ04/Eaj3/iaAb5/iSG0jooUkCTsdAPxLOQFN9pEPqcmtr4m/GafrChqbfmXQhjV/+sVAgJYneKxGoivqayJtVYaXUGqPWouZQu2oW3SopyKyBaIIirpLfM2QIxCU2rSByek6WrH2NDtDGgvUOZzepc6yt/cKMmcNsAPviIXYdB9ATEUMaYm+k6DgOMApuesommUotslA8HpOlCmReADJPepVbGDt278xVVsWbSAdN7EyBt/7RCNqHcQgU0qyix0m+2vaap+I+oTkrmzKFbYbGKFEpnYE1tQkzk2pRQ7nmaxqWegRXSClQbJoTG1ZF7xsOHcFlv8AeXEtZ8GLaSf3m4wYzYNKgg79ZQcTc652pqjWaPMb2CLZjvLY6/eM1VbcSjlCCxTb/UT1GMpTXdzoGkta8SjIGSiLgjnwuyqNXEUtjzMQ3xYHYyuVhoWxz/E5MyFcn3vMxpr4mxuC3F8idYtgMisarYETlxZmX4sNSnoZ06tLhBt2EUUTWRbUPEh6pqCjY7yrZCqnVU48Qt9we5MSB7+oQ+HeEuI7FHxB8SDZT7gB2EqDS1d7TmylbFH5dRMY1D5C2r5UQdoipYZa3G81sisNFHjmS31cntQlkLcaraWsSiP/ALljbuIlU1dOY4ZQCK3lxLdWZwQQOK5mIPiJPGpernSqgCJxn2AVUTny5CxrpL5GCr5PE5yB1NGNG42I6bSv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" onload="var elem=this;setTimeout(function(){elem.onload = null;elem.src=elem.getAttribute('pagespeed_high_res_src');}, 0);"/>
        </a>
        </div>
        <div class="pelInfoToolTip" id="divtool2079">
        <div class="divTituloTool">
        <span class="titulotool"><strong>Shin chan. El pequeño samurai</strong></span> <strong>(2002)</strong>
        </div>
        <div>
        <strong>Género: </strong>Comedia       </div>
        <div class="sinopsis">
        <strong>Sinopsis:</strong> En Shin chan el pequeño samurái Shinnosuke viaja en el tiempo como por arte de magia hasta el Japón del año 1574, una época llena de conflictos. En una batalla entre clanes conoce a Matabe, un joven samurái solitario con el que pronto hace muy buenas migas. Los Nohara, preocupados por la desaparición de su [...]       </div>
        <div>
        '''
        patron  = '<a target="_blank" href="(.*?)"[^<]+'
        patron += '<img width="\d+" height="\d+" border="0" pagespeed_high_res_src="(.*?)" alt="(.*?)".*?'
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