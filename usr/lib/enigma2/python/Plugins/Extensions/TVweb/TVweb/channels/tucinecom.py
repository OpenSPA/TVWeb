# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para tucinecom
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "tucinecom"
__category__ = "F"
__type__ = "generic"
__title__ = "tucinecom"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[tucinecom.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__ , action="peliculas"    , title="Peliculas"    , url="http://www.tucinecom.com/" ))
    itemlist.append( Item(channel=__channel__ , action="novedades"    , title="Documentales" , url="http://tucinecom.com/Pel%C3%ADculas/documentales/" ))

    return itemlist

def peliculas(item):
    logger.info("[tucinecom.py] peliculas")

    itemlist = []
    itemlist.append( Item(channel=__channel__ , action="novedades"    , title="Novedades"    , url="http://tucinecom.com/Pel%C3%ADculas/peliculas/" ))
    itemlist.append( Item(channel=__channel__ , action="letras"       , title="Alfabético"   , url="http://tucinecom.com/Pel%C3%ADculas/peliculas/" ))
    itemlist.append( Item(channel=__channel__ , action="generos"      , title="Géneros"      , url="http://tucinecom.com/Pel%C3%ADculas/peliculas/" ))
    itemlist.append( Item(channel=__channel__ , action="idiomas"      , title="Idiomas"      , url="http://tucinecom.com/Pel%C3%ADculas/peliculas/" ))

    return itemlist

def novedades(item):
    logger.info("[tucinecom.py] novedades")
    itemlist = []

    # Descarga la página
    data = get_main_page(item.url)

    # Extrae las entradas (carpetas)
    '''
    <div class="review-box-stars">
    <div style="display: none">VN:RO [1.9.22_1171]</div><div class="ratingblock "><div class="ratingheader "></div><div class="ratingstars "><div id="article_rater_9680" class="ratepost gdsr-oxygen gdsr-size-12"><div class="starsbar gdsr-size-12"><div class="gdouter gdheight"><div id="gdr_vote_a9680" style="width: 0px;" class="gdinner gdheight"></div></div></div></div></div><div class="ratingtext "><div id="gdr_text_a9680" class="inactive">Rating: 0.0/<strong>10</strong> (0 votes cast)</div></div></div>
    </div>
    <a href="http://tucinecom.com/pelicula/un-lugar-donde-refugiarse-safe-haven-2013-ver-online-y-descargar-gratis/" title="Un lugar donde refugiarse (Safe Haven) (2013) Ver Online Y Descargar Gratis">
    <img src="http://tucinecom.com/wp-content/uploads/2013/02/Un-lugar-donde-refugiarse-Nicholas-Sparks-140x210.jpg" alt="Un lugar donde refugiarse (Safe Haven) (2013) Ver Online Y Descargar Gratis"/>
    </a>
    <div id="mejor_calidad">
    <a href="http://tucinecom.com/pelicula/un-lugar-donde-refugiarse-safe-haven-2013-ver-online-y-descargar-gratis/" title="Un lugar donde refugiarse (Safe Haven) (2013) Ver Online Y Descargar Gratis"><img id="espanol" src="http://tucinecom.com/wp-content/themes/reviewit/images/Blueray-S_calidad.png" class="idiomas" alt="Un lugar donde refugiarse (Safe Haven) (2013) Ver Online Y Descargar Gratis"/>
    </a>
    <span>Blueray-S</span></div>
    </div>

    <div class="review-box-text">
    <h2><a href="http://tucinecom.com/pelicula/un-lugar-donde-refugiarse-safe-haven-2013-ver-online-y-descargar-gratis/" title="Un lugar donde refugiarse (Safe Haven) (2013) Ver Online Y Descargar Gratis">Un lugar donde refugiarse (Saf...</a></h2>
    <p>Katie (Julianne Hough) es una bella joven con un oscuro pasado que llega a la pequeña localidad cos...</p>
    </div>
    <div id="campos_idiomas">
    <img id="espanol" src="http://tucinecom.com/wp-content/themes/reviewit/images/s.png" class="idiomas" alt=""/>
    <img id="latino" src="http://tucinecom.com/wp-content/themes/reviewit/images/lx.png" class="idiomas" alt=""/>
    <img id="ingles" src="http://tucinecom.com/wp-content/themes/reviewit/images/ix.png" class="idiomas" alt=""/>
    <img id="vose" src="http://tucinecom.com/wp-content/themes/reviewit/images/v.png" class="idiomas" alt=""/>
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
    patron += '</div.*?'
    #patron += '</div[^<]+'
    #patron += '<div class="review-box-text"[^<]+'
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
        title=scrapedtitle +" ("+calidad+") ("
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
        itemlist.append( Item(channel=__channel__, action="mirrors", title=title , url=url , thumbnail=thumbnail , plot=plot , viewmode="movies_with_plot", folder=True) )

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
    logger.info("[tucinecom.py] letras")
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
    logger.info("[tucinecom.py] generos")
    itemlist = []

    # Descarga la página
    data = get_main_page(item.url)
    data = scrapertools.get_match(data,'<li class="cat-item cat-item-\d+"><a href="http...tucinecom.com/Pel.*?s/generos/"[^<]+</a>(.*?)</ul>')

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
    logger.info("[tucinecom.py] idiomas")
    itemlist = []

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

def mirrors(item):
    logger.info("[tucinecom.py] mirrors")
    data = get_main_page(item.url)
    itemlist = []

    '''
    <p>
    <span><img id="espanol" src="http://tucinecom.com/wp-content/themes/reviewit/images/s.png" class="servidor" alt="" /></span>
    <span><a href="#div_4_e" class='MO'>Opción 4</a></span>
    <span>TS HQ</span>
    <span>      <img src="http://tucinecom.com/wp-content/themes/reviewit/images/calidad3.png" class="caracteristicas_idiomas_calidad" alt="" />
    </span>
    <span>Arkonada</span>
    <span>      <img src="http://tucinecom.com/wp-content/themes/reviewit/images/imgres15.jpg" class="servidor" alt="" />
    </span>                </p>
    '''
    #no descarga directa
    #bloque = scrapertools.get_match(data,"<h3>Descarga Directa</h3>(.*?)</div[^<]+</div[^<]+</div[^<]+</div")
    #patron  = '<p[^<]+'
    #patron += '<span><img id="([^"]+)"[^<]+</span[^<]+'
    #patron += '<span><a href="#([^"]+)"[^>]+>([^<]+)</a></span[^<]+'
    #patron += '<span>([^<]+)</span'
    #matches = re.compile(patron,re.DOTALL).findall(bloque)
    #scrapertools.printMatches(matches)

    #for idioma,bloque,scrapedtitle,calidad in matches:
    #    title="Descarga directa "+scrapedtitle.strip()+" ["+idioma+"]["+calidad+"]"
    #    url=item.url
    #    thumbnail=""
    #    plot=""
    #    if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
    #    itemlist.append( Item(channel=__channel__, action="findvideos", title=title , url=url , thumbnail=thumbnail , plot=plot , extra=bloque, folder=True) )

    bloque = scrapertools.get_match(data,"<h3>Ver Online</h3>(.*?)</div[^<]+</div[^<]+</div[^<]+</div")
    patron  = '<p[^<]+'
    patron += '<span><img id="([^"]+)"[^<]+</span[^<]+'
    patron += '<span><a href="#([^"]+)"[^>]+>([^<]+)</a></span[^<]+'
    patron += '<span>([^<]+)</span'
    matches = re.compile(patron,re.DOTALL).findall(bloque)
    scrapertools.printMatches(matches)

    for idioma,bloque,scrapedtitle,calidad in matches:
        title="Ver online "+scrapedtitle.strip()+" ["+idioma+"]["+calidad+"]"
        url=item.url
        thumbnail=item.thumbnail
        plot=item.plot
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item(channel=__channel__, action="findvideos", title=title , url=url , thumbnail=thumbnail , plot=plot , extra=bloque, folder=True) )

    return itemlist

def findvideos(item):
    logger.info("[tucinecom.py] findvideos")

    itemlist=[]
    data = get_main_page(item.url)

    if item.extra!="":
        data = scrapertools.get_match(data,'<div id="'+item.extra+'"(.*?)</div>')
        logger.info("data="+data)

    itemlist = servertools.find_video_items(data=data)

    for videoitem in itemlist:
        videoitem.channel = __channel__
        videoitem.thumbnail = item.thumbnail
        videoitem.fulltitle = item.title
        videoitem.title = "Ver en ["+videoitem.server+"]"
    
    patron = "(http\://adf.ly/[A-Z0-9a-z]+)"
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    for url in matches:
        itemlist.append( Item(channel=__channel__, action="play", title="Enlace adf.ly" , url=url , folder=False) )

    return itemlist

def play(item):
    logger.info("[tucinecom.py] play")

    itemlist=[]
    # Extrae la URL de saltar el anuncio en adf.ly
    if item.url.startswith("http://adf"):
        # Averigua el enlace
        from servers import adfly
        location = adfly.get_long_url(item.url)
        logger.info("location="+location)

        from servers import servertools
        itemlist=servertools.find_video_items(data=location)
        for videoitem in itemlist:
            videoitem.channel=__channel__
            videoitem.folder=False

    else:
        itemlist.append(Item(url=item.url, server=item.server))

    return itemlist

def get_main_page(url):
    logger.info("[tucinecom.py] get_main_page")

    headers=[]
    headers.append(["User-Agent","Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:20.0) Gecko/20100101 Firefox/20.0"])
    headers.append(["Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"])
    headers.append(["Accept-Language","es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3"])
    headers.append(["Accept-Encoding","gzip, deflate"])

    # Descarga la página
    data = scrapertools.cachePage(url,headers=headers)
    #logger.info("[tucinecom.py] data="+data)

    '''
    <form id="ChallengeForm" action="http://tucinecom.com/Pel%C3%ADculas/peliculas/" method="POST">
    <input type="hidden" name="act" value="jschl"/>
    <input type="hidden" name="jschl_vc" value="4b00fc195c8b540eff250c29db58a1ca"/>
    <input type="hidden" id="jschl_answer" name="jschl_answer"/>
    </form>
    '''
    if '<form id="ChallengeForm"' in data:
        logger.info("[tucinecom.py] versión protegida")

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
            xmbctools.handle_wait(6,"Espera 5 segundos","Para acceder a Tucinecom tienes que esperar 5 segundos")
        except:
            import time
            time.sleep(6)
        post = urllib.urlencode({'act':act,'jschl_vc':jschl_vc,'jschl_answer':jschl_answer})

        # Llama
        data = scrapertools.cache_page(url,post=post,headers=headers)
    else:
        logger.info("[tucinecom.py] versión normal")


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
