# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para peliculasyonkis
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Adaptado por Boludiko basado en el canal seriesyonkis V9 Por Truenon y Jesus
# v11
#------------------------------------------------------------
import urlparse,urllib2,urllib,re

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "peliculasyonkis_generico"
__category__ = "F"
__type__ = "generic"
__title__ = "Peliculasyonkis"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[peliculasyonkis_generico.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="lastepisodes"   , title="Utimas Peliculas" , url="http://www.peliculasyonkis.com/ultimas-peliculas"))
    itemlist.append( Item(channel=__channel__, action="listalfabetico" , title="Listado alfabetico", url="http://www.peliculasyonkis.com/lista-de-peliculas"))
    itemlist.append( Item(channel=__channel__, action="listcategorias" , title="Listado por Categorias",url="http://www.peliculasyonkis.com/") )
    itemlist.append( Item(channel=__channel__, action="mostviewed"     , title="Peliculas mas vistas", url="http://www.peliculasyonkis.com/peliculas-mas-vistas"))
    itemlist.append( Item(channel=__channel__, action="search"         , title="Buscar...", url="http://www.peliculasyonkis.com/buscar/pelicula"))

    return itemlist

def listcategorias(item):
    logger.info("[peliculasyonkis_generico.py] listcategorias")
    itemlist=[]
    # Descarga la pagina
    data = scrapertools.cachePage(item.url)
    #logger.info(data)
    
    # Extrae las entradas (carpetas)
    patronvideos  = '<li><a href="(/genero/[^"]+)" title="([^"]+)".*?</li>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    
    for match in matches:
        try:
           scrapedtitle = unicode( match[1], "utf-8" ).encode("iso-8859-1")
        except:
           scrapedtitle = match[1]
        scrapedurl = "http://www.peliculasyonkis.com"+match[0]
        scrapedthumbnail = ""
        scrapedplot = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item ( channel=__channel__ , action="peliculascat" , title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot ) )

    return itemlist
   
def peliculascat(item):
    logger.info("[peliculasyonkis_generico.py] series")
    itemlist = []

    data = scrapertools.cachePage(item.url)
   
    #Paginador
    matches = re.compile('<div class="paginator">.*?<a href="([^"]+)">&gt;</a>.*?</div>', re.S).findall(data)
    if len(matches)>0:
        paginador = Item(channel=__channel__, action="peliculascat" , title="!Pagina siguiente" , url=urlparse.urljoin(item.url,matches[0]), thumbnail=item.thumbnail, plot="", extra = "" , show=item.show)
    else:
        paginador = None
    
    if paginador is not None:
        itemlist.append( paginador )

    matches = re.compile('<li class=.*?title="([^"]+)" href="([^"]+)".*?</li>', re.S).findall(data)
    #scrapertools.printMatches(matches)

    for match in matches:
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=match[0] , fulltitle=match[0], url=urlparse.urljoin(item.url,match[1]), thumbnail="", plot="", extra = "" , show=match[1] ))

    if paginador is not None:
        itemlist.append( paginador )

    return itemlist
   
def search(item,texto):
    logger.info("[peliculasyonkis_generico.py] search")
    itemlist = []

    if item.url=="":
        item.url = "http://www.peliculasyonkis.com/buscar/pelicula"
    url = "http://www.peliculasyonkis.com/buscar/pelicula" # write ur URL here
    post = 'keyword='+texto[0:18]+'&search_type=pelicula'
    
    data = scrapertools.cache_page(url,post=post)
    
    import seriesyonkis
    itemlist = seriesyonkis.getsearchresults(item, data, "findvideos")
    for item in itemlist:
        item.channel=__channel__

    return itemlist

def lastepisodes(item):
    logger.info("[peliculasyonkis_generico.py] lastepisodes")

    data = scrapertools.cache_page(item.url)
  
    matches = re.compile('<li class="thumb-episode"> <a href="([^"]+)".*?src="([^"]+)".*?title="([^"]+)".*?</li>', re.S).findall(data)
    #scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:               
        scrapedtitle = match[2] 
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = urlparse.urljoin(item.url,match[1])
        scrapedplot = ""

        # Depuracion
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")            
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle, context="4|5"))

    return itemlist  

def mostviewed(item):
    logger.info("[peliculasyonkis_generico.py] mostviewed")
    data = scrapertools.cachePage(item.url)

    matches = re.compile('<li class="thumb-episode"> <a href="([^"]+)" title="([^"]+)".*?src="([^"]+)".*?</li>', re.S).findall(data)
    #scrapertools.printMatches(matches)
    itemlist = []
    for match in matches:               
        scrapedtitle = match[1] 
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = urlparse.urljoin(item.url,match[2])
        scrapedplot = ""

        # Depuracion
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")            
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle))

    return itemlist

def peliculas(item):
    logger.info("[peliculasyonkis_generico.py] series")
    itemlist = []

    data = scrapertools.cachePage(item.url)
   
    #Paginador
    matches = re.compile('<div class="paginator">.*?<a href="([^"]+)">&gt;</a>.*?</div>', re.S).findall(data)
    if len(matches)>0:
        paginador = Item(channel=__channel__, action="peliculas" , title="!Pagina siguiente" , url=urlparse.urljoin(item.url,matches[0]), thumbnail=item.thumbnail, plot="", extra = "" , show=item.show)
    else:
        paginador = None
    
    if paginador is not None:
        itemlist.append( paginador )

    #<div id="main-section" class="lista-series">.*?</div>
    #matches = re.compile('<div id="main-section" class="lista-series">.*?</div>', re.S).findall(data)
    matches = re.compile('<ul id="list-container".*?</ul>', re.S).findall(data)    
    #scrapertools.printMatches(matches)
    for match in matches:
        data=match
        break
    
    #<li><a href="/serie/al-descubierto" title="Al descubierto">Al descubierto</a></li>
    matches = re.compile('<li>.*?href="([^"]+)".*?title="([^"]+)".*?</li>', re.S).findall(data)
    #scrapertools.printMatches(matches)

    for match in matches:
        itemlist.append( Item(channel=__channel__, action="findvideos" , title=match[1] , fulltitle=match[1], url=urlparse.urljoin(item.url,match[0]), thumbnail="", plot="", extra = "" , show=match[1] ))

    if paginador is not None:
        itemlist.append( paginador )

    return itemlist

def findvideos(item):
    logger.info("[seriesyonkis.py] findvideos")
    itemlist = []

    Nro = 0
    fmt=id=""

    # Acota la zona de búsqueda
    data = scrapertools.cache_page(item.url)    
    data = scrapertools.get_match(data,'<div id="section-content"(.*?)<h2 class="header-subtitle magnet"')
    logger.info("data="+data)
    
    # Procesa línea por línea
    matches = re.compile('<tr.*?</tr>', re.S).findall(data)
    scrapertools.printMatches(matches)

    for match in matches:
        logger.info(match)
        #<tr data-server="streamcloud" data-lang="lat" data-sub="no_sub">
        #<td class="episode-title episode-server" data-value="0">
        #<a href="/s/ngo/5/5/5/8/986" title="Reproducir El hobbit: Un viaje inesperado (2012) en streamcloud" target="_blank"><img src="http://s.staticyonkis.com/img/veronline.png" height="22" width="22" alt="ver online" />Reproducir</a>  <span class="public_sprite like_green vote_link_positive user_not_logged" data-id="5558986" data-type="+" title="Voto positivo">[positivo]</span> <span class="public_sprite dislike_red vote_link_negative user_not_logged" data-id="5558986" data-type="-" title="Voto negativo">[negativo]</span> </td> <td class="episode-server-img"><a href="/s/ngo/5/5/5/8/986" title="Reproducir El hobbit: Un viaje inesperado (2012) " target="_blank">
        #<span class="server streamcloud" data-visible="true"></span></a></td> <td class="episode-lang">
        #<span class="flags lat" title="Español Latino" data-visible="true">lat</span></td> <td class="episode-subtitle subtitles center">
        #<span class="flags no_sub" title="Sin información" data-visible="true">no_sub</span></td> <td class="episode-quality">
        #<span class="episode-quality-icon" title="Calidad alta"> <i class="public_sprite meter04 quality4"></i> </span> </td> <td class="episode-notes"> <span class="icon-info"></span> <div class="tip hidden"> <h3>Información vídeo</h3> <div class="arrow-tip-right-dark sprite"></div> <ul> <li>  1.3 Gb  </li>  </ul> </div> </td> <td class="episode-source center"><span title="Blu-Ray, DVD... - Calidad alta">BR/DVD</span></td> <td class="episode-uploader"><span title="88TodoPelis88">88Todo...</span></td> <td class="episode-error bug center"><a href="#" class="errorlink" data-id="5558986" ><img src="http://s.staticyonkis.com/img/icons/bug.png" alt="error" /></a></td> </tr>  <tr data-server="nowvideo" data-la

        '''
        <tr data-server="vk" data-lang="spa" data-sub="no_sub"> 
        <td class="episode-server" data-value="1"> 
        <a href="/s/ngo/2/6/4/8/694" title="Reproducir Los colegas del barrio (1996) en vk" target="_blank">
        <img src="http://s.staticyonkis.com/img/veronline.png" height="22" width="22" alt="ver online" />Reproducir</a>  
        <span class="public_sprite like_green vote_link_positive user_not_logged" data-id="2648694" data-type="+" title="Voto positivo">[positivo]</span> 
        <span class="public_sprite dislike_red vote_link_negative user_not_logged" data-id="2648694" data-type="-" title="Voto negativo">[negativo]</span> </td> 
        <td class="episode-server-img"><a href="/s/ngo/2/6/4/8/694" title="Reproducir Los colegas del barrio (1996) " target="_blank">
        <span class="server vk"></span></a></td> 
        <td class="episode-lang"><span class="flags spa" title="Español">spa</span></td> 
        <td class="episode-subtitle subtitles center"><span class="flags no_sub" title="Sin información">no_sub</span></td> <td class="quality"> 
        <span class="episode-quality-icon" title="Calidad alta"> <i class="public_sprite meter04 quality4"></i> </span> </td> <td class="episode-notes"> <span class="icon-info"></span> <div class="tip hidden"> <h3>Información vídeo</h3> <div class="arrow-tip-right-dark sprite"></div> <ul> <li>    </li>  </ul> </div> </td> <td class="source center"><span title="Blu-Ray, DVD... - Calidad alta">BR/DVD</span></td> <td class="episode-uploader"><span title="--3286--">--3286--</span></td
        '''
        
        patron  = '<a href="(/s/ngo/[^"]+)".*?'
        patron += '<span class="server ([^"]+)".*?'
        patron += 'title="[^"]+"[^>]*>([^<]+)</span>.*?'
        patron += '"flags ([^_]+)_sub".*?'
        patron += 'class="public_sprite meter\d+ quality([^"]+)"'
        datos = re.compile(patron, re.S).findall(match)
        for info in datos:  
            id = info[0]
            servidor = info[1]
            Nro = Nro + 1
            fmt = info[4]      
            audio = "Audio:" + info[2]
            subs = "Subs:" + info[3]
            url = urlparse.urljoin(item.url,info[0])
            scraptedtitle = "%02d) [%s %s] - (Q:%s) [%s] " % (Nro , audio,subs,fmt,servidor)
            itemlist.append( Item(channel=__channel__, action="play" , title=scraptedtitle, fulltitle=item.fulltitle , url=url, thumbnail=item.thumbnail, plot=item.plot, folder=False,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))

    return itemlist

def play(item):
    import seriesyonkis
    return seriesyonkis.play(item)

def listalfabetico(item):
    logger.info("[peliculasyonkis_generico.py] listalfabetico")
       
    itemlist = []
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="0-9", url="http://www.peliculasyonkis.com/lista-de-peliculas/0-9"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="A"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/A"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="B"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/B"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="C"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/C"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="D"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/D"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="E"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/E"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="F"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/F"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="G"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/G"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="H"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/H"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="I"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/I"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="J"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/J"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="K"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/K"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="L"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/L"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="M"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/M"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="N"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/N"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="O"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/O"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="P"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/P"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="Q"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/Q"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="R"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/R"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="S"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/S"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="T"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/T"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="U"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/U"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="V"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/V"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="W"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/W"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="X"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/X"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="Y"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/Y"))
    itemlist.append( Item(channel=__channel__, action="peliculas" , title="Z"  , url="http://www.peliculasyonkis.com/lista-de-peliculas/Z"))

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    
    # mainlist
    mainlist_items = mainlist(Item())
    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    episode_items = lastepisodes(mainlist_items[0])
    bien = False
    for episode_item in episode_items:
        mediaurls = findvideos( episode_item )
        if len(mediaurls)>0:
            return True

    return False