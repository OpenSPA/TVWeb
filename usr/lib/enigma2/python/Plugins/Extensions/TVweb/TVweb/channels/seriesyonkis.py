# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para seriesyonkis
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
# Por Truenon y Jesus, modificada por Boludiko
# v11
#------------------------------------------------------------
import urlparse,urllib2,urllib,re

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools

__channel__ = "seriesyonkis"
__category__ = "S,A"
__type__ = "generic"
__title__ = "Seriesyonkis"
__language__ = "ES"

DEBUG = config.get_setting("debug")

def isGeneric():
    return True

def mainlist(item):
    logger.info("[seriesyonkis.py] mainlist")

    itemlist = []
    itemlist.append( Item(channel=__channel__, action="lastepisodes"      , title="Ultimos capítulos" , url="http://www.seriesyonkis.com/ultimos-capitulos",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))
    itemlist.append( Item(channel=__channel__, action="listalfabetico"    , title="Listado alfabetico", url="http://www.seriesyonkis.com",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))
    itemlist.append( Item(channel=__channel__, action="mostviewed"    , title="Series más vistas", url="http://www.seriesyonkis.com/series-mas-vistas",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))
    itemlist.append( Item(channel=__channel__, action="search"    , title="Buscar", url="http://www.seriesyonkis.com/buscar/serie",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))

    return itemlist

def search(item,texto, categoria="*"):
    logger.info("[seriesyonkis.py] search")
    itemlist = []

    if categoria not in ("*", "S"): return itemlist ## <--
    
    if item.url=="":
        item.url = "http://www.seriesyonkis.com/buscar/serie"
    url = "http://www.seriesyonkis.com/buscar/serie" # write ur URL here
    post = 'keyword='+texto[0:18] + '&search_type=serie'
    
    data = scrapertools.cache_page(url,post=post)
    return getsearchresults(item, data, "episodios")
    
def getsearchresults(item, data, action):
    itemlist = []

    patron='_results_wrapper">(.*?)<div id="tab-profesionales"'
    matches = re.compile(patron,re.DOTALL).findall(data)
    for match in matches:        
        #<li class="nth-child1n"> <figure> <a href="/pelicula/el-moderno-sherlock-holmes-1924" title="El moderno Sherlock Holmes (1924)"><img width="100" height="144" src="http://s.staticyonkis.com/img/peliculas/100x144/el-moderno-sherlock-holmes-1924.jpg" alt=""></a> <figcaption>8.0</figcaption> </figure> <aside> <h2><a href="/pelicula/el-moderno-sherlock-holmes-1924" title="El moderno Sherlock Holmes (1924)">El moderno Sherlock Holmes (1924)</a></h2> <p class="date">1924 | Estados Unidos | votos: 3</p> <div class="content">Película sobre el mundo del cine, Keaton es un proyeccionista que sueña con ser un detective cuando, milagrosamente, se encuentra dentro de la película que está proyectando. Allí intentará salvar a su amada de las garras del villano. Una de...</div> <p class="generos">  <a href="/genero/comedia">Comedia</a>  <a class="topic" href="/genero/cine-mudo">Cine mudo</a>  <a class="topic" href="/genero/mediometraje">Mediometraje</a>  <i>(1 más) <span class="aditional_links"> <span>  <a class="topic" href="/genero/sherlock-holmes">Sherlock Holmes</a>  </span> </span> </i>  </p> </aside> </li>
        patron='<li[^>]+>.*?href="([^"]+)".*?title="([^"]+)".*?src="([^"]+).*?<div class="content">([^<]+)</div>.*?</li>'
        results = re.compile(patron,re.DOTALL).findall(match)
        for result in results:        
            scrapedtitle = result[1]
            scrapedurl = urlparse.urljoin(item.url,result[0])
            scrapedthumbnail = result[2]
            scrapedplot = result[3]
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")

            itemlist.append( Item(channel=__channel__, action=action , title=scrapedtitle , fulltitle=scrapedtitle, url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle))
        
    return itemlist

def lastepisodes(item):
    logger.info("[seriesyonkis.py] lastepisodes")

    data = scrapertools.cache_page(item.url)

    #<li class="thumb-episode "> <a href="/capitulo/strike-back/project-dawn-part-3/200215"><img class="img-shadow" src="/img/series/170x243/strike-back.jpg" height="166" width="115"></a> <div class="transparent"> <a href="/capitulo/strike-back/project-dawn-part-3/200215"><span>2x03</span></a> </div> <strong><a href="/serie/strike-back" title="Strike back">Strike back</a></strong> </li>
    matches = re.compile('<li class="thumb-episode ">.*?</li>', re.S).findall(data)
    #scrapertools.printMatches(matches)

    itemlist = []
    for match in matches:
        
        #<li class="thumb-episode "> <a href="/capitulo/strike-back/project-dawn-part-3/200215"><img class="img-shadow" src="/img/series/170x243/strike-back.jpg" height="166" width="115"></a> <div class="transparent"> <a href="/capitulo/strike-back/project-dawn-part-3/200215"><span>2x03</span></a> </div> <strong><a href="/serie/strike-back" title="Strike back">Strike back</a></strong> </li>
        datos = re.compile('<a href="([^"]+)">.*?src="([^"]+)".*?<span>([^<]+)</span>.*?title="([^"]+)"', re.S).findall(match)
    
        for capitulo in datos:        
            scrapedtitle = capitulo[3] + " " + capitulo[2] 
            scrapedurl = urlparse.urljoin( item.url , capitulo[0] )
            scrapedthumbnail = item.url + capitulo[1]            
            scrapedplot = ""
    
            # Depuracion
            if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")            
            itemlist.append( Item(channel=__channel__, action="findvideos" , title=scrapedtitle , fulltitle=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, show=scrapedtitle,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))

    return itemlist  

def mostviewed(item):
    logger.info("[seriesyonkis.py] mostviewed")
    data = scrapertools.cachePage(item.url)

    #<li class="thumb-episode"> <a href="/serie/como-conoci-a-vuestra-madre" title="Cómo conocí a vuestra madre"><img class="img-shadow" src="/img/series/170x243/como-conoci-a-vuestra-madre.jpg" height="166" width="115"></a> <strong><a href="/serie/como-conoci-a-vuestra-madre" title="Cómo conocí a vuestra madre">Cómo conocí a vuestra madre</a></strong> </li> 
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
        itemlist.append( Item(channel=__channel__, action="episodios" , title=scrapedtitle, fulltitle=scrapedtitle , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot, viewmode="movie", show=scrapedtitle,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))

    return itemlist

def series(item):
    logger.info("[seriesyonkis.py] series")
    itemlist = []

    data = scrapertools.cachePage(item.url)
   
    #Paginador
    #<div class="paginator"> &nbsp;<a href="/lista-de-series/C/">&lt;</a>&nbsp;<a href="/lista-de-series/C/">1</a>&nbsp;<strong>2</strong>&nbsp;<a href="/lista-de-series/C/200">3</a>&nbsp;<a href="/lista-de-series/C/200">&gt;</a>&nbsp; </div>
    matches = re.compile('<div class="paginator">.*?<a href="([^"]+)">&gt;</a>.*?</div>', re.S).findall(data)
    if len(matches)>0:
        paginador = Item(channel=__channel__, action="series" , title="!Página siguiente" , url=urlparse.urljoin(item.url,matches[0]), thumbnail=item.thumbnail, plot="", extra = "" , show=item.show,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg")
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
        itemlist.append( Item(channel=__channel__, action="episodios" , title=match[1], fulltitle=match[1] , url=urlparse.urljoin(item.url,match[0]), thumbnail="", plot="", extra = "" , show=match[1],fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg" ))

    if len(itemlist)>0 and config.get_platform() in ("wiimc","rss") and item.channel<>"wiideoteca":
        itemlist.append( Item(channel=__channel__, action="add_serie_to_wiideoteca", title=">> Agregar Serie a Wiideoteca <<", fulltitle=item.fulltitle , url=item.url , thumbnail="", plot="", extra="") )
 
    if paginador is not None:
        itemlist.append( paginador )

    return itemlist

def detalle_programa(item,data=""):
    
    #http://www.seriesyonkis.com/serie/gungrave
    #http://www.seriesyonkis.com/ficha/serie/gungrave
    url = item.url
    if "seriesyonkis.com/serie/" in url:
        url = url.replace("seriesyonkis.com/serie/","seriesyonkis.com/ficha/serie/")
    
    # Descarga la página
    if data=="":
        data = scrapertools.cache_page(url)

    # Obtiene el thumbnail
    try:
        item.thumbnail = scrapertools.get_match(data,'<div class="profile-info"[^<]+<a[^<]+<img src="([^"]+)"')
    except:
        pass

    try:
        item.plot = scrapertools.htmlclean( scrapertools.get_match(data,'<div class="details">(.*?)</div>') )
    except:
        pass
    logger.info("plot="+item.plot)

    try:
        item.title = scrapertools.get_match(data,'<h1 class="underline"[^>]+>([^<]+)</h1>').strip()
    except:
        pass

    return item

def episodios(item):
    logger.info("[seriesyonkis.py] episodios")

    # Descarga la pagina
    data = scrapertools.cache_page(item.url)
    item = detalle_programa(item)

    #<h2 class="header-subtitle">CapÃ­tulos</h2> <ul class="menu"> 
    #<h2 class="header-subtitle">Cap.*?</h2> <ul class="menu">.*?</ul>
    matches = re.compile('<h2 class="header-subtitle">Cap.*?</h2> <ul class="menu">.*?</ul>', re.S).findall(data)
    if len(matches)>0:
        data = matches[0]
    #<li.*?
    matches = re.compile('<li.*?</li>', re.S).findall(data)
    #scrapertools.printMatches(matches)
        
    itemlist = []  

    No = 0
    for match in matches:
        itemlist.extend( addChapters(Item(url=item.url,extra=match, thumbnail=item.thumbnail,show=item.show,plot=item.plot,fulltitle=item.title)) )
        '''
        if(len(matches)==1):
            itemlist = addChapters(Item(url=match, thumbnail=thumbnail))
        else:
            # Añade al listado de XBMC
            No = No + 1
            title = "Temporada "+str(No)
            itemlist.append( Item(channel=__channel__, action="season" , title= title, url=match, thumbnail=thumbnail, plot="", show = title, folder=True))
        '''

    if config.get_platform().startswith("xbmc") or config.get_platform().startswith("boxee"):
        itemlist.append( Item(channel=item.channel, title="Añadir esta serie a la biblioteca de XBMC", url=item.url, action="add_serie_to_library", extra="episodios", show=item.show,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg") )
        itemlist.append( Item(channel=item.channel, title="Descargar todos los episodios de la serie", url=item.url, action="download_all_episodes", extra="episodios", show=item.show,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg") )

    return itemlist

def addChapters(item):
    #<tr > <td class="episode-title"> <span class="downloads allkind" title="Disponibles enlaces a descarga directa y visualizaciones"></span>
    #<a href="/capitulo/bones/capitulo-2/2870"> <strong> 1x02 </strong> - El hombre en la unidad especial de victimas </a> </td> <td> 18/08/2007 </td> <td class="episode-lang">  <span class="flags_peq spa" title="Español"></span>  </td> <td class="score"> 8 </td> </tr>
    matches = re.compile('<tr[^<]+<td class="episode-title.*?<a href="([^"]+)"[^<]+<strong>([^<]+)</strong>(.*?)</a>(.*?)</tr>', re.S).findall(item.extra)
    scrapertools.printMatches(matches)
    
    itemlist=[]
    for match in matches:
        url = urlparse.urljoin(item.url,match[0])
        title = match[1].strip()+match[2]

        patron = '<span class="flags[^"]+" title="([^"]+)">'
        flags = re.compile(patron,re.DOTALL).findall(match[3])
        for flag in flags:
            title = title + " ("+flag+")"

        itemlist.append( Item(channel=__channel__, action="findvideos" , title=title, fulltitle=item.fulltitle+" "+title, url=url, thumbnail=item.thumbnail, plot=item.plot, show = item.show, context="4", viewmode="movie_with_plot", folder=True,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))

    return itemlist

def findvideos(item):
    logger.info("[seriesyonkis.py] findvideos")
    itemlist = []

    try:
        Nro = 0
        fmt=id=""

        # Acota la zona de búsqueda
        data = scrapertools.cache_page(item.url)    
        data = scrapertools.get_match(data,'<div id="section-content"(.*?)<h2 class="header-subtitle p2p')
        
        # Procesa línea por línea
        matches = re.compile('<tr>.*?</tr>', re.S).findall(data)
        if DEBUG: scrapertools.printMatches(matches)

        for match in matches:
            logger.info(match)
            #<tr> <td class="episode-server"> <a href="/s/ngo/2/0/0/4/967" title="Reproducir No estamos solos 2x1" target="_blank"><img src="http://s.staticyonkis.com/img/veronline.png" height="22" width="22"> Reproducir</a> </td> <td class="episode-server-img"><a href="/s/ngo/2/0/0/4/967" title="Reproducir No estamos solos 2x1" target="_blank"><span class="server megavideo"></span></a></td> <td class="episode-lang"><span class="flags esp" title="Español">esp</span></td> <td class="center"><span class="flags no_sub" title="Sin subtítulo o desconocido">no</span></td> <td> <span class="episode-quality-icon" title="Calidad del episodio"> <i class="sprite quality5"></i> </span> </td> <td class="episode-notes"><span class="icon-info"></span> <div class="tip hidden"> <h3>Información vídeo</h3> <div class="arrow-tip-right-dark sprite"></div> <ul> <li>Calidad: 6, Duración: 85.8 min, Peso: 405.79 MB, Resolución: 640x368</li> </ul> </div> </td> <td class="episode-uploader">lksomg</td> <td class="center"><a href="#" class="errorlink" data-id="2004967"><img src="http://s.staticyonkis.com/img/icons/bug.png" alt="" /></a></td> </tr>
            #<tr> <td class="episode-server" data-value="0"> <a href="/s/ngo/5/5/9/8/737" title="Descargar Capítulo 514 1x514 de rapidgator" target="_blank"><img src="http://s.staticyonkis.com/img/descargadirecta.png" height="22" width="22" alt="descarga directa" /> Descargar</a>  <span class="public_sprite like_green vote_link_positive user_not_logged" data-id="5598737" data-type="+" title="Voto positivo">[positivo]</span> <span class="public_sprite dislike_red vote_link_negative user_not_logged" data-id="5598737" data-type="-" title="Voto negativo">[negativo]</span> </td> <td class="episode-server-img"><a href="/s/ngo/5/5/9/8/737" title="Descargar Capítulo 514 1x514" target="_blank"><span class="server rapidgator"></span></a></td> <td class="episode-lang"><span class="flags spa" title="Español">spa</span></td> <td class="episode-subtitle subtitles center"><span class="flags no_sub" title="Sin información">no_sub</span></td> <td class="episode-notes"> <span class="icon-info"></span> <div class="tip hidden"> <h3>Información vídeo</h3> <div class="arrow-tip-right-dark sprite"></div> <ul> <li>hdtv</li>  </ul> </div> </td> <td class="episode-uploader"> <span title="repomen77">repomen77</span> </td> <td class="episode-error bug center"><a href="#" class="errorlink" data-id="5598737"><img src="http://s.staticyonkis.com/img/icons/bug.png" alt="error" /></a></td> </tr>
            #<a href="/s/ngo/5/5/9/8/737"
            #<span class="server rapidgator"></span></a></td> <td class="episode-lang">
            #<span class="flags spa" title="Español">spa</span></td> <td class="episode-subtitle subtitles center">
            #<span class="flags no_sub" title="Sin información">no_sub</span></td> <td class="episode-notes"> <span class="icon-info"></span> <div class="tip hidden"> <h3>Información vídeo</h3>
            #<div class="arrow-tip-right-dark sprite"></div> <ul> <li>hdtv</li>  </ul> </div> </td> <td class="episode-uploader"> <span title="repomen77">repomen77</span> </td> <td class="episode-error bug center"><a href="#" class="errorlink" data-id="5598737"><img src="http://s.staticyonkis.com/img/icons/bug.png" alt="error" /></a></td> </tr>
            patron  = '<a href="(/s/ngo/[^"]+)".*?'
            patron += '<span class="server ([^"]+)".*?title="[^"]+">([^<]+)</span>.*?"flags ([^_]+)_sub".*?'
            patron += '<div class="arrow-tip-right-dark sprite"></div> <ul> <li>([^<]+)<'
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
                # El plot va vacío porque necesita menos memoria, y en realidad es el de la serie y no el del episodio :)
                itemlist.append( Item(channel=__channel__, action="play" , title=scraptedtitle, fulltitle=item.fulltitle , url=url, thumbnail=item.thumbnail, plot="", folder=False,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))
    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )

    return itemlist

def play(item):
    logger.info("[seriesyonkis.py] play")
    itemlist = []
    
    # Descarga la página de reproducción de este episodio y server
    #<a href="/s/y/597157/0/s/1244" target="_blank">Reproducir ahora</a>
    logger.info("[seriesyonkis.py] play url="+item.url)
    data = scrapertools.cache_page(item.url)
    patron = '<a href="([^"]+)" target="_blank">\s*Reproducir ahora\s*</a>'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if len(matches)==0:
        patron = '<a href="([^"]+)" target="_blank">\s*Descargar ahora\s*</a>'
        matches = re.compile(patron,re.DOTALL).findall(data)
    
    if len(matches)==0:
        logger.info("[seriesyonkis.py] play ERROR, no encuentro el enlace 'Reproducir ahora' o 'Descargar ahora'")
        return []
    
    playurl = urlparse.urljoin(item.url,matches[0])
    logger.info("[seriesyonkis.py] play url="+playurl)

    try:
        location = scrapertools.getLocationHeaderFromResponse(playurl)
        logger.info("[seriesyonkis.py] play location="+location)

        if location<>"":
            logger.info("[seriesyonkis.py] Busca videos conocidos en la url")
            videos = servertools.findvideos(location)
            
            if len(videos)==0:
                location = scrapertools.getLocationHeaderFromResponse(location)
                logger.info("[seriesyonkis.py] play location="+location)

                if location<>"":
                    logger.info("[seriesyonkis.py] Busca videos conocidos en la url")
                    videos = servertools.findvideos(location)
                    
                    if len(videos)==0:
                        logger.info("[seriesyonkis.py] play downloading location")
                        data = scrapertools.cache_page(location)
                        logger.info("------------------------------------------------------------")
                        #logger.info(data)
                        logger.info("------------------------------------------------------------")
                        videos = servertools.findvideos(data) 
                        logger.info(str(videos))
                        logger.info("------------------------------------------------------------")
        else:
            logger.info("[seriesyonkis.py] play location vacía")
            videos=[]

        if(len(videos)>0): 
            url = videos[0][1]
            server=videos[0][2]                   
            itemlist.append( Item(channel=item.channel, action="play" , title=item.title, fulltitle=item.fulltitle , url=url, thumbnail=item.thumbnail, plot=item.plot, server=server, extra=item.extra, folder=False))
        else:
            data = scrapertools.cache_page(playurl)
            patron='<ul class="form-login">(.*?)</ul'
            matches = re.compile(patron, re.S).findall(data)
            if(len(matches)>0):
                if "xbmc" in config.get_platform():
                    data = matches[0]
                    #buscamos la public key
                    patron='src="http://www.google.com/recaptcha/api/noscript\?k=([^"]+)"'
                    pkeys = re.compile(patron, re.S).findall(data)
                    if(len(pkeys)>0):
                        pkey=pkeys[0]
                        #buscamos el id de challenge
                        data = scrapertools.cache_page("http://www.google.com/recaptcha/api/challenge?k="+pkey)
                        patron="challenge.*?'([^']+)'"
                        challenges = re.compile(patron, re.S).findall(data)
                        if(len(challenges)>0):
                            challenge = challenges[0]
                            image = "http://www.google.com/recaptcha/api/image?c="+challenge
                            
                            #CAPTCHA
                            exec "import pelisalacarta.captcha as plugin"
                            tbd = plugin.Keyboard("","",image)
                            tbd.doModal()
                            confirmed = tbd.isConfirmed()
                            if (confirmed):
                                tecleado = tbd.getText()
                                logger.info("tecleado="+tecleado)
                                sendcaptcha(playurl,challenge,tecleado)
                            del tbd 
                            #tbd ya no existe
                            if(confirmed and tecleado != ""):
                                itemlist = play(item)
                else:
                    itemlist.append( Item(channel=item.channel, action="error", title="El sitio web te requiere un captcha") )

    except:
        import sys
        for line in sys.exc_info():
            logger.error( "%s" % line )
    logger.info("len(itemlist)=%s" % len(itemlist))
    return itemlist

def sendcaptcha(url,challenge,text):
    values = {'recaptcha_challenge_field' : challenge,
          'recaptcha_response_field' : text}
    form_data = urllib.urlencode(values)
    url = url.replace("seriesyonkis","seriescoco")
    url = url.replace("peliculasyonkis","peliculascoco")
    logger.info("url="+url+", form_data="+form_data)
    request = urllib2.Request(url,form_data)
    request.add_header('User-Agent', 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)')
    response = urllib2.urlopen(request)
    html = response.read()
    logger.info("response="+html)
    response.close()
    return html

# Pone todas las series del listado alfabético juntas, para no tener que ir entrando una por una
def completo(item):
    logger.info("[seriesyonkis.py] completo()")
    itemlist = []

    # Carga el menú "Alfabético" de series
    item = Item(channel=__channel__, action="listalfabetico")
    items_letras = listalfabetico(item)
    
    # Para cada letra
    for item_letra in items_letras:
        #print item_letra.title
        
        # Lee las series
        items_programas = series(item_letra)

        salir = False
        while not salir:

            # Saca la URL de la siguiente página
            ultimo_item = items_programas[ len(items_programas)-1 ]

            # Páginas intermedias
            if ultimo_item.action=="series":
                #print ultimo_item.url
                # Quita el elemento de "Página siguiente" 
                ultimo_item = items_programas.pop()

                # Añade las series de la página a la lista completa
                itemlist.extend( items_programas )
    
                # Carga la sigiuente página
                items_programas = series(ultimo_item)

            # Última página
            else:
                # Añade a la lista completa y sale
                itemlist.extend( items_programas )
                salir = True

    return itemlist

def listalfabetico(item):
    logger.info("[seriesyonkis.py] listalfabetico")
    
    itemlist = []
    
    itemlist.append( Item(channel=__channel__, action="series" , title="0-9", url="http://www.seriesyonkis.com/lista-de-series/0-9",fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))
    for letra in ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']:
        itemlist.append( Item(channel=__channel__, action="series" , title=letra , url="http://www.seriesyonkis.com/lista-de-series/"+letra,fanart="http://pelisalacarta.mimediacenter.info/fanart/seriesyonkis.jpg"))

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