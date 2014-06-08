# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para disneychannel
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "disneychannel"
MAIN_URL = "http://replay.disneychannel.es/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.disneychannel mainlist")
    return series(item)

def series(item):
    logger.info("tvalacarta.channels.disneychannel series")
    
    # Descarga la página
    item.url = MAIN_URL
    data = scrapertools.cache_page(item.url)
    #logger.info(data)

    # Extrae las entradas (series)
    '''
    <li>
    <a class="thumb" href="http://replay.disneychannel.es/ant-farm-escuela-de-talentos/"><img src="/static/images/thSerie160_Serie_12.png" alt="A.N.T. FARM. Escuela de talentos" /></a>
    <div class="data">
    <h3><a href="http://replay.disneychannel.es/ant-farm-escuela-de-talentos/">A.N.T. FARM. Escuela de talentos</a></h3>
    '''
    patron  = '<li>[^<]+'
    patron += '<a class="thumb" href="([^"]+)"><img src="([^"]+)" alt="([^"]+)" /></a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    #if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for url,thumbnail,title in matches:
        scrapedtitle = title
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle, folder=True) )

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.disneychannel episodios")
    
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # episodios
    '''
    <li class="video">
    <a class="thumb" href="/pecezuelos/diversion-en-pupu-buenosratos.html"><img alt="Pez fuera del agua" src="/clipping/2011/11/29/00018/7.jpg"></a>								
    <div class="data">
    <div class="duration"></div>
    <h3><a href="/pecezuelos/diversion-en-pupu-buenosratos.html">Diversión en Pupu Buenosratos</a></h3>
    <div class="likes"><span class="invisible">Gusta a </span>42</div>
    </div>
    <a class="play" href="" style="z-index: -1; visibility: visible;"></a>
    </li>
    '''
    patron  = '<li class="video">[^<]+'
    patron += '<a class="thumb" href="([^"]+)"><img alt="[^"]+" src="([^"]+)"></a>[^<]+'
    patron += '<div class="data">[^<]+'
    patron += '<div class="duration[^<]+</div>[^<]+'
    patron += '<h3><a[^>]+>([^<]+)</a></h3>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    #if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for url,thumbnail,title in matches:
        scrapedtitle = title
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="disneychannel", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show , folder=False) )

    if (config.get_platform().startswith("xbmc") or config.get_platform().startswith("boxee")) and len(itemlist)>0:
        itemlist.append( Item(channel=item.channel, title=">> Opciones para esta serie", url=item.url, action="serie_options##episodios", thumbnail=item.thumbnail, show=item.show, folder=False))

    return itemlist

def partes(item):
    logger.info("tvalacarta.channels.disneychannel partes")
    
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # episodios
    '''
    <li class="video">
    <a class="thumb" href="/pecezuelos/diversion-en-pupu-buenosratos.html"><img alt="Pez fuera del agua" src="/clipping/2011/11/29/00018/7.jpg"></a>                                
    <div class="data">
    <div class="duration"></div>
    <h3><a href="/pecezuelos/diversion-en-pupu-buenosratos.html">Diversión en Pupu Buenosratos</a></h3>
    <div class="likes"><span class="invisible">Gusta a </span>42</div>
    </div>
    <a class="play" href="" style="z-index: -1; visibility: visible;"></a>
    </li>
    '''
    patron  = '<li class="video">[^<]+'
    patron += '<a class="thumb" href="([^"]+)"><img alt="[^"]+" src="([^"]+)"></a>[^<]+'
    patron += '<div class="data">[^<]+'
    patron += '<div class="duration[^<]+</div>[^<]+'
    patron += '<h3><a[^>]+>([^<]+)</a></h3>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    #if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for url,thumbnail,title in matches:
        scrapedtitle = title
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="disneychannel", url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show , folder=False) )

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    items_programas = mainlist(Item())
    if len(items_programas)==0:
        return False

    items_episodios = episodios(items_programas[0])
    if len(items_episodios)==0:
        return False

    return bien