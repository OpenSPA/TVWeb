# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para cinetube
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os,sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "cinetube"
__category__ = "F,S,A,D"
__type__ = "generic"
__title__ = "Cinetube"
__language__ = "ES"

#DEBUG = config.get_setting("debug")
DEBUG = False
'''
SESION = config.get_setting("session","cinetube")
LOGIN = config.get_setting("login","cinetube")
PASSWORD = config.get_setting("password","cinetube")
'''

def isGeneric():
    return True

def mainlist(item):
    logger.info("[cinetube.py] getmainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Películas"                , action="menupeliculas"))
    #itemlist.append( Item(channel=__channel__, title="Series"                   , action="menuseries"))
    #itemlist.append( Item(channel=__channel__, title="Documentales"             , action="menudocumentales"))
    #itemlist.append( Item(channel=__channel__, title="Anime"                    , action="menuanime"))
    
    #itemlist.append( Item(channel=__channel__, title="Buscar"                   , action="search") )   
    #itemlist.append( Item(channel=__channel__, title="Buscar por Actor/Director", action="search" , url="actor-director") )

    '''
    if SESION=="true":
        perform_login(LOGIN,PASSWORD)
        itemlist.append( Item(channel=__channel__, title="Cerrar sesion ("+LOGIN+")", action="logout"))
    else:
        itemlist.append( Item(channel=__channel__, title="Iniciar sesion", action="login"))
    '''
    
    return itemlist

def menupeliculas(item):
    logger.info("[cinetube.py] menupeliculas")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Películas - Novedades"        , action="peliculas"        , url="http://www.cinetube.es/peliculas/"))
    #itemlist.append( Item(channel=__channel__, title="Películas - Estrenos de Cine" , action="documentales"     , url="http://www.cinetube.es/peliculas/estrenos-de-cine/"))
    #itemlist.append( Item(channel=__channel__, title="Películas - Estrenos en DVD"  , action="documentales"     , url="http://www.cinetube.es/peliculas/estrenos-dvd/"))
    #itemlist.append( Item(channel=__channel__, title="Películas - Nueva Calidad"    , action="documentales"     , url="http://www.cinetube.es/peliculas/nueva-calidad/"))
    itemlist.append( Item(channel=__channel__, title="Películas - A-Z"              , action="letras"           , url="http://www.cinetube.es/peliculas/"))
    itemlist.append( Item(channel=__channel__, title="Películas - Categorías"       , action="categorias"       , url="http://www.cinetube.es/peliculas/"))
    
    itemlist.append( Item(channel=__channel__, title="Buscador..."                  , action="search"           , url="peliculas") )

    return itemlist


def peliculas(item,paginacion=True):
    logger.info("[cinetube.py] peliculas")

    url = item.url

    # Descarga la página
    data = scrapertools.cachePage(url)

    # Extrae las entradas
    patronvideos  = '<div class="imgmov[^<]+'
    patronvideos += '<i[^<]+</i[^<]+'
    patronvideos += '<img src="([^"]+)"[^<]+'
    patronvideos += '<a href="([^"]+)"[^<]+<i[^<]+</i[^<]+'
    patronvideos += '<strong>([^<]+)</strong[^<]+'
    patronvideos += '<span[^>]+>(.*?)</span>'

    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for scrapedthumbnail,scrapedurl,scrapedtitle,scrapedplot in matches:
        title = scrapedtitle.strip()+" ("+scrapertools.htmlclean(scrapedplot).strip()+")"
        title = title.replace("Calidad:","")
        title = title.replace("Idiomas :","")
        title = re.compile("\s+",re.DOTALL).sub(" ",title)
        url = urlparse.urljoin(item.url,scrapedurl)
        plot = ""
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        # Añade al listado de XBMC
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title , fulltitle=title , url=url , thumbnail=thumbnail , plot=plot ) )

    # Extrae el paginador
    try:
        next_page_url = scrapertools.get_match(data,'<a class="lnne icob" href="([^"]+)">Siguientes</a>')
        itemlist.append( Item(channel=__channel__, action="peliculas", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page_url) ) )
    except:
        pass
        
    return itemlist

def letras(item):
    logger.info("[cinetube.py] listalfabetico("+item.url+")")
    
    if "peliculas" in item.url:
        action = "peliculas"
    elif "series-anime" in item.url:
        action="series"
    elif "peliculas-anime" in item.url:
        action="documentales"
    
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<ul class="lstabc[^>]+>(.*?)</ul>')

    # Extrae las entradas
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=__channel__, action=action, title=title , url=url , thumbnail=thumbnail , plot=plot) )

    return itemlist

def categorias(item):
    logger.info("[cinetube.py] listcategorias")

    if "peliculas" in item.url:
        action = "peliculas"
    elif "series-anime" in item.url:
        action="series"
    elif "peliculas-anime" in item.url:
        action="documentales"
    
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<h3 class="tibk bgwh fx pore"><strong>Temáticas</strong></h3>(.*?)</ul>')

    # Extrae las entradas
    patron = '<li><a href="([^"]+)">([^<]+)</a></li>'
    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []
    for scrapedurl,scrapedtitle in matches:
        title = scrapedtitle.strip()
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = ""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")

        # Añade al listado
        itemlist.append( Item(channel=__channel__, action=action, title=title , url=url , thumbnail=thumbnail , plot=plot) )

    return itemlist

def menuseries(item):
    logger.info("[cinetube.py] menuseries")

    itemlist = []

    itemlist.append( Item(channel=__channel__, title="Series - Novedades"           , action="series"           , url="http://www.cinetube.es/series/"))
    itemlist.append( Item(channel=__channel__, title="Series - A-Z"                 , action="listalfabetico"   , url="series"))
    itemlist.append( Item(channel=__channel__, title="Series - Listado completo"    , action="completo"         , url="http://www.cinetube.es/series-todas/"))
    itemlist.append( Item(channel=__channel__, title="Series - Categorías"          , action="listcategorias"   , url="series"))

    itemlist.append( Item(channel=__channel__, title="Buscar Series"                , action="search"           , url="series") )

    return itemlist

def menudocumentales(item):
    logger.info("[cinetube.py] menudocumentales")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Documentales - Novedades"         , action="documentales"     , url="http://www.cinetube.es/documentales/"))
    itemlist.append( Item(channel=__channel__, title="Documentales - A-Z"               , action="listalfabetico"   , url="documentales"))
    itemlist.append( Item(channel=__channel__, title="Documentales - Listado completo"  , action="completo"         , url="http://www.cinetube.es/documentales-todos/"))
    itemlist.append( Item(channel=__channel__, title="Documentales - Categorías"        , action="listcategorias"   , url="documentales"))

    itemlist.append( Item(channel=__channel__, title="Buscar Documentales"              , action="search"           , url="documentales") )

    return itemlist

def menuanime(item):
    logger.info("[cinetube.py] menuanime")

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Series Anime - Novedades"             , action="series"           , url="http://www.cinetube.es/series-anime/"))
    itemlist.append( Item(channel=__channel__, title="Series Anime - A-Z"                   , action="listalfabetico"   , url="series-anime" ))
    itemlist.append( Item(channel=__channel__, title="Series Anime - Listado completo"      , action="completo"         , url="http://www.cinetube.es/series-anime-todas/"))
    itemlist.append( Item(channel=__channel__, title="Series Anime - Categorías"            , action="listcategorias"   , url="series-anime"))
                     
    itemlist.append( Item(channel=__channel__, title="Películas Anime - Novedades"          , action="documentales"     , url="http://www.cinetube.es/peliculas-anime/") )
    itemlist.append( Item(channel=__channel__, title="Películas Anime - A-Z"                , action="listalfabetico"   , url="peliculas-anime" ))
    itemlist.append( Item(channel=__channel__, title="Películas Anime - Listado completo"   , action="completo"         , url="http://www.cinetube.es/peliculas-anime-todas/"))
    itemlist.append( Item(channel=__channel__, title="Películas Anime - Categorías"         , action="listcategorias"   , url="peliculas-anime"))

    itemlist.append( Item(channel=__channel__, title="Buscar Anime"                         , action="search"           , url="anime") )

    return itemlist

def perform_login(login,password):
    # Invoca al login, y con eso se quedarán las cookies de sesión necesarias
    login = login.replace("@","%40")
    data = scrapertools.cache_page("http://www.cinetube.es/login.php",post="usuario=%s&clave=%s" % (login,password))

def logout(item):
    nombre_fichero_config_canal = os.path.join( config.get_data_path() , __channel__+".xml" )
    config_canal = open( nombre_fichero_config_canal , "w" )
    config_canal.write("<settings>\n<session>false</session>\n<login></login>\n<password></password>\n</settings>")
    config_canal.close();

    itemlist = []
    itemlist.append( Item(channel=__channel__, title="Sesión finalizada", action="mainlist"))
    return itemlist

def login(item):
    if config.get_platform() in ("wiimc", "rss", "mediaserver"):
        login = config.get_setting("cinetubeuser")
        password = config.get_setting("cinetubepassword")
        if login<>"" and password<>"":
            url="http://www.cinetube.es/login.php"
            data = scrapertools.cache_page("http://www.cinetube.es/login.php",post="usuario=%s&clave=%s" % (login,password))
            itemlist = []
            itemlist.append( Item(channel=__channel__, title="Sesión iniciada", action="mainlist"))
    else:
        import xbmc
        keyboard = xbmc.Keyboard("","Login")
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            login = keyboard.getText()

        keyboard = xbmc.Keyboard("","Password")
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            password = keyboard.getText()

        nombre_fichero_config_canal = os.path.join( config.get_data_path() , __channel__+".xml" )
        config_canal = open( nombre_fichero_config_canal , "w" )
        config_canal.write("<settings>\n<session>true</session>\n<login>"+login+"</login>\n<password>"+password+"</password>\n</settings>")
        config_canal.close();

        itemlist = []
        itemlist.append( Item(channel=__channel__, title="Sesión iniciada", action="mainlist"))
    return itemlist

# Al llamarse "search" la función, el launcher pide un texto a buscar y lo añade como parámetro
def search(item,texto,categoria=""):
    logger.info("[cinetube.py] "+item.url+" search "+texto)
    itemlist = []
    url = item.url
    texto = texto.replace(" ","+")
    if "*" in categoria:
        url = "none"
    elif "F" in categoria:
        url = "peliculas"
    elif "S" in categoria:
        url = "series"
    logger.info("categoria: "+categoria+" url: "+url)
    try:
        # Series
        if url=="series" or url=="" or url=="none":
            item.url="http://www.cinetube.es/buscar/series/?palabra=%s&categoria=&valoracion="
            item.url = item.url % texto
            itemlist.extend(series(item))
        
        # Películas
        if url=="peliculas" or url=="" or url=="none":
            item.url="http://www.cinetube.es/buscar/peliculas/?palabra=%s&categoria=&valoracion="
            item.url = item.url % texto
            itemlist.extend(peliculas(item))
        
        # Documentales
        if item.url=="documentales" or url=="" or url=="none":
            item.url="http://www.cinetube.es/buscar/peliculas/?palabra=%s&categoria=&valoracion="
            item.url = item.url % texto
            itemlist.extend(documentales(item))
            
        # Anime
        if url=="anime" or url=="" or url=="none" or "F" in categoria:
            # Peliculas-anime
            item.url="http://www.cinetube.es/buscar/peliculas-anime/?palabra=%s&categoria=&valoracion="
            item.url = item.url % texto
            itemlist.extend(documentales(item))
        if url=="anime" or url=="" or url=="none" or "S" in categoria:
            # Series-anime
            item.url="http://www.cinetube.es/buscar/series-anime/?palabra=%s&categoria=&valoracion="
            item.url = item.url % texto
            itemlist.extend(series(item))

        # Actor/Director
        if url=="actor-director":
            item.url="http://www.cinetube.es/buscar/actor-director/?palabra=%s&categoria=&valoracion="
            item.url = item.url % texto
            itemlist.extend(peliculas(item))          
    
        return itemlist
        
    # Se captura la excepción, para no interrumpir al buscador global si un canal falla
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
        return []

def documentales(item):
    logger.info("[cinetube.py] documentales")

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Extrae las entradas
    '''
    <!--PELICULA-->
    <div class="peli_item textcenter peli_item_puntos"><a href="/peliculas/drama/ver-pelicula-somewhere.html">
    <div class="pelicula_img">
    <img src="http://caratulas.cinetube.es/pelis/10070.jpg" alt="Somewhere" />
    </div></a>
    <a href="/peliculas/drama/ver-pelicula-somewhere.html" ><div class="estreno"></div></a>                                        <a href="/peliculas/drama/ver-pelicula-somewhere.html" title="Ver estreno Somewhere"><p class="white">Somewhere</p></a>
    <p><span class="rosa">BLURAY-SCREENER</span></p><div class="icos_lg"><img src="http://caratulas.cinetube.es/img/cont/espanol.png" alt="" /><img src="http://caratulas.cinetube.es/img/cont/downupload.png" alt="" /><img src="http://caratulas.cinetube.es/img/cont/megavideo.png" alt="" /><img src="http://caratulas.cinetube.es/img/cont/ddirecta.png" alt="descarga directa" /> </div><div class="puntos_box">
    <div id="votos_media">6,2</div>
    <div id="votos_votaciones">48 votos</div>
    </div>
    </div>
    <!--FIN PELICULA-->
    '''
    patronvideos  = '<!--PELICULA-->[^<]+'
    patronvideos += '<div class="peli_item textcenter[^<]+<a href="([^"]+)">[^<]+'
    patronvideos += '<div class="pelicula_img">[^<]+'
    patronvideos += '<img src="([^"]+)" alt="([^"]+)"'
    
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    itemlist = []
    for match in matches:
        scrapedtitle = match[2]
        
        # Convierte desde UTF-8 y quita entidades HTML
        scrapedtitle = unicode( scrapedtitle, "iso-8859-1" , errors="replace" ).encode("utf-8")
        scrapedtitle = scrapertools.entityunescape(scrapedtitle)
        fulltitle = scrapedtitle
        
        scrapedplot = ""
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = urlparse.urljoin(item.url,match[1])
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        # Añade al listado
        if match[0].startswith("/documentales/serie-documental"):
            itemlist.append( Item(channel=__channel__, action="episodios", title=scrapedtitle+" (serie)" , fulltitle=fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=scrapedtitle) )
        else:
            itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , fulltitle=fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=scrapedtitle) )

    # Extrae el paginador
    #<li class="navs"><a class="pag_next" href="/peliculas-todas/2.html"></a></li>
    patronvideos  = '<li class="navs"><a class="pag_next" href="([^"]+)"></a></li>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="documentales", title="!Página siguiente" , url=scrapedurl) )

    return itemlist

# Pone todas las series del listado alfabético juntas, para no tener que ir entrando una por una
def completo(item):
    logger.info("[cinetube.py] completo()")
    
    url = item.url
    siguiente = True
    itemlist = []
    
    data = scrapertools.cachePage(url)
    patronpag  = '<li class="navs"><a class="pag_next" href="([^"]+)"></a></li>'
    while siguiente==True:
    
        patron = '<!--SERIE-->.*?<a href="([^"]+)" .*?>([^<]+)</a></span></li>.*?<!--FIN SERIE-->'
        matches = re.compile(patron,re.DOTALL).findall(data)
        for match in matches:
            scrapedtitle = match[1]
            # Convierte desde UTF-8 y quita entidades HTML
            scrapedtitle = unicode( scrapedtitle, "iso-8859-1" , errors="replace" ).encode("utf-8")
            scrapedtitle = scrapertools.entityunescape(scrapedtitle)
            fulltitle = scrapedtitle
            
            scrapedplot = ""
            scrapedurl = urlparse.urljoin(url,match[0])
            scrapedthumbnail = ""    

            itemlist.append( Item(channel=__channel__, action="temporadas", title=scrapedtitle , fulltitle=fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=scrapedtitle, show=scrapedtitle) )

        # Extrae el paginador
        matches = re.compile(patronpag,re.DOTALL).findall(data)
        if len(matches)==0:
            siguiente = False
        else:
            data = scrapertools.cachePage(urlparse.urljoin(url,matches[0]))

    return itemlist

def series(item):
    logger.info("[cinetube.py] series")
    itemlist = []
    
    # Descarga la página
    data = scrapertools.cachePage(item.url)
    logger.info("Pagina de %d caracteres" % len(data))

    # Extrae las entradas
    '''
    <li>
    <a href="/series/en-tierra-de-lobos/temporada-1/capitulo-12/"><img src="http://caratulas.cinetube.es/series/8912.jpg" alt="peli" /></a>
    <div class="icos_lg"><img src="http://caratulas.cinetube.es/img/cont/espanol.png" alt="espanol" /> <img src="http://caratulas.cinetube.es/img/cont/megavideo.png" alt="megavideo.png" /> <img src="http://caratulas.cinetube.es/img/cont/ddirecta.png" alt="descarga directa" /> <p><span class="rosa"></span></p></div>
    <p class="tit_ficha"><a class="tit_ficha" title="Ver serie Tierra de lobos" href="/series/en-tierra-de-lobos/temporada-1/capitulo-12/">Tierra de lobos </a></p>
    <p class="tem_fich">1a Temporada - Cap 12</p>
    </li>
    '''
    '''
    <li>
    <a href="/series/gabriel-un-amor-inmortal/"><img src="http://caratulas.cinetube.es/series/7952.jpg" alt="peli" /></a>
    <div class="icos_lg"><img src="http://caratulas.cinetube.es/img/cont/latino.png" alt="" /><img src="http://caratulas.cinetube.es/img/cont/megavideo.png" alt="" /><img src="http://caratulas.cinetube.es/img/cont/ddirecta.png" alt="descarga directa" /> </div>                                        
    <p class="tit_ficha">Gabriel, un amor inmortal </p>
    </li>
    '''
    '''
    <li>
    <a href="/series-anime/star-driver-kagayaki-no-takuto/temporada-1/capitulo-13/"><img src="http://caratulas.cinetube.es/seriesa/9009.jpg" alt="peli" /></a>
    <div class="icos_lg"><img src="http://caratulas.cinetube.es/img/cont/sub.png" alt="sub" /> <img src="http://caratulas.cinetube.es/img/cont/megavideo.png" alt="megavideo.png" /> <img src="http://caratulas.cinetube.es/img/cont/ddirecta.png" alt="descarga directa" /> <p><span class="rosa"></span></p></div>
    <p class="tit_ficha"><a class="tit_ficha" title="Ver serie Star Driver Kagayaki no Takuto" href="/series-anime/star-driver-kagayaki-no-takuto/temporada-1/capitulo-13/">Star Driver Kagayaki no Takuto </a></p>
    <p class="tem_fich">1a Temporada - Cap 13</p>
    </li>
    '''
    patronvideos  = '<li>[^<]+'
    patronvideos += '<a href="([^"]+)"><img src="([^"]+)"[^>]*></a>[^<]+'
    patronvideos += '<div class="icos_lg">(.*?)</div>[^<]+'
    patronvideos += '<p class="tit_ficha">(.*?)</p>[^<]+'
    patronvideos += '(?:<p class="tem_fich">([^<]+)</p>)?'

    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for match in matches:
        # Titulo
        scrapedtitle = match[3].strip()
        if len(match)>=5:
            scrapedtitle = scrapedtitle+" "+match[4]
        '''
        matchesconectores = re.compile('<img.*?alt="([^"]*)"',re.DOTALL).findall(match[2])
        conectores = ""
        for matchconector in matchesconectores:
            logger.info("matchconector="+matchconector)
            if matchconector=="":
                matchconector = "megavideo"
            conectores = conectores + matchconector + "/"
        if len(matchesconectores)>0:
            scrapedtitle = scrapedtitle + " (" + conectores[:-1] + ")"
        scrapedtitle = scrapedtitle.replace("megavideo/megavideo","megavideo")
        scrapedtitle = scrapedtitle.replace("megavideo/megavideo","megavideo")
        scrapedtitle = scrapedtitle.replace("megavideo/megavideo","megavideo")
        scrapedtitle = scrapedtitle.replace("descarga directa","DD")
        '''
        scrapedtitle = scrapertools.htmlclean(scrapedtitle)
        scrapedtitle = scrapertools.entityunescape(scrapedtitle)
        fulltitle = scrapedtitle

        scrapedplot = ""
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = match[1]
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="temporadas", title=scrapedtitle , fulltitle= fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , extra=scrapedtitle, show=scrapedtitle) )

    # Paginador
    #<li class="navs"><a class="pag_next" href="/peliculas-todas/2.html"></a></li>
    patronvideos  = '<li class="navs"><a class="pag_next" href="([^"]+)"></a></li>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    if len(matches)>0:
        scrapedurl = urlparse.urljoin(item.url,matches[0])
        itemlist.append( Item(channel=__channel__, action="series", title="!Página siguiente" , url=scrapedurl) )

    return itemlist

def temporadas(item):
    logger.info("[cinetube.py] temporadas")
    itemlist = []
    fulltitle = item.fulltitle
    # extra = item.extra
    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Busca el argumento
    patronvideos  = '<div class="content">.*?<p>(.*?)</p>'
    matches = re.compile(patronvideos,re.DOTALL).findall(data)
    if len(matches)>0:
        scrapedplot = scrapertools.htmlclean(matches[0])
        logger.info("plot actualizado en detalle");
    else:
        logger.info("plot no actualizado en detalle");

    # Busca las temporadas
    patron = '<div class="temporadas">.*?<tbody>(.*?)</tbody>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    if len(matches)>0:
        data = matches[0]
    
    patron  = '<tr><td[^>]+></td>[^<]+'
    patron += '<td><a href="([^"]+)">([^<]+)</a></td>[^<]+'
    patron += '<td>([^<]+)</td>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for url,titulo,num_episodios in matches:
        scrapedtitle = titulo.strip()+" ("+num_episodios+")"
        # directory = match[1].strip()
        extra = titulo.strip()
        scrapedurl = urlparse.urljoin(item.url,url)
        scrapedthumbnail = item.thumbnail
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="episodios", title=scrapedtitle , fulltitle=fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail, category=item.category , plot=scrapedplot, extra=extra, show=item.show) )

    # Una trampa, si la serie enlaza no con la temporada sino con la lista de episodios, se resuelve aquí
    if len(itemlist)==0:
        itemlist = episodios(item)
        
    # Si la serie lleva directamente a la página de detalle de un episodio (suele pasar en novedades) se detecta aquí
    if len(itemlist)==0:
        itemlist.extend(findvideos(item))

    # Opcion de añadir serie a Wiideoteca
    if len(itemlist)>0 and config.get_platform() in ("wiimc","rss") and item.channel<>"wiideoteca":
        itemlist.append( Item(channel=__channel__, action="add_serie_to_wiideoteca", title=">> Agregar Serie a Wiideoteca <<", fulltitle=fulltitle , url=item.url , thumbnail=scrapedthumbnail, plot=scrapedplot, extra=match[1].strip()) )
   
    return itemlist

def episodios(item):
    logger.info("[cinetube.py] episodios")
    extra = item.extra
    # directory = item.directory
    itemlist = []

    # Descarga la página
    data = scrapertools.cachePage(item.url)

    # Busca los episodios
    patron  = '<li>[^<]+'
    patron += '<span class="link"><a href="([^"]+)">([^<]+)</a></span>[^<]+'
    patron += '<dl>[^<]+'
    patron += '<dt>Info[^<]+</dt>[^<]+'
    patron += '<dd class="n"><img src="[^"]+" alt="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for match in matches:
        scrapedtitle = match[1].strip()

        # Convierte desde UTF-8 y quita entidades HTML
        scrapedtitle = unicode( scrapedtitle, "iso-8859-1" , errors="replace" ).encode("utf-8")
        scrapedtitle = scrapertools.entityunescape(scrapedtitle)
        fulltitle = scrapedtitle
        scrapedurl = urlparse.urljoin(item.url,match[0])
        scrapedthumbnail = item.thumbnail
        scrapedplot = item.plot
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

        itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , fulltitle=fulltitle , url=scrapedurl , thumbnail=scrapedthumbnail, category=item.category , extra=extra+" "+scrapedtitle, plot=scrapedplot, show=item.show, context="4") )

    if config.get_platform().startswith("xbmc"):
        itemlist.append( Item(channel=item.channel, title="Añadir estos episodios a la biblioteca de XBMC", url=item.url, action="add_serie_to_library", extra="episodios", show=item.show) )

    return itemlist

def findvideos(item):
    logger.info("[cinetube.py] findvideos")

    # Descarga la pagina
    data = scrapertools.cachePage(item.url)

    # Busca el argumento
    try:
        scrapedplot = scrapertools.get_match(data,'<meta name="description" content="([^"]+)"')
    except:
        scrapedplot = ""

    # Busca los enlaces a los mirrors, o a los capitulos de las series...
    patron  = '<li class="rwbd ovhd"[^<]+'
    patron += '<div class="cld2 flol"><img src="[^"]+"><span>([^<]+)</span></div[^<]+'
    patron += '<div class="cld3 flol">(.*?)</div[^<]+'
    patron += '<div class="cld4 flol"><img src="([^"]+)"><a class="rpdbtn hide" href="([^"]+)"'
    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []
    for idioma,calidad,imgservidor,scrapedurl in matches:
        title = "Ver en "+imgservidor.replace("/img/cnt/servidor/","").replace(".png","")+" ("+scrapertools.htmlclean(calidad)+" "+idioma+")"
        url = urlparse.urljoin(item.url,scrapedurl)
        thumbnail = urlparse.urljoin(item.url,imgservidor)
        plot = scrapedplot
        itemlist.append( Item(channel=__channel__, action="play", title=title , fulltitle=item.title , url=url , thumbnail=thumbnail, plot=plot, folder=True) )

    return itemlist

def play(item):
    logger.info("[cinetube.py] play")

    # Lee el iframe
    data = scrapertools.cache_page(item.url)
    patron = 'ct_url_decode\("([^"]+)"\)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    
    # Decodifica el bloque donde están los enlaces
    if len(matches)>0:
        data = matches[0]
        logger.info("-------------------------------------------------------------------------------------")
        logger.info(data)
        logger.info("-------------------------------------------------------------------------------------")
        data = ct_url_decode(data)

    logger.info("-------------------------------------------------------------------------------------")
    logger.info(data)
    logger.info("-------------------------------------------------------------------------------------")

    itemlist = servertools.find_video_items(data=data)
    
    for videoitem in itemlist:
        videoitem.title = item.title
        videoitem.fulltitle = item.fulltitle
        videoitem.thumbnail = item.thumbnail
        videoitem.channel = __channel__

    return itemlist    

def ct_url_decode(C):
    if not(C):
        return C
    
    C = C[::-1]
    X = 4-len(C)%4;
    if X in range(1,4):
        for z in range(X):
            C = C+"="
    
    import base64
    return base64.decodestring(C)

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    bien = True
    
    # mainlist
    mainlist_items = mainlist(Item())
    menupeliculas_items = menupeliculas(mainlist_items[0])

    # Da por bueno el canal si alguno de los vídeos de "Novedades" devuelve mirrors
    peliculas_items = peliculas(menupeliculas_items[0])
    
    bien = False
    for pelicula_item in peliculas_items:
        mirrors = findvideos(item=pelicula_item)
        if len(mirrors)>=0 and len( play(mirrors[0]) )>0:
            bien = True
            break
    
    return bien
