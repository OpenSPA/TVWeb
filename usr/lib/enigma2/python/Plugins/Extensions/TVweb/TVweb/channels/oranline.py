# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para oranline
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "oranline"
__category__ = "F"
__type__ = "generic"
__title__ = "oranline"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[oranline.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__ , action="peliculas"    , title="Peliculas"    , url="http://www.oranline.com/" ))
    itemlist.append( Item(channel=__channel__ , action="novedades"    , title="Documentales" , url="http://oranline.com/Pel%C3%ADculas/documentales/" ))

    return itemlist

def peliculas(item):
    logger.info("[oranline.py] peliculas")

    itemlist = []
    itemlist.append( Item(channel=__channel__ , action="novedades"    , title="Novedades"    , url="http://oranline.com/Pel%C3%ADculas/peliculas/" ))
    itemlist.append( Item(channel=__channel__ , action="letras"       , title="Alfabético"   , url="http://oranline.com/Pel%C3%ADculas/peliculas/" ))
    itemlist.append( Item(channel=__channel__ , action="generos"      , title="Géneros"      , url="http://oranline.com/Pel%C3%ADculas/peliculas/" ))
    itemlist.append( Item(channel=__channel__ , action="idiomas"      , title="Idiomas"      , url="http://oranline.com/Pel%C3%ADculas/peliculas/" ))

    return itemlist

def novedades(item):
    logger.info("[oranline.py] novedades")
    itemlist = []

    # Descarga la página
    data = get_main_page(item.url)

    # Extrae las entradas (carpetas)
    '''
    <div class="review-box-stars">
    <div style="display: none">VN:RO [1.9.22_1171]</div><div class="ratingblock "><div class="ratingheader "></div><div class="ratingstars "><div id="article_rater_2067" class="ratepost gdsr-oxygen gdsr-size-12"><div class="starsbar gdsr-size-12"><div class="gdouter gdheight"><div id="gdr_vote_a2067" style="width: 0px;" class="gdinner gdheight"></div></div></div></div></div><div class="ratingtext "><div id="gdr_text_a2067" class="inactive">Rating: 0.0/<strong>10</strong> (0 votes cast)</div></div></div>                                        
    </div>                  
    <a href="http://oranline.com/pelicula/cazadores-de-sombras-ciudad-de-hueso-2013-ver-online-y-descargar-gratis/" title="Cazadores de sombras: Ciudad de Hueso (2013) Ver Online Y Descargar Gratis">
    <img src="http://oranline.com/wp-content/uploads/2013/08/cazadores-140x210.jpg" alt="Cazadores de sombras: Ciudad de Hueso (2013) Ver Online Y Descargar Gratis" />        
    </a>    
    <div id="mejor_calidad">
    <a href="http://oranline.com/pelicula/cazadores-de-sombras-ciudad-de-hueso-2013-ver-online-y-descargar-gratis/" title="Cazadores de sombras: Ciudad de Hueso (2013) Ver Online Y Descargar Gratis"><img id="espanol" src="http://oranline.com/wp-content/themes/reviewit/images/CAM_calidad.png" class="idiomas" alt="Cazadores de sombras: Ciudad de Hueso (2013) Ver Online Y Descargar Gratis" />  
    </a>
    <span>CAM</span></div>      
    </div>                  
    <!--End Image-->
    <div class="review-box-text">
    <h2><a href="http://oranline.com/pelicula/cazadores-de-sombras-ciudad-de-hueso-2013-ver-online-y-descargar-gratis/" title="Cazadores de sombras: Ciudad de Hueso (2013) Ver Online Y Descargar Gratis">Cazadores de sombras: Ciudad d...</a></h2>  
    <p>En la discoteca de moda de Nueva York, Clary Fray (Lily Collins) sigue a un atractivo chico de pelo ...</p>                                      
    </div>
    '''
    '''
    <div class="review-box-stars">
    <div style="display: none">VN:RO [1.9.22_1171]</div><div class="ratingblock "><div class="ratingheader "></div><div class="ratingstars "><div id="article_rater_9680" class="ratepost gdsr-oxygen gdsr-size-12"><div class="starsbar gdsr-size-12"><div class="gdouter gdheight"><div id="gdr_vote_a9680" style="width: 0px;" class="gdinner gdheight"></div></div></div></div></div><div class="ratingtext "><div id="gdr_text_a9680" class="inactive">Rating: 0.0/<strong>10</strong> (0 votes cast)</div></div></div>
    </div>
    <a href="http://oranline.com/pelicula/un-lugar-donde-refugiarse-safe-haven-2013-ver-online-y-descargar-gratis/" title="Un lugar donde refugiarse (Safe Haven) (2013) Ver Online Y Descargar Gratis">
    <img src="http://oranline.com/wp-content/uploads/2013/02/Un-lugar-donde-refugiarse-Nicholas-Sparks-140x210.jpg" alt="Un lugar donde refugiarse (Safe Haven) (2013) Ver Online Y Descargar Gratis"/>
    </a>
    <div id="mejor_calidad">
    <a href="http://oranline.com/pelicula/un-lugar-donde-refugiarse-safe-haven-2013-ver-online-y-descargar-gratis/" title="Un lugar donde refugiarse (Safe Haven) (2013) Ver Online Y Descargar Gratis"><img id="espanol" src="http://oranline.com/wp-content/themes/reviewit/images/Blueray-S_calidad.png" class="idiomas" alt="Un lugar donde refugiarse (Safe Haven) (2013) Ver Online Y Descargar Gratis"/>
    </a>
    <span>Blueray-S</span></div>
    </div>

    <div class="review-box-text">
    <h2><a href="http://oranline.com/pelicula/un-lugar-donde-refugiarse-safe-haven-2013-ver-online-y-descargar-gratis/" title="Un lugar donde refugiarse (Safe Haven) (2013) Ver Online Y Descargar Gratis">Un lugar donde refugiarse (Saf...</a></h2>
    <p>Katie (Julianne Hough) es una bella joven con un oscuro pasado que llega a la pequeña localidad cos...</p>
    </div>
    <div id="campos_idiomas">
    <img id="espanol" src="http://oranline.com/wp-content/themes/reviewit/images/s.png" class="idiomas" alt=""/>
    <img id="latino" src="http://oranline.com/wp-content/themes/reviewit/images/lx.png" class="idiomas" alt=""/>
    <img id="ingles" src="http://oranline.com/wp-content/themes/reviewit/images/ix.png" class="idiomas" alt=""/>
    <img id="vose" src="http://oranline.com/wp-content/themes/reviewit/images/v.png" class="idiomas" alt=""/>
    </div>
    </div>
    '''
    patron  = '<div class="review-box.*?'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<img src="([^"]+)"[^<]+'
    patron += '</a[^<]+'
    patron += '<div id="mejor_calidad"[^<]+'
    patron += '<a[^<]+<img[^<]+'
    patron += '</a[^<]+'
    patron += '<span>([^<]+)</span></div[^<]+'
    patron += '</div[^<]+'
    patron += '<![^<]+'
    patron += '<div class="review-box-text"[^<]+'
    patron += '<h2[^<]+<a[^<]+</a></h2[^<]+'
    patron += '<p>([^<]+)</p[^<]+'
    patron += '</div[^<]+'
    patron += '<div id="campos_idiomas">(.*?)</div>'

    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail,calidad,scrapedplot,idiomas in matches:
        scrapedtitle = scrapedtitle.replace("Ver Online Y Descargar Gratis","").strip()
        scrapedtitle = scrapedtitle.replace("Ver Online Y Descargar gratis","").strip()
        scrapedtitle = scrapedtitle.replace("Ver Online Y Descargar","").strip()
        title=scrapedtitle+" ("+calidad+") ("
        if "s.png" in idiomas:
            title=title+"ESP,"
        if "l.png" in idiomas:
            title=title+"LAT,"
        if "i.png" in idiomas:
            title=title+"ING,"
        if "v.png" in idiomas:
            title=title+"VOSE,"
        title = title[:-1]+")"
        url=urlparse.urljoin(item.url,scrapedurl)
        thumbnail=urlparse.urljoin(item.url,scrapedthumbnail)
        plot=scrapedplot.strip()
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title , url=url , thumbnail=thumbnail , plot=plot , viewmode="movies_with_plot", folder=True) )

    try:
        next_page = scrapertools.get_match(data,"<a href='([^']+)'>\&rsaquo\;</a>")
        itemlist.append( Item(channel=__channel__, action="novedades", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page) , folder=True) )
    except:
        try:
            next_page = scrapertools.get_match(data,"<span class='current'>\d+</span><a href='([^']+)'")
            itemlist.append( Item(channel=__channel__, action="novedades", title=">> Página siguiente" , url=urlparse.urljoin(item.url,next_page) , folder=True) )
        except:
            pass
        pass

    return itemlist

def letras(item):
    logger.info("[oranline.py] letras")
    itemlist = []

    # Descarga la página
    data = get_main_page(item.url)
    data = scrapertools.get_match(data,'<div id="alphaList" align="center">(.*?)</div>')

    # Extrae las entradas
    patron  = '<a href="([^"]+)">([^<]+)</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle in matches:
        title=scrapedtitle.strip()
        url=urlparse.urljoin(item.url,scrapedurl)
        thumbnail=""
        plot=""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="novedades", title=title , url=url , thumbnail=thumbnail , plot=plot , folder=True) )

    return itemlist

def generos(item):
    logger.info("[oranline.py] generos")
    itemlist = []

    # Descarga la página
    data = get_main_page(item.url)
    #<li class="cat-item cat-item-23831"><a href="http://www.oranline.com/Películas/3d-hou/" title="Ver todas las entradas archivadas en 3D-HOU">3D-HOU</a> (5)
    data = scrapertools.get_match(data,'<li class="cat-item cat-item-\d+"><a href="http://www.oranline.com/Pel.*?s/generos/"[^<]+</a>(.*?)</ul>')

    # Extrae las entradas
    patron  = '<li class="cat-item cat-item-\d+"><a href="([^"]+)"[^>]+>([^<]+)</a>\s+\((\d+)\)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,cuantas in matches:
        title=scrapedtitle.strip()+" ("+cuantas+")"
        url=urlparse.urljoin(item.url,scrapedurl)
        thumbnail=""
        plot=""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="novedades", title=title , url=url , thumbnail=thumbnail , plot=plot , folder=True) )

    return itemlist

def idiomas(item):
    logger.info("[oranline.py] idiomas")
    itemlist = []

    '''
    div class="widget"><h3>&Uacute;ltimos estrenos</h3>

    <ul>
    <li class="cat-item cat-item-84"><a href="http://www.oranline.com/Películas/castellano/" title="Ver todas las entradas archivadas en Castellano">Castellano</a> (585)
    </li>
    <li class="cat-item cat-item-85"><a href="http://www.oranline.com/Películas/latino/" title="Ver todas las entradas archivadas en Latino">Latino</a> (623)
    </li>
    <li class="cat-item cat-item-86"><a href="http://www.oranline.com/Películas/version-original/" title="Ver todas las entradas archivadas en Versión Original">Versión Original</a> (27)
    </li>
    <li class="cat-item cat-item-87"><a href="http://www.oranline.com/Películas/vos/" title="Ver todas las entradas archivadas en VOS">VOS</a> (1471)
    </li>
    '''
    # Descarga la página
    data = get_main_page(item.url)
    data = scrapertools.get_match(data,'<div class="widget"><h3>&Uacute;ltimos estrenos</h3>(.*?)</ul>')

    # Extrae las entradas
    patron  = '<li class="cat-item cat-item-\d+"><a href="([^"]+)"[^>]+>([^<]+)</a>\s+\((\d+)\)'
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,cuantas in matches:
        title=scrapedtitle.strip()+" ("+cuantas+")"
        url=urlparse.urljoin(item.url,scrapedurl)
        thumbnail=""
        plot=""
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="novedades", title=title , url=url , thumbnail=thumbnail , plot=plot , folder=True) )

    return itemlist

def get_main_page(url):
    logger.info("[oranline.py] get_main_page")

    headers=[]
    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:20.0) Gecko/20100101 Firefox/20.0"])
    headers.append(["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"])
    headers.append(["Accept-Language","es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"])
    headers.append(["Accept-Encoding","gzip, deflate"])

    # Descarga la página
    data = scrapertools.cachePage(url,headers=headers)
    #logger.info("[oranline.py] data="+data)

    '''
    <form id="ChallengeForm" action="http://oranline.com/Pel%C3%ADculas/peliculas/" method="POST">
    <input type="hidden" name="act" value="jschl"/>
    <input type="hidden" name="jschl_vc" value="4b00fc195c8b540eff250c29db58a1ca"/>
    <input type="hidden" id="jschl_answer" name="jschl_answer"/>
    </form>
    '''
    if '<form id="ChallengeForm"' in data:
        logger.info("[oranline.py] versión protegida")

        # Prepara las cabeceras
        headers.append(["Referer",url])
        
        # Prepara el post
        #act=jschl&jschl_vc=ca5de909bd9058f267a3ef41ead567b7&jschl_answer=77
        #var t,r,a;
        #t = document.createElement('div'); t.innerHTML="<a href='/'>x</a>"; t = t.firstChild.href;
        #r = t.match(/https?:\/\//)[0]; t = t.substr(r.length); t = t.substr(0,t.length-1);
        #a = $('#jschl_answer');
        #a.val(22+14*3);
        #64
        #l=13
        #a.val(parseInt(a.val())+t.length);

        #a.val(32+14*6);
        #116
        #l=13
        #act=jschl&jschl_vc=b72895c6482d3b84ebc0f4c2fecad311&jschl_answer=129

        url = scrapertools.get_match(data,'<form id="ChallengeForm" action="([^"]+)"')
        act=scrapertools.get_match(data,'<input type="hidden" name="act" value="([^"]+)"')
        jschl_vc=scrapertools.get_match(data,'<input type="hidden" name="jschl_vc" value="([^"]+)"')
        jschl_answer=scrapertools.get_match(data,'a.val\(([^\)]+)\)')
        jschl_answer=str(eval(jschl_answer)+13)

        try:
            import xmbctools
            xmbctools.handle_wait(6,"Espera 5 segundos","Para acceder a oranline tienes que esperar 5 segundos")
        except:
            import time
            time.sleep(6)
        post = urllib.urlencode({'act':act,'jschl_vc':jschl_vc,'jschl_answer':jschl_answer})

        # Llama
        data = scrapertools.cache_page(url,post=post,headers=headers)
    else:
        logger.info("[oranline.py] versión normal")


    return data

# Verificación automática de canales: Esta función debe devolver "True" si está ok el canal.
def test():
    from servers import servertools
    
    # mainlist es "peliculas | documentales"
    mainlist_items = mainlist(Item())

    # peliculas es "novedades | alfabetco | generos | idiomas"
    peliculas_items = peliculas(mainlist_items[0])

    # novedades es la lista de pelis
    novedades_items = novedades(peliculas_items[0])
    bien = False
    for novedad_item in novedades_items:
        # mirrors es una lista de alternativas
        mirrors_items = mirrors( novedad_item )

        for mirror_item in mirrors_items:
            # videos con "play"
            videos = findvideos(mirror_item)
            for video in videos:
                enlaces = play(video)
                if len(enlaces)>0:
                    return True

    return False