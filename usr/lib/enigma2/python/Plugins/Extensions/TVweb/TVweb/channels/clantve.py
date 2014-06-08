# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Clan TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re

from core import logger
from core import scrapertools
from core.item import Item

DEBUG = True
CHANNELNAME = "clantve"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.clantv mainlist")

    itemlist = []
    itemlist.append( Item(channel=CHANNELNAME, title="Últimos vídeos añadidos" , url="http://www.rtve.es/infantil/components/TE_INFDEF/videos/videos-1.inc" , action="ultimos_videos" , folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Todos los programas" , url="http://www.rtve.es/infantil/series/" , action="programas" , folder=True) )

    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.clantv programas")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae los programas
    patron  = '<div class="informacion-serie">[^<]+'
    patron += '<h3>[^<]+'
    patron += '<a href="([^"]+)">([^<]+)</a>[^<]+'
    patron += '</h3>[^<]+'
    patron += '<a[^>]+>[^<]+</a><img.*?src="([^"]+)"><div>(.*?)</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = match[1]
        scrapedtitle = scrapertools.unescape(scrapedtitle)
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedurl = urlparse.urljoin(scrapedurl,"videos")
        scrapedthumbnail = urlparse.urljoin(item.url,match[2])
        scrapedplot = match[3]
        scrapedplot = scrapertools.unescape(scrapedplot).strip()
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()

        scrapedpage = urlparse.urljoin(item.url,match[0])
        if (DEBUG): logger.info("scraped title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"] plot=["+scrapedplot+"]")
        #logger.info(scrapedplot)

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , page=scrapedpage, show=scrapedtitle , folder=True) )

    # Añade el resto de páginas
    next_page = scrapertools.find_single_match(data,'<li class="siguiente">[^<]+<a rel="next" title="Ir a la p&aacute;gina siguiente" href="([^"]+)">Siguiente')
    if next_page!="":
        itemlist.append(Item(channel=CHANNELNAME,action="programas",title=">> Página siguiente",url=urlparse.urljoin(item.url,next_page), folder=True))

    return itemlist

def detalle_programa(item):
    
    #http://www.rtve.es/infantil/series/monsuno/videos/
    #http://www.rtve.es/infantil/series/hay-nuevo-scooby-doo/
    url = item.url
    if url.endswith("/videos"):
        url = url.replace("/videos","")
    
    # Descarga la página
    print "url="+url
    data = scrapertools.cache_page(url)
    data = scrapertools.get_match(data,'<div class="contenido-serie">(.*?</div>)')
    print "data="+data

    # Obtiene el thumbnail
    try:
        item.thumbnail = scrapertools.get_match(data,'<img.*?src="([^"]+)"')
    except:
        pass

    try:
        item.plot = scrapertools.htmlclean( scrapertools.get_match(data,'<div>(.*?)</div>') ).strip()
    except:
        pass

    try:
        title = scrapertools.get_match(data,'<h3>[^<]+<a[^>]+>([^<]+)</a>[^<]+</h3>').strip()
        item.title = scrapertools.entityunescape(title)
    except:
        pass

    return item

def episodios(item):
    logger.info("tvalacarta.channels.clantv episodios")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae los capítulos
    patron = '<div class="contenido-serie">(.*?)</div>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    logger.info("tvalacarta.channels.clantv encontrados %d episodios" % len(matches) )
    if len(matches)==0:
        return itemlist
    data2 = matches[0]

    itemlist = videos(item,data2)

    # Añade el resto de páginas
    patron = '<li class="siguiente"><a rel="next" title="Ir a la p&aacute;gina siguiente" href="([^"]+)">Siguiente</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches)>0:
        match = matches[0]
        item.url = urlparse.urljoin(item.url,match)
        itemlist.extend(episodios(item))

    from core import config
    if (config.get_platform().startswith("xbmc") or config.get_platform().startswith("boxee")) and len(itemlist)>0:
        itemlist.append( Item(channel=item.channel, title=">> Opciones para esta serie", url=item.url, action="serie_options##episodios", thumbnail=item.thumbnail, show=item.show, folder=False))

    return itemlist

def ultimos_videos(item):
    logger.info("tvalacarta.channels.clantv ultimos_videos")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    itemlist = videos(item,data)
    #http://www.rtve.es/infantil/components/TE_INFDEF/videos/videos-1.inc
    #http://www.rtve.es/infantil/components/TE_INFDEF/videos/videos-2.inc
    #...
    current_page = scrapertools.find_single_match(item.url,"videos-(\d+).inc$")
    next_page = str(int(current_page)+1)
    next_page_url = item.url.replace("videos-"+current_page+".inc","videos-"+next_page+".inc")
    itemlist.append( Item(channel=item.channel, title=">> Página siguiente", url=next_page_url, action="ultimos_videos", folder=True))

    return itemlist

def videos(item,data2):
    logger.info("tvalacarta.channels.clantv videos")
    logger.info("tvalacarta.channels.clantv data2="+data2)

    itemlist = []

    patron = '<a rel="([^"]+)".*?href="([^"]+)"><img src="([^"]+)"[^>]+>(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data2)
    scrapertools.printMatches(matches)

    # Extrae los items
    for match in matches:
        scrapedtitle = match[3]
        scrapedtitle = scrapertools.unescape(scrapedtitle)
        scrapedtitle = scrapertools.htmlclean(scrapedtitle)
        scrapedtitle = unicode(scrapedtitle,"utf-8").capitalize().encode("utf-8")
        
        # La página del vídeo
        scrapedpage = urlparse.urljoin(item.url,match[1])
        scrapedpage = scrapedpage.replace("videos-juegos/videos","videos-juegos/#/videos")
        
        # Código de la serie
        scrapedcode = match[0]
        
        # Url de la playlist
        scrapedurl = "http://www.rtve.es/infantil/components/"+scrapedcode+"/videos.xml.inc"
        scrapedthumbnail = urlparse.urljoin(item.url,match[2])
        scrapedplot = ""
        if (DEBUG): logger.info("scraped title=["+scrapedtitle+"], url=["+scrapedurl+"], page=["+scrapedpage+"] thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , server="directo", page=scrapedpage, url=scrapedurl, thumbnail=scrapedthumbnail, fanart=scrapedthumbnail, show=item.show , plot=scrapedplot , viewmode="movie_with_plot", folder=False) )

    # Ahora extrae el argumento y la url del vídeo
    dataplaylist = scrapertools.cachePage(scrapedurl)
    
    for episodeitem in itemlist:
        partes = episodeitem.page.split("/")
        code = partes[len(partes)-2]
        patron  = '<video id="'+code+'".*?url="([^"]+)".*?'
        patron += '<sinopsis>(.*?)</sinopsis>'
        matches = re.compile(patron,re.DOTALL).findall(dataplaylist)

        if len(matches)>0:
            episodeitem.url = urlparse.urljoin(item.url,matches[0][0])
            episodeitem.plot = matches[0][1]

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # El canal tiene estructura programas -> episodios -> play
    menu_itemlist = mainlist(Item())

    items_programas = programas(menu_itemlist[1])
    if len(items_programas)==0:
        print "No hay programas"
        return False

    items_episodios = episodios(items_programas[0])
    if len(items_episodios)==0:
        print "No hay episodios en "+items_programas[0].tostring()
        return False

    items_novedades = ultimos_videos(menu_itemlist[0])
    if len(items_novedades)==0:
        print "No hay nada en ultimos-episodios"
        return False

    return bien
