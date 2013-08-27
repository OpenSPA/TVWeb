# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para MTV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib

from core import logger
from core import config
from core import scrapertools
from core.item import Item

DEBUG = False
CHANNELNAME = "mtv"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.mtv mainlist")

    item = Item(channel=CHANNELNAME, url="http://www.mtv.es/programas/ver/")
    return programas(item)

def programas(item):
    logger.info("tvalacarta.channels.mtv programas")
    itemlist = []

    '''
    <div class="row row140" >
    <div class="thumbcontainer thumb140">
    <a href="/programas/100-artistas-mas-sexis/" title="Los 100 artistas más sexis" class="thumblink" >
    <img class="thumbnail " src="http://mtv-es.mtvnimages.com/marquee/KYLIE_SEXY_1.jpg?width=140&amp;quality=0.91" alt="Los 100 artistas más sexis" />
    </a>
    '''

    # Extrae las series
    data = scrapertools.cachePage(item.url)
    patron  = '<div class="row row140"[^<]+'
    patron += '<div class="thumbcontainer thumb140"[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)"[^<]+'
    patron += '<img class="thumbnail " src="(http://mtv-es.mtvnimages.com/.*?)\?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)
    
    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        #http://www.mtv.es/programas/destacados/alaska-y-mario/
        #http://www.mtv.es/programas/destacados/alaska-y-mario/episodios/
        url = urlparse.urljoin(url,"episodios")

        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="episodios" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    try:
        next_page=scrapertools.get_match(data,'<a href="([^"]+)"><span class="link">Pr')
        #/videos?prog=3798&#038;v=1&#038;pag=2
        itemlist.append( Item( channel=item.channel , title=">> Página siguiente" , action="programas" , url=urlparse.urljoin(item.url,next_page) ) )
    except:
        pass

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.mtv episodios")
    itemlist=[]

    '''
    <div class="row row70 " >
    <div class="thumbcontainer thumb70">
    <a href="/programas/destacados/alaska-y-mario/videos/alaska-y-mario-ep-106-parte-1-de-3-660835/" title="Alaska y Mario episodio 6: 'Ibiza Mix'" class="thumblink" >
    <img class="thumbnail " src="http://mtv-es.mtvnimages.com/img/imagenes/aym106a400x300.jpg?height=53&amp;quality=0.91" alt="Alaska y Mario episodio 6: 'Ibiza Mix'" />
    <span class="video"> </span>
    </a>
    </div>
    <div class="link-block">
    <a href="/programas/destacados/alaska-y-mario/videos/alaska-y-mario-ep-106-parte-1-de-3-660835/" title="Alaska y Mario episodio 6: 'Ibiza Mix'" class="titlelink " >Alaska y Mario episodio 6: 'Ibiza Mix'</a></div>
    <div class="watchButton" >
    <a href="/programas/destacados/alaska-y-mario/videos/alaska-y-mario-ep-106-parte-1-de-3-660835/"><span>Ver</span></a> </div>
    </div>  
    '''
    # Extrae los episodios
    data = scrapertools.cachePage( item.url )
    patron  = '<div class="row row70[^<]+'
    patron += '<div class="thumbcontainer thumb70[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)" class="thumblink"[^<]+'
    patron += '<img class="thumbnail " src="(http://mtv-es.mtvnimages.com/.*?)\?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)


    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="partes" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )

    if len(itemlist) == 0:
	    patron  = '<div class="link-block">[^<]+'
	    patron += '<a href="([^"]+)" title="([^"]+)"'
	    matches = re.compile(patron,re.DOTALL).findall(data)
	    if DEBUG: scrapertools.printMatches(matches)

    	    for scrapedurl,scrapedtitle in matches:
        	title = scrapedtitle.strip()
        	thumbnail = item.thumbnail
        	plot = ""
        	url = urlparse.urljoin(item.url,scrapedurl)
        	if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        	itemlist.append( Item( channel=item.channel , title=title , action="partes" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=True ) )



    try:
        #<a href="/programas/destacados/alaska-y-mario/episodios?start_20=20"><span class="link">Próximo</span>
        next_page=scrapertools.get_match(data,'<a href="([^"]+)"><span class="link">Pr')
        #/videos?prog=3798&#038;v=1&#038;pag=2
        itemlist.append( Item( channel=item.channel , title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page) ) )
    except:
        pass

    return itemlist

def partes(item):
    logger.info("tvalacarta.channels.mtv partes")
    itemlist=[]

    '''
    <div class="row row70 " >
    <div class="thumbcontainer thumb70">
    <a href="/programas/destacados/gandia-shore/videos/gandía-shore-ep-114-parte-3-de-4-872479/" title="Gandía Shore Ep. 114 |Parte 3 de 4|" class="thumblink" >
    <img class="thumbnail " src="http://mtv-es.mtvnimages.com/img/imagenes/gsh114c.jpg?height=53&amp;quality=0.91" alt="Gandía Shore Ep. 114 |Parte 3 de 4|" />
    <span class="video"> </span>
    </a>
    </div>
    <div class="link-block">
    <a href="/programas/destacados/gandia-shore/videos/gandía-shore-ep-114-parte-3-de-4-872479/" title="Gandía Shore Ep. 114 |Parte 3 de 4|" class="titlelink " >Gandía Shore Ep. 114 |Parte 3 de 4|</a></div>
    <p class="video-description" >Destrozando la casa </p>
    <div class="flux-usage" >
    <script type="text/javascript">
    /* <![CDATA[ */
    Flux.createWidget("ContentAction", {
    "contentUri": "mgid:hcx:content:mtv.es:2edfa803-946e-46a3-9d4d-09a43d7c921c",
    "layout": "horizontal",
    "size": "small",
    "items": [
    { id: 'commentCount', title: 'Comentarios' },
    { id: 'contentRating', title: { thumbsUpTitle: 'Me gusta', thumbsDownTitle: 'No me gusta' } }
    ]
    });
    /* ]]> */
    </script>
    </div> </div>
    '''
    # Extrae los episodios
    data = scrapertools.cachePage(item.url)
    data = scrapertools.get_match(data,'<h3 class="header-title">[^<]+</h3>(.*?)</div[^<]+</div[^<]+</div[^<]+</div>')
    patron  = '<div class="row row70[^<]+'
    patron += '<div class="thumbcontainer thumb70[^<]+'
    patron += '<a href="([^"]+)" title="([^"]+)" class="thumblink"[^<]+'
    patron += '<img class="thumbnail " src="(http://mtv-es.mtvnimages.com/.*?)\?'
    matches = re.compile(patron,re.DOTALL).findall(data)
    if DEBUG: scrapertools.printMatches(matches)

    for scrapedurl,scrapedtitle,scrapedthumbnail in matches:
        title = scrapedtitle.strip()
        thumbnail = urlparse.urljoin(item.url,scrapedthumbnail)
        plot = ""
        url = urlparse.urljoin(item.url,scrapedurl)
        if (DEBUG): logger.info("title=["+title+"], url=["+url+"], thumbnail=["+thumbnail+"]")
        itemlist.append( Item( channel=item.channel , title=title , action="play" , server="mtv" , url=url , thumbnail=thumbnail , plot=plot , show=title , fanart=thumbnail , folder=False ) )

    try:
        #<a href="/programas/destacados/alaska-y-mario/episodios?start_20=20"><span class="link">Próximo</span>
        next_page=scrapertools.get_match(data,'<a href="([^"]+)"><span class="link">Pr')
        #/videos?prog=3798&#038;v=1&#038;pag=2
        itemlist.append( Item( channel=item.channel , title=">> Página siguiente" , action="episodios" , url=urlparse.urljoin(item.url,next_page) ) )
    except:
        pass

    return itemlist

# Verificación automática de canales: Esta función debe devolver "True" si todo está ok en el canal.
def test():
    
    # El canal tiene estructura
    items_mainlist = mainlist(Item())
    if len(items_mainlist)==0:
        print "No hay programas"
        return False

    # Ahora recorre los programas hasta encontrar vídeos en alguno
    for item_programa in items_mainlist:
        print "Verificando "+item_programa.title
        items_episodios = episodios(item_programa)

        if len(items_episodios)>0:
            return True

    print "No hay videos en ningún programa"
    return False
