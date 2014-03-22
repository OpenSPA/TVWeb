# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para peliculaspepito
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "peliculaspepito"
__category__ = "S"
__type__ = "generic"
__title__ = "Peliculaspepito"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[peliculaspepito.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="peliculas"    , title="novedades", url="http://www.peliculaspepito.com"))
    itemlist.append( Item(channel=__channel__, action="listalfabetico"   , title="Listado alfabético"))
    itemlist.append( Item(channel=__channel__, action="search"   , title="Buscar"))
 
    return itemlist

def search(item,texto):
    texto = texto.replace("+","-")
    itemlist = []
    item.url = "http://www.peliculaspepito.com/buscador/" + texto
    itemlist.extend(peliculas(item))
    return itemlist

def peliculas(item):
    logger.info("[peliculaspepito.py] novedades")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<ul class="lista_peliculas">(.*?)</ul>')
    
    '''
    <li><a class="tilcelpel" title="Emperador" href="http://emperador.peliculaspepito.com/"><img id="img_13266" data-id="13266" alt="Emperador" src="http://s.peliculaspepito.com/peliculas/13266-emperador-thumb.jpg" /></a><div class="pfestrenoportada"><span class="text-warning">07-03-2014</span></div><div id="imgtilinfo13266" class="til_info"><p><a title="Emperador" href="http://emperador.peliculaspepito.com/">Emperador</a></p><p class="pcalidi"><span class="flag flag_0"></span></p><p class="pidilis">DVD/BR&nbsp;Screener</p></div><a title="Emperador" href="http://emperador.peliculaspepito.com/"><div data-id="13266" id="til_info_sensor13266" data-on="0" data-an="0" class="til_info_sensor"></div></a></li>
    '''
    patron  = '<li[^<]+'
    patron += '<a class="tilcelpel" title="([^"]+)" href="([^"]+)"[^<]+'
    patron += '<img id="[^"]+" data-id="[^"]+" alt="[^"]+" src="([^"]+)"[^>]+>.*?'
    patron += '<p class="pcalidi"><span class="([^"]+)"></span></p><p class="pidilis">([^<]+)</p>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist = []
    for scrapedtitle,scrapedurl,scrapedthumbnail,idiomas,calidad in matches:
        logger.info("title="+scrapedtitle)
        title = scrapertools.htmlclean(scrapedtitle).strip()
        title = title.replace("\r","").replace("\n","")
        #title = unicode( title, "iso-8859-1" , errors="replace" ).encode("utf-8")
        #title = re.compile("\s+",re.DOTALL).sub(" ",title)
        logger.info("title="+title)
	calidad = scrapertools.htmlclean(calidad).strip()

        if "flag_0" in idiomas:
            title = title + " (Español)"
        if "flag_1" in idiomas:
            title = title + " (Latino)"
        if "flag_2" in idiomas:
            title = title + " (VO)"
        if "flag_3" in idiomas:
            title = title + " (VOS)"

	title = title + "["+calidad+"]"

        url = scrapedurl
        thumbnail = scrapedthumbnail
        plot = ""
        plot = unicode( plot, "iso-8859-1" , errors="replace" ).encode("utf-8")

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, show=title, viewmode="movie"))

    return itemlist


def listalfabetico(item):
    logger.info("[peliculaspepito.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="pelis" , title="0-9",url="http://www.peliculaspepito.com/lista-peliculas/num/"))
    for letra in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']:
        itemlist.append( Item(channel=__channel__, action="pelis" , title=letra,url="http://www.peliculaspepito.com/lista-peliculas/"+letra.lower()+"/"))

    return itemlist

def pelis(item):
    logger.info("[peliculaspepito.py] pelis")

    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<ul class="ullistadoalfa">(.*?)</ul>')

    patron = '<li><a title="([^"]+)" href="([^"]+)"[^<]+</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    itemlist = []
    for scrapedtitle,scrapedurl in matches:
        #title = unicode( scrapedtitle.strip(), "iso-8859-1" , errors="replace" ).encode("utf-8")
        title = scrapedtitle.strip()
        url = scrapedurl
        thumbnail = ""
        plot = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title , url=url, thumbnail=thumbnail, plot=plot, show=title,viewmode="movie"))

    return itemlist


def detalle_programa(item,data=""):
    if data=="":
        data = scrapertools.cachePage(item.url)
    
    try:
        data2 = scrapertools.get_match(data,'<img class="imgcolpelicula" alt="[^"]+" src="([^"]+)"')
        item.thumbnail = data2.replace("%20"," ")
    except:
        pass

    # Argumento
    try:
        data2 = scrapertools.get_match(data,'<div id="ph_sinopsis">(.*?)</div>')
        item.plot = scrapertools.htmlclean(data2)
    except:
        pass

    return item


def findvideos(item):
    logger.info("[peliculaspepito.py] findvideos")
    itemlist = []

    # Descarga la pagina
    data = scrapertools.cachePage(item.url)

    # Completa plot y thumbnail
    item = detalle_programa(item,data)

    data = scrapertools.get_match(data,'div class="t_titulo">Ver Online(.*?)</table>')

    #logger.info(data)
    '''
    <tr>
    <td class="tdidioma"><span class="flag flag_2"></span></td>
    <td>25/06/2012</td>
    <td class="tdservidor"><img src="http://www.peliculaspepito.com/uploads/servidores/76-imagen_img.png" alt="Moevideos" />&nbsp;Moevideos</td>
    <td class="tdenlace"><a class="btn btn-mini enlace_link" rel="nofollow" target="_blank" title="Ver..." href="http://falling-skies.peliculaspepito.com/temporada-2/capitulo-3/385944/"><i class="icon-play"></i>&nbsp;&nbsp;Ver</a></td>
    <td class="tdusuario"><a id="a_ava_71" href="http://www.peliculaspepito.com/usuarios/perfil/d02560dd9d7db4467627745bd6701e809ffca6e3">mater</a></td>
    <td class="tdcomentario"></td>
    <td class="tdreportar"><button class="btn btn-danger btn-mini hide sptt breportar" data-tt_my="left center" data-tt_at="right center" data-tt_titulo="Reportar problemas..." data-tt_texto="¿Algún problema con el enlace?, ¿esta roto?, ¿el audio esta mal?, ¿no corresponde el contenido?, repórtalo y lo revisaremos, ¡gracias!." data-enlace="385944" type="button"><i class="icon-warning-sign icon-white"></i></button></td>
    </tr>
    '''
    '''
    <tr>
    <td class="tdidioma"><span class="flag flag_3"></span></td>
    <td>28/12/2011</td>
    <td class="tdservidor"><img src="http://www.peliculaspepito.com/uploads/servidores/44-imagen_img.png" alt="Uploaded" />&nbsp;Uploaded</td>
    <td class="tdenlace"><a class="btn btn-mini enlace_link" rel="nofollow" target="_blank" title="Bajar..." href="http://rizzoli-and-isles.peliculaspepito.com/temporada-2/capitulo-15/329503/"><i class="icon-download"></i>&nbsp;Bajar</a></td>
    <td class="tdusuario"><a href="http://www.peliculaspepito.com/usuarios/perfil/9109c85a45b703f87f1413a405549a2cea9ab556">Pepito</a></td>
    <td class="tdcomentario"></td>
    <td class="tdreportar"><button class="btn btn-danger btn-mini hide sptt breportar" data-tt_my="left center" data-tt_at="right center" data-tt_titulo="Reportar problemas..." data-tt_texto="¿Algún problema con el enlace?, ¿esta roto?, ¿el audio esta mal?, ¿no corresponde el contenido?, repórtalo y lo revisaremos, ¡gracias!." data-enlace="329503" type="button"><i class="icon-warning-sign icon-white"></i></button></td>
    '''
    # Listas de enlaces
    patron  = '<tr[^<]+'
    patron += '<td class="tdidioma"><span class="([^"]+)".*?'
    patron += '<td class="tdcalidad">([^<]+).*?'
    patron += '<td class="tdservidor"><img src="([^"]+)"[^>]+>([^<]+)</td[^<]+'
    # patron += '<td class="tdenlace"><a class="btn btn-mini enlace_link" data-servidor="([^"]+)" rel="nofollow" target="_blank" title="[^"]+" href="([^"]+)"'
    patron += '<td class="tdenlace"><a class="btn btn_link" data-servidor="([^"]+)" rel="nofollow" target="_blank" title="[^"]+" href="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for idiomas,calidad,scrapedthumbnail,servidor,dataservidor,scrapedurl in matches:
        url = urlparse.urljoin(item.url,scrapedurl)
        title = "Ver en "+scrapertools.entityunescape(servidor).strip()
        plot = ""

        if "flag_0" in idiomas:
            title = title + " (Español)"
        if "flag_1" in idiomas:
            title = title + " (Latino)"
        if "flag_2" in idiomas:
            title = title + " (VO)"
        if "flag_3" in idiomas:
            title = title + " (VOS)"

	title = title + "["+calidad+"]"

        itemlist.append( Item(channel=__channel__, action="play" , title=title , url=url, thumbnail=item.thumbnail, plot=item.plot, show=item.show, folder=False,fanart="http://pelisalacarta.mimediacenter.info/fanart/peliculaspepito.jpg"))

    return itemlist

def play(item):
    logger.info("[peliculaspepito.py] play")
    itemlist=[]
    
    data = scrapertools.cache_page(item.url)
    
    videoitemlist = servertools.find_video_items(data=data)
    i=1
    for videoitem in videoitemlist:
        if not "favicon" in videoitem.url:
            videoitem.title = "Mirror %d%s" % (i,videoitem.title)
            videoitem.fulltitle = item.fulltitle
            videoitem.channel=channel=__channel__
            videoitem.show = item.show
            itemlist.append(videoitem)
            i=i+1

    return itemlist


