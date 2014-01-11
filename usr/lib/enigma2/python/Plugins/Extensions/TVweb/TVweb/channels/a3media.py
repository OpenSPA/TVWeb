# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para antena 3
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re
import urllib, urllib2

from core import logger
from core import scrapertools
from core.item import Item


DEBUG = False
CHANNELNAME = "a3media"

import hmac


def isGeneric():
    return True

def mainlist(item):
    logger.info("[a3media.py] mainlist")

    '''
	<nav class="list clearfix">	
							<a  href="http://www.atresplayer.com/television/series/">Series</a>
					<a  href="http://www.atresplayer.com/television/programas/">Programas</a>
					<a  href="http://www.atresplayer.com/television/deportes/">Deportes</a>
					<a  href="http://www.atresplayer.com/television/noticias/">Noticias</a>
					<a  href="http://www.atresplayer.com/television/documentales/">Documentales</a>
					<a  href="http://www.atresplayer.com/television/series-infantiles/">Infantil</a>
					<a  href="http://www.atresplayer.com/television/webseries/">Webseries</a>
					<a  href="http://www.atresplayer.com/television/especial/">Más Contenido</a>
	</nav>
    '''

    url="http://www.atresplayer.com/"
    data = scrapertools.cachePage(url)
    logger.info(data)

    patron  = '<nav class="list clearfix">(.*?)</nav>'

    bloque = scrapertools.get_match(data,patron)

    itemlist = []

    if str(bloque)!="":
    	patron  = '<a[^h]+href="([^"]+)">([^<]+)</a>'
    	matches = re.compile(patron,re.DOTALL).findall(bloque)

    	itemlist.append( Item(channel=CHANNELNAME, title="Destacados" , action="programas" , extra="dest", url=url, folder=True) )

    	for scrapedurl, scrapedtitle in matches:
        	itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="programas" , url=scrapedurl, folder=True) )

    	itemlist.append( Item(channel=CHANNELNAME, title="A.....Z" , action="alfabetico" , url="http://www.atresplayer.com/buscador/sections.json", folder=True) )


    return itemlist

def alfabetico(item):
    logger.info("[a3media.py] temporadas")

    data = scrapertools.cachePage(item.url)
    logger.info(data)

    '''
{"href":"television/series-infantiles/academia-gladiadores/","img":"/clipping/2013/06/26/00721/703.jpg","titulo":"Academia de Gladiadores","letra":"A","descripcion":"ATRESPLAYER TV. Vídeos de ACADEMIA DE GLADIADORES.","cadena":"atres"}
    '''

    patron  = '{"href":"([^"]+)","img":"([^"]+)","titulo":"([^"]+)"'

    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []
    for url,img,scrapedtitle in matches:
	scrapedurl = "http://www.atresplayer.com/" + url
	scrapedthumbnail =  "http://www.atresplayer.com" + img
	scrapedplot = ""
	# Añade al listado
	itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="temporadas" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=True) )

    return itemlist


def temporadas(item):
    logger.info("[a3media.py] temporadas")

    data = scrapertools.cachePage(item.url)
    logger.info(data)

    '''
	<div class="fn_sinopsis_lay fn_slide_lay hide">
		<p class="mar-b_5">La acción se desarrolla a partir de octubre de 1961. Tras la doble boda entre Mauro e Inés y Daniel y Belén, muchos de los personajes deciden rehacer sus vidas lejos de Madrid. Mauro e Inés, junto con Tomás, se trasladan a Barcelona. Pedrito, en contra de su voluntad, se marcha finalmente con Felisa a Suiza para reencontrarse con su familia, abandonando a una desconsolada Dorita. Daniel y Belén cruzarán finalmente el charco hasta Colombia, dejando el hostal La Estrella en manos de Manolita. El eje central de todos los personajes, nuevos y antiguos, continúa girando alrededor de la Plaza de los Frutos, escenario principal de la ficción, y de El Asturiano, un bar clásico que se adapta a los tiempos que corren y que servirá de punto de encuentro entre los personajes y lugar de unión entre las distintas tramas.</p>
	</div>
    '''

    patron  = '<p class="mar-b_5">(.*?)</p>'

    try:
    	plot = scrapertools.get_match(data,patron)
	item.plot = plot
    except:
        pass


    '''
					<ul class="fn_lay hide">
							<li><a class="item chapter_b mar-b_5" href="http://www.atresplayer.com/television/series/amar-es-para-siempre/temporada-2/">Temporada 2</a></li>
							<li><a class="item chapter_b mar-b_5" href="http://www.atresplayer.com/television/series/amar-es-para-siempre/temporada-1/">Temporada 1</a></li>
					</ul>
    '''

    patron  = '<li><a class="item chapter_b mar-b_5" href="([^"]+)">([^<]+)</a></li>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []

    scrapedplot=""
    for scrapedurl, scrapedtitle  in matches:
	# Añade al listado
	itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=item.thumbnail, plot=item.plot , folder=True) )

    if len(itemlist) == 0:   
	if not '<div class="mod_carrousel_compuesto clearfix">' in data:  	## hay subprogramas
		itemlist = programas(item)
	else:					## No hay temporadas?
		itemlist = episodios(item)

    return itemlist

def programas(item):
    logger.info("[a3media.py] programas")

    data = scrapertools.cachePage(item.url)
    logger.info(data)

    if item.extra == "dest":
    	try:
		patron = '<div class="grid_4">(.*?)<div class="grid_12">'
		match = scrapertools.get_match(data,patron)
		data = match
    	except:
		pass

    '''
		<div class="mod_promo antena3 ">
				<a title="El tiempo entre costuras" href="http://www.atresplayer.com/television/series/el-tiempo-entre-costuras/">
					<img title="El tiempo entre costuras" src="/clipping/2013/10/21/00568/702.jpg"  alt="El tiempo entre costuras"/>
				</a>
    '''

    patron  = '<div class="mod_promo [^"]+">[^<]+'
    patron += '<a title="([^"]+)" href="([^"]+)">[^<]+'
    patron += '<img.*?src="([^"]+)"'
    if item.extra == "dest":
	patron += '.*?<span class="segunda-linea fn_ellipsis">([^<]+)</span>'

    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []

    for match in matches:
	scrapedtitle = match[0]
	scrapedurl = match[1]
	scrapedthumbnail = "http://www.atresplayer.com" + match[2]
	scrapedplot = ""
	if item.extra == "dest":
		scrapedtitle = scrapedtitle + " "+match[3] 
		accion = "play" 
	else: 
		accion = "temporadas"
	# Añade al listado
	itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action=accion , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , folder=True) )

    return itemlist

def episodios(item):
    logger.info("[a3media.py] episodios")

    data = scrapertools.cachePage(item.url)
    logger.info(data)

    patron  = '<p class="mar-b_5">(.*?)</p>'

    try:
    	plot = scrapertools.get_match(data,patron)
	item.plot = plot
    except:
	pass

    data = scrapertools.cachePage(item.url+"carousel.json")
    logger.info(data)

    '''
{"title":"42 (31-10-13)","hrefHtml":"http://www.atresplayer.com/television/series/amar-es-para-siempre/temporada-2/capitulo-42-31-10-13_2013103000399.html","srcImage":"/clipping/2013/10/30/00042/703.jpg","icono":"","textButton":"Ver contenido"}
    '''

    patron = '{"title":"([^"]+)","hrefHtml":"([^"]+)","srcImage":"([^"]+)","icono":([^,]+),"textButton":"[^"]+"}'

    matches = re.compile(patron,re.DOTALL).findall(data)

    itemlist = []

    for scrapedtitle, scrapedurl, scrapedthumbnail, icono in matches:
	scrapedthumbnail = "http://www.atresplayer.com" + scrapedthumbnail
	icono=icono.replace('"','')
	if icono=="":
		# Añade al listado
		itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=item.plot , folder=False) )


    return itemlist



def play(item):
    logger.info("[a3media.py] play")

    '''
<section class="mod_player">
	<div id="capa_modulo_player" episode="20131030-EPISODE-00002-false"></div> 
    '''

    data = scrapertools.cachePage(item.url)
    logger.info(data)

    patron = '<div id="[^"]+" episode="([^"]+)"></div>'

    episode = scrapertools.get_match(data,patron)
    itemlist = []

    if len(episode)>0:
    	token = d(episode, "puessepavuestramerced")
    	url = "http://servicios.atresplayer.com/api/urlVideoLanguage/%s/%s/%s/es" % (episode, "android_tablet",token)
    	data = scrapertools.cachePage(url)
    	logger.info(data)
    	lista = load_json(data)
    	if lista != None: 
		#item.url = lista['resultObject']['es']
		item.url = lista['resultDes']
		if item.url == "Idioma inválido":     #### DRM encrypted
			item.url = "El video no puede verse en esta sistema"
    		itemlist.append(item)


    return itemlist


def getApiTime():
    stime = scrapertools.cachePage("http://servicios.atresplayer.com/api/admin/time")
    return long(stime) / 1000L

def d(s, s1):
    l = 3000L + getApiTime()
    s2 = e(s+str(l), s1)
    return "%s|%s|%s" % (s, str(l), s2)

def e(s, s1):
    return hmac.new(s1, s).hexdigest()


def load_json(data):
    # callback to transform json string values to utf8
    def to_utf8(dct):
        rdct = {}
        for k, v in dct.items() :
            if isinstance(v, (str, unicode)) :
                rdct[k] = v.encode('utf8', 'ignore')
            else :
                rdct[k] = v
        return rdct
    try :        
        from lib import simplejson
        json_data = simplejson.loads(data, object_hook=to_utf8)
        return json_data
    except:
        try:
            import json
            json_data = json.loads(data, object_hook=to_utf8)
            return json_data
        except:
            import sys
            for line in sys.exc_info():
                logger.error("%s" % line)




