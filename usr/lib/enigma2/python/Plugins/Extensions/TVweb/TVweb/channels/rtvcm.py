# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para rtvcm
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib
import os

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "rtvcm"
MAIN_URL = "http://www.rtvcm.es/"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[acbtv.py] mainlist")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(MAIN_URL)
    data = scrapertools.get_match(data,'<div[^<]+<a[^>]+>Programas</a></div>(.*?)</ul>')

    # Extrae categorias
    patron = '<li><a href="(/programas/default.php[^"]+)[^>]+>([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        url = urlparse.urljoin(MAIN_URL,scrapedurl)
        thumbnail = ""
        plot = ""
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="programas" , folder=True) )

    return itemlist

def programas(item):
    logger.info("[acbtv.py] programas")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    
    # Extrae programas
    '''
    <div class="caja-1">
    <div class="contentCaja">
    <p class="resumen-programa">&iquest;Conoces la m&uacute;sica popular de tu regi&oacute;n?&nbsp;Podr&aacute;s&nbsp;descubrirla en&nbsp; '<strong>El Templete</strong>', un programa donde bandas de m&uacute;sica, rondas y rondallas ser&aacute;n las encargadas de ense&ntilde;arnos lo mejor de nuestros pueblos con la m&uacute;sica como hilo conductor. Conoceremos a sus componentes y nos colaremos en sus ensayos, para acabar&nbsp;acompa&ntilde;&aacute;ndoles en sus rondas, en sus pasacalles y en sus actuaciones.</p>
    
    <div></div>
    
    <h6><strong>Entretenimiento</strong></h6>
    <h5>Martes a las 20:30<br>en CMT</h5>
    <a href="detail.php?id=7623"><img src="http://media.rtvcm.es/media//0000048500/0000048975.jpg" alt="" width="150" height="124" /></a>
    <h3><a href="detail.php?id=7623">El Templete</a></h3>
    <h4></h4>
    
    </div>
    </div>
    '''
    patron  = '<div class="caja-1"[^<]+'
    patron += '<div class="contentCaja"[^<]+'
    patron += '<p class="resumen-programa">(.*?)</p>.*?'
    patron += '<a href="([^"]+)"><img src="([^"]+)"[^<]+</a[^<]+'
    patron += '<h3><a href="[^"]+">([^<]+)</a></h3>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedplot,scrapedurl,scrapedthumbnail,scrapedtitle in matches:
        title = scrapedtitle.strip()
        title = scrapertools.htmlclean(title)
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = scrapertools.htmlclean(scrapedplot).strip()
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="episodios" , show = item.title , extra="1", folder=True) )

    return itemlist

def episodios(item):
    logger.info("[acbtv.py] episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    data = scrapertools.get_match(data,'deos</h4[^<]+<ul>(.*?)</ul>')
    
    # Extrae videos
    patron  = '<a href="\#None" onClick="showVideo\(\'([^\']+)\'\)"[^>]+>([^<]+)<br/><br/></a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle
        url = url = "rtmp://fl0.c80331.cdn.qbrick.com/80331/_definst_/mp4:"+scrapedurl
        thumbnail = item.thumbnail
        plot = item.plot
        itemlist.append( Item(channel=CHANNELNAME, title=title , url=url,  thumbnail=thumbnail , action="play" , server="directo", show = item.title , folder=False) )

    return itemlist
