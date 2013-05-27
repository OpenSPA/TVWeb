# -*- coding: iso-8859-1 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para cartoonito
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import scrapertools
from core.item import Item

logger.info("[cartoonito.py] init")

DEBUG = True
CHANNELNAME = "cartoonito"
MAIN_URL = "http://cartoonito.cartoonnetwork.es/videos"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[cartoonito.py] mainlist")
    item.url = MAIN_URL
    return series(item)

def series(item):
    logger.info("[cartoonito.py] series")
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    logger.info(data)

    # Extrae las series
    '''
    <div id="views_slideshow_singleframe_main_navigation_filter_view-block_1-4" class="views_slideshow_singleframe_main views_slideshow_main">
    <div id="views_slideshow_singleframe_teaser_section_navigation_filter_view-block_1-4" class="views_slideshow_singleframe_teaser_section">
    <div class="views_slideshow_singleframe_slide views_slideshow_slide views-row-1 views-row-odd" id="views_slideshow_singleframe_div_navigation_filter_view-block_1-4_0">
    <div class="views-row views-row-0 views-row-first views-row-odd">
    <a href="/serie/baby-looney-tunes/videos"><img src="http://cartoonito.cartoonnetwork.es/sites/cartoonito.cartoonnetwork.es/files/imagecache/intra_nav/babyLooneyTunes.png" alt="" title=""  class="imagecache imagecache-intra_nav imagecache-default imagecache-intra_nav_default" width="48" height="48" /></a>
    </div>
    <div class="views-row views-row-1 views-row-even">
    <a href="/serie/bananas-en-pijama/videos"><img src="http://cartoonito.cartoonnetwork.es/sites/cartoonito.cartoonnetwork.es/files/imagecache/intra_nav/bananasInPjs.png" alt="" title=""  class="imagecache imagecache-intra_nav imagecache-default imagecache-intra_nav_default" width="48" height="48" /></a>
    </div>
    <div class="views-row views-row-2 views-row-odd">
    <a href="/serie/bucea-olly/videos"><img src="http://cartoonito.cartoonnetwork.es/sites/cartoonito.cartoonnetwork.es/files/imagecache/intra_nav/diveOllyDive.png" alt="" title=""  class="imagecache imagecache-intra_nav imagecache-default imagecache-intra_nav_default" width="48" height="48" /></a>
    </div>
    <div class="views-row views-row-3 views-row-even">
    <a href="/serie/escuela-de-bomberos/videos"><img src="http://cartoonito.cartoonnetwork.es/sites/cartoonito.cartoonnetwork.es/files/imagecache/intra_nav/firehouse-tales-carousel.png" alt="" title=""  class="imagecache imagecache-intra_nav imagecache-default imagecache-intra_nav_default" width="48" height="48" /></a>
    </div>
    </div>
    </div>
    </div>
    '''
    data = scrapertools.get_match(data,'<div id="views_slideshow_singleframe_main_navigation_filter_view-block_1-4"(.*?)</div>[^<]+</div>[^<]+</div>[^<]+</div>')
    patron  = '<div class="views-row[^<]+'
    patron += '<a href="([^"]+)"><img src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    for url,thumbnail in matches:
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedtitle = url.replace("/serie/","").replace("/videos","").replace("-"," ").capitalize()
        scrapedthumbnail = thumbnail
        itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="episodios" , url=urlparse.urljoin(item.url,scrapedurl), thumbnail=scrapedthumbnail , show = scrapedtitle, folder=True) )

    return itemlist

def episodios(item):
    logger.info("[cartoonito.py] episodios")

    # Descarga la página
    #http://www.boing.es/serie/hora-de-aventuras
    #http://www.boing.es/videos/hora-de-aventuras
    data = scrapertools.cachePage(item.url)
    #logger.info(data)

    # Extrae los videos
    '''
    <div class="im">
    <a href="/serie/escuela-de-bomberos/videos/una-fant%C3%A1stica-captura">
    <img src="http://i.cdn.turner.com/tbseurope/big/Cartoonito_ES/thumbs/ES_CP_FIRCLP0012_01.jpg" class="video-thumbnail"/>
    </a>
    </div>
    </div>
    <h3>
    <span class="ie7vcent">
    <a href="/serie/escuela-de-bomberos/videos/una-fant%C3%A1stica-captura">
    Escuela de Bomberos video - Una fantástica captura</a>
    </span>
    </h3>
    '''
    patron  = '<div class="im">[^<]+'
    patron += '<a href="([^"]+)">[^<]+'
    patron += '<img src="([^"]+)" class="video-thumbnail"/>[^<]+'
    patron += '</a>[^<]+'
    patron += '</div>[^<]+'
    patron += '</div>[^<]+'
    patron += '<h3>[^<]+'
    patron += '<span class="ie7vcent">[^<]+'
    patron += '<a href="[^"]+">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    #if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for url,thumbnail,title in matches:
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedtitle = title.strip()
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play", server="cartoonito" , url=urlparse.urljoin(item.url,scrapedurl), thumbnail=scrapedthumbnail, page=item.url, show = item.show, folder=False) )

    # Extrae el resto de vídeos
    '''
    <span class="ie7vcent">
    <a href="/serie/escuela-de-bomberos/videos/graves-problemas">
    Escuela de Bomberos video - Graves problemas    </a>
    </span>
    </h3>
    <div class="im"><img src="http://i.cdn.turner.com/tbseurope/big/Cartoonito_ES/thumbs/ES_CP_FIRCLP0011_01.jpg" class="video-thumbnail"/></div>
    '''
    patron  = '<span class="ie7vcent">[^<]+'
    patron += '<a href="([^"]+)">([^<]+)</a>[^<]+'
    patron += '</span>[^<]+'
    patron += '</h3>[^<]+'
    patron += '<div class="im"><img src="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    #if DEBUG: scrapertools.printMatches(matches)

    for url,title,thumbnail in matches:
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedtitle = title.strip()
        scrapedthumbnail = urlparse.urljoin(item.url,thumbnail)
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play", server="cartoonito" , url=urlparse.urljoin(item.url,scrapedurl), thumbnail=scrapedthumbnail, page=item.url, show = item.show, folder=False) )

    return itemlist

def test():
    itemsmainlist = mainlist(None)
    for item in itemsmainlist: print item.tostring()

    itemsseries = series(itemsmainlist[1])
    itemsepisodios = episodios(itemsseries[4])

if __name__ == "__main__":
    test()
