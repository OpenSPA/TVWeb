# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para yaske
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "yaske"
__category__ = "F"
__type__ = "generic"
__title__ = "yaske.net"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("pelisalacarta.yaske mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Novedades"          , action="peliculas",       url="http://www.yaske.net/"))
    itemlist.append( Item(channel=__channel__, title="Por año"            , action="menu_anyos",       url="http://www.yaske.net/"))
    itemlist.append( Item(channel=__channel__, title="Por género"         , action="menu_categorias", url="http://www.yaske.net/"))
    itemlist.append( Item(channel=__channel__, title="Por calidad"        , action="menu_calidades",  url="http://www.yaske.net/"))
    itemlist.append( Item(channel=__channel__, title="Por idioma"         , action="menu_idiomas",    url="http://www.yaske.net/"))
    itemlist.append( Item(channel=__channel__, title="Buscar"             , action="search") )

    return itemlist

def search(item,texto):

    logger.info("pelisalacarta.yaske search")
    itemlist = []

    try:
        item.url = "http://www.yaske.net/es/peliculas/search/%s"
        item.url = item.url % texto
        item.extra = ""
        itemlist.extend(peliculas(item))
        itemlist = sorted(itemlist, key=lambda Item: Item.title) 

        return itemlist

    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def peliculas(item):
    logger.info("pelisalacarta.yaske listado")

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas
    '''
    <li class="item-movies c5">
    <a class="image-block" href="http://www.yaske.net/es/pelicula/0002014/ver-sometimes-in-april-online.html" title="Siempre en abril">
    <img src="http://t0.gstatic.com/images?q=tbn:ANd9GcSpMMsdPI9tKkvdHUA2qPknXygXuHaISe7FRgYM85zvPZhr1tbWDA" width="140" height="200" />
    </a>
    <ul class="bottombox">
    <li title="Siempre en abril"><a href="http://www.yaske.net/es/pelicula/0002014/ver-sometimes-in-april-online.html" title="Siempre en abril">Siempre en abril</a></li>
    <li>Drama, Guerra, Historica</li>
    <li><img src='http://www.yaske.net/theme/01/data/images/flags/la_la.png' title='Latino ' width='25'/> <img src='http://www.yaske.net/theme/01/data/images/flags/en_es.png' title='English SUB Spanish' width='25'/> </li>
    <li><a rel="lyteframe" rev="width: 600px; height: 380px; scrolling: no;" youtube="trailer" href="http://www.youtube.com/v/XiteY6o2UwI&amp;hl&amp;autoplay=1" target="_blank"><img src="http://4.bp.blogspot.com/-_t9RtdUMJlo/UgYO_qA49VI/AAAAAAAABj4/7O_ZrYtIMHw/s1600/vertrailer2.png" height="22" border="0"></a></li>
    </ul>
    <div class="quality">Dvd Rip</div>
    <div class="view"><span>view: 10800</span></div>
    </li>   
    '''
    patron  = '<li class="item-movies[^<]+'
    patron += '<a class="image-block" href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)" width="\d+" height="\d+"[^<]+'
    patron += '</a[^<]+'
    patron += '<ul class="bottombox"[^<]+'
    patron += '<li[^<]+<a[^<]+</a></li[^<]+'
    patron += '<li[^<]+</li[^<]+'
    patron += "<li>(.*?)</li[^<]+"
    patron += '<li><a[^<]+<img[^<]+</a></li[^<]+'
    patron += '</ul[^<]+'
    patron += '<div class="quality">([^<]+)<'



    matches = re.compile(patron,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    itemlist = []

    for scrapedurl, scrapedtitle, scrapedthumbnail, idiomas, calidad in matches:

        patronidiomas = "<img src='[^']+' title='([^']+)'"
        matchesidiomas = re.compile(patronidiomas,re.DOTALL).findall(idiomas)
        idiomas_disponibles = ""
        for idioma in matchesidiomas:
            idiomas_disponibles = idiomas_disponibles + idioma.strip() + "/"
        if len(idiomas_disponibles)>0:
            idiomas_disponibles = "["+idiomas_disponibles[:-1]+"]"
        
        title = scrapedtitle.strip()+" "+idiomas_disponibles+"["+calidad+"]"
        title = scrapertools.htmlclean(title)
        url = scrapedurl
        thumbnail = scrapedthumbnail
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title , url=url , thumbnail=thumbnail , plot=scrapedplot , fulltitle=scrapertools.htmlclean(scrapedtitle.strip()), viewmode="movie", folder=True) )

    # Extrae el paginador
    patronvideos  = "<a href='([^']+)'>\&raquo\;</a>"
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="peliculas", title=">> Página siguiente" , url=scrapedurl , folder=True) )

    return itemlist

def menu_categorias(item):
    logger.info("pelisalacarta.yaske menu_categorias")

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)
    data = scrapertools.get_match(data,'div class="title">Categoria[^<]+</div>(.*?)</ul>')
    logger.info("data="+data)

    # Extrae las entradas
    patron  = "<li><a href='([^']+)'><img[^>]+>([^<]+)</a>"
    matches = re.compile(patron,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    itemlist = []

    for scrapedurl,scrapedtitle in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

def menu_idiomas(item):
    logger.info("pelisalacarta.yaske menu_idiomas")

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)

    data = scrapertools.get_match(data,'<select name="language"(.*?)</select>')
    logger.info("data="+data)

    # Extrae las entradas
    patron  = "<option value='([^']*)'>([^<]+)</option>"
    matches = re.compile(patron,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    itemlist = []

    for scrapedurl,scrapedtitle in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        url = "http://www.yaske.net/es/peliculas/custom/?year=&gender=&quality=&language="+scrapedurl
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=url , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    url = "http://www.yaske.net/es/peliculas/custom/?year=&gender=&quality=&language=sub"
    itemlist.append( Item(channel=__channel__, action="peliculas", title="Subtitulado" , url=url , folder=True) )

    return itemlist

def menu_anyos(item):
    logger.info("pelisalacarta.yaske menu_anyos")

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)

    data = scrapertools.get_match(data,'<select name="year"(.*?)</select>')
    logger.info("data="+data)

    # Extrae las entradas
    patron  = "<option value='([^']+)'>([^<]+)</option>"
    matches = re.compile(patron,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    itemlist = []

    for scrapedurl,scrapedtitle in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        url = "http://www.yaske.net/es/peliculas/custom/?year="+scrapedurl+"&gender=&quality=&language="
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=url , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

def menu_calidades(item):
    logger.info("pelisalacarta.yaske menu_calidades")

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)

    '''
    <select name="quality" id="qualities" class="jqlist">
    <option value="" selected="selected">Selecciona...</option>
    <option value='c8'>hd real 720</option><option value='c7'>hd rip 320</option><option value='c6'>br-screener</option><option value='c5'>dvd rip</option><option value='c4'>dvd screener</option><option value='c3'>ts screener hq</option><option value='c2'>ts screener</option><option value='c1'>cam</option> </select></td>
    </tr>
    '''
    data = scrapertools.get_match(data,'<select name="quality"(.*?)</select>')
    logger.info("data="+data)

    # Extrae las entradas
    patron  = "<option value='([^']+)'>([^<]+)</option>"
    matches = re.compile(patron,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    itemlist = []

    for scrapedurl,scrapedtitle in matches:
        scrapedthumbnail = ""
        scrapedplot = ""
        url = "http://www.yaske.net/es/peliculas/custom/?year=&gender=&quality="+scrapedurl+"&language="
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+url+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=url , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

    return itemlist

def findvideos(item):
    logger.info("pelisalacarta.yaske findvideos url="+item.url)

    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae las entradas
    '''
    <tr bgcolor="">
    <td height="32" align="center"><a class="btn btn-mini enlace_link" style="text-decoration:none;" rel="nofollow" target="_blank" title="Ver..." href="http://www.yaske.net/es/reproductor/pelicula/2141/44446/"><i class="icon-play"></i><b>&nbsp; Opcion &nbsp; 04</b></a></td>
    <td align="left"><img src="http://www.google.com/s2/favicons?domain=played.to"/>played</td>
    <td align="center"><img src="http://www.yaske.net/theme/01/data/images/flags/la_la.png" width="21">Lat.</td>
    <td align="center" class="center"><span title="" style="text-transform:capitalize;">hd real 720</span></td>
    <td align="center"><div class="star_rating" title="HD REAL 720 ( 5 de 5 )">
    <ul class="star"><li class="curr" style="width: 100%;"></li></ul>
    </div>
    </td> <td align="center" class="center">2553</td> </tr>
    '''
    patron  = '<tr bgcolor=(.*?)</tr>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    #scrapertools.printMatches(matches)
    itemlist = []

    n = 1
    for tr in matches:
        logger.info("tr="+tr)
        try:
            title = scrapertools.get_match(tr,'<b>([^<]+)</b>')
            server = scrapertools.get_match(tr,'"http\://www.google.com/s2/favicons\?domain\=([^"]+)"')
            # <td align="center"><img src="http://www.yaske.net/theme/01/data/images/flags/la_la.png" width="19">Lat.</td> 
            idioma = scrapertools.get_match(tr,'<img src="http://www.yaske.[a-z]+/theme/01/data/images/flags/([a-z_]+).png"[^>]+>[^<]*<')
            subtitulos = scrapertools.get_match(tr,'<img src="http://www.yaske.[a-z]+/theme/01/data/images/flags/[^"]+"[^>]+>([^<]*)<')
            calidad = scrapertools.get_match(tr,'<td align="center" class="center"[^<]+<span title="[^"]*" style="text-transform.capitalize.">([^<]+)</span></td>')
            
            #<a href="http://www.yaske.net/es/reproductor/pelicula/2244/15858/" title="Batman: El regreso del Caballero Oscuro, Parte 2"
            # 01-08-2014 - Comentado
            #url = scrapertools.get_match(tr,'<a.*?href="([^"]+)"')
            # 01-08-2014 - Añadido
            #<a [....] href="http://www.yaske.net/goto/" data-key="WZmWd6z1zkcEmlesZzItESWI+720osvEeKsY+NXtLxI=">
            data_key = scrapertools.get_match(tr,'<a.*?data-key="([^"]+)"')
            url = scrapertools.get_match(tr,'<a.*?href="([^"]+)"')+"|"+data_key
            thumbnail = ""
            plot = ""

            title = title.replace("&nbsp;","")

            if "es_es" in idioma:
                scrapedtitle = title + " en "+server.strip()+" [Español]["+calidad+"]"
            elif "la_la" in idioma:
                scrapedtitle = title + " en "+server.strip()+" [Latino]["+calidad+"]"
            elif "en_es" in idioma:
                scrapedtitle = title + " en "+server.strip()+" [Inglés SUB Español]["+calidad+"]"
            else:
                scrapedtitle = title + " en "+server.strip()+" ["+idioma+" / "+subtitulos+"]["+calidad+"]"
            scrapedtitle = scrapertools.entityunescape(scrapedtitle)
            scrapedtitle = scrapedtitle.strip()
            scrapedurl = url
            scrapedthumbnail = thumbnail
            scrapedplot = plot
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
            if config.get_platform().startswith("xbmc") or config.get_platform().startswith("boxee"):
                itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , fulltitle=item.fulltitle , folder=False) )
            else:
                
                itemlist.append( Item(channel=__channel__, action="play", title=scrapedtitle , url=scrapedurl.split("|")[0] , thumbnail=scrapedthumbnail , plot=scrapedplot , fulltitle=item.fulltitle , extra=scrapedurl.split("|")[1] , folder=False) )
            n += 1
        except:
            import traceback
            logger.info("Excepcion: "+traceback.format_exc())

    return itemlist

def play(item):
    logger.info("pelisalacarta.yaske play item.url="+item.url)
    
    itemlist=[]

    # 01-08-2014 - Añadido
    if config.get_platform().startswith("xbmc") or config.get_platform().startswith("boxee"):
        url = item.url.split("|")[0]
        values = {'url': item.url.split("|")[1]}
    else:
        url = item.url
        values = {'url': item.extra}
    post = urllib.urlencode(values)
    request = urllib2.Request(url,post)
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)')
    response = urllib2.urlopen(request)
    data = response.read()
    response.close()

    # 01-08-2014 - Comentado
    '''
    if item.url.startswith("http://adf.ly"):
        from servers import adfly
        item.url = adfly.get_long_url(item.url)

    #data = scrapertools.downloadpageGzip(item.url)
    #logger.info("data="+data)

    data = data.replace("http://www.yaske.net/archivos/allmyvideos/play.php?v=","http://allmyvideos.net/")
    '''

    itemlist = servertools.find_video_items(data=data)
    for newitem in itemlist:
        newitem.fulltitle = item.fulltitle
    
    return itemlist


# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    peliculas_items = peliculas(mainlist_items[0])
    bien = False
    for pelicula_item in peliculas_items:
        mirrors = findvideos( item=pelicula_item )
        if len(mirrors)>0:
            bien = True
            break

    return bien