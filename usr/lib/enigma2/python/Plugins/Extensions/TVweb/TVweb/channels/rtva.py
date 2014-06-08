# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para RTVA
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib,re

from core import logger
from core import scrapertools
from core.item import Item

logger.info("[rtva.py] init")

DEBUG = False
CHANNELNAME = "rtva"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[rtva.py] mainlist")
    
    item.url="http://www.canalsuralacarta.es/television/listado/todos/0"
    itemlist = programas(item)
    return itemlist

def programas(item):
    logger.info("[rtva.py] programas")
    
    itemlist=[]

    # Extrae los programas
    '''
    <li>
    <div class="programs_list_az_item capaseccionl">
    <div class="programs_list_az_item_media">
    <a href="http://www.canalsuralacarta.es/television/programa/a-caballo/56" class="programs_list_az_item_media_link capaseccionl" title="A caballo">
    <img src="http://www.canalsuralacarta.es/pictures/246/picture246_20110114_131605_crop1sub2.jpg" alt="A caballo" title="A caballo" class="no_foto" width="138" height="77" />
    </a>
    </div>
    <h5 class="programs_list_az_item_name">
    <a href="http://www.canalsuralacarta.es/television/programa/a-caballo/56" class="programs_list_az_item_name_link capaseccionl" title="A caballo">
    A caballo                </a>
    </h5>
    <p class="programs_list_az_item_description">A caballo es el programa de canalSur 2 que se ocupa del mundo de la equitaci&oacute;n y la...</p>
    </div>
    </li>
    '''
    data = scrapertools.cache_page(item.url)
    patron  = '<li>[^<]+'
    patron += '<div class="programs_list_az_item capaseccionl">[^<]+'
    patron += '<div class="programs_list_az_item_media">[^<]+'
    patron += '<a href="([^"]+)"[^>]+>[^<]+'
    patron += '<img src="([^"]+)"[^>]+>[^<]+'
    patron += '</a>[^<]+'
    patron += '</div>[^<]+'
    patron += '<h5 class="programs_list_az_item_name">[^<]+'
    patron += '<a[^>]+>(.*?)</a>[^<]+'
    patron += '</h5>[^<]+'
    patron += '<p class="programs_list_az_item_description">([^<]+)</p>[^<]+'
    patron += '</div>[^<]+'
    patron += '</li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = match[2].strip()
        scrapedurl = match[0]
        scrapedthumbnail = match[1]
        scrapedplot = scrapertools.htmlclean(match[3].strip())
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, plot=scrapedplot , show=scrapedtitle, viewmode="movie_with_plot") )

    next_page = scrapertools.find_single_match(data,'<a href="([^"]+)"  class="enlace siguiente"')
    if next_page!="":
        itemlist.append( Item(channel=CHANNELNAME, title=">> Página siguiente" , action="programas" , url=urlparse.urljoin(item.url,next_page), folder=True ))

    return itemlist

def episodios(item):
    logger.info("[rtva.py] episodios")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    '''
    <div class="video_item capaseccionl">
    <div class="media capaseccionl">
    <span class="">
    <a href="http://www.canalsuralacarta.es/television/video/jamaica/2590/12" title="Jamaica">
    <img class="no_foto" src="http://www.canalsuralacarta.es/pictures/2829/picture2829_20110511_093437_crop1sub1.jpg" width="212" height="119" alt="Jamaica" />
    </a>
    </span>
    <span class="video_mosca">
    <a href="http://www.canalsuralacarta.es/television/video/jamaica/2590/12" title="Jamaica">
    <img src="./img/1pxtrans.gif" width="212" height="119" alt="Jamaica" />
    </a>
    </span>
    </div>
    <div class="text_content capaseccionl">
    <h5 class="media_name"><a href="http://www.canalsuralacarta.es/television/video/jamaica/2590/12" title="Jamaica">Jamaica</a></h5>
    <h6 style="position: absolute; right: 2pt; bottom: 2pt; color: #000;">10/05/2011</h6>
    </div>
    '''
    patron  = '<div class="video_item capaseccionl">[^<]+'
    patron += '<div class="media capaseccionl">[^<]+'
    patron += '<span class="">[^<]+'
    patron += '<a href="([^"]+)"[^>]+>[^<]+'
    patron += '<img class="no_foto" src="([^"]+)"[^>]+>.*?'
    patron += '<h5 class="media_name"><a[^>]+>([^<]+)</a></h5>[^<]+'
    patron += '<h6[^>]+>([^<]+)</h6>[^<]+'
    patron += '</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for match in matches:
        # Datos
        scrapedtitle = match[2] + " (" + match[3] + ")"
        scrapedurl = match[0]
        scrapedthumbnail = match[1]
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle + " " + scrapedplot , action="play" , url=scrapedurl, page = scrapedurl , thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show , folder=False) )

    patron = '<a href="([^"]+)"  class="enlace siguiente"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)>0:
        logger.info("[rtva.py] Página siguiente: "+matches[0])
        item = Item(url=matches[0], show=item.show)
        itemlist.extend(episodios(item))

    return itemlist

def play(item):
    logger.info("[rtva.py] play")

    url = item.url

    # Descarga pagina detalle
    #http://www.canalsuralacarta.es/television/video/jamaica/2590/12
    #_url_xml_datos=http://www.canalsuralacarta.es/webservice/video/2590"
    data = scrapertools.cachePage(url)
    patron = '_url_xml_datos=([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)>0:
        url = urlparse.urljoin(url,matches[0])
    logger.info("[rtva.py] url="+url)

    # Extrae la URL del video
    #http://ondemand.rtva.ondemand.flumotion.com/rtva/ondemand/flash8/programas/andaluces-por-el-mundo/20110509112657-7-andaluces-por-el-mundo-jamaica-10-05-11.flv
    #http://ondemand.rtva.ondemand.flumotion.com/rtva/ondemand/flash8/programas/andaluces-por-el-mundo/20110509112657-7-andaluces-por-el-mundo-jamaica-10-05-11.flv
    data = scrapertools.cachePage(url)
    patron = '<url>([^<]+)</url>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    if len(matches)>0:
        url = matches[len(matches)-1]

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , server="directo" , url=url, thumbnail=item.thumbnail, plot=item.plot , show=item.show , folder=False) )

    return itemlist

def test():

    programas_items = mainlist(Item())
    if len(programas_items)==0:
        print "No devuelve programas en "+categorias_items[0]
        return False

    episodios_items = episodios(programas_items[0])
    if len(episodios_items)==1:
        print "No devuelve videos en "+programas_items[0].title
        return False

    return True