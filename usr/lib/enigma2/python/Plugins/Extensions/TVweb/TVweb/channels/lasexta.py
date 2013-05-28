# -*- coding: utf-8 -*-
#------------------------------------------------------------
# Canal para la sexta
#------------------------------------------------------------
import urlparse,re

from core import logger
from core import scrapertools
from core.item import Item

logger.info("[sexta.py] init")

DEBUG = True
CHANNELNAME = "lasexta"
MAIN_URL = "http://www.lasexta.com/programas"
def isGeneric():
    return True

def mainlist(item):
    logger.info("[sexta.py] mainlist")
    itemlist=[]
    
    itemlist.append( Item(channel="antena3", title="Series"         , action="series"       , url="http://www.lasexta.com/videos/series.html", folder=True) )
    itemlist.append( Item(channel="antena3", title="Noticias"       , action="series"     , url="http://www.lasexta.com/videos/noticias.html", folder=True) )
    itemlist.append( Item(channel="antena3", title="Programas"      , action="series"    , url="http://www.lasexta.com/videos/programas.html", folder=True) )
    itemlist.append( Item(channel="antena3", title="Xplora"         , action="series"       , url="http://www.lasexta.com/videos/videos-xplora.html", folder=True) )

    return itemlist

    # Descarga la pagina
    #item.url = MAIN_URL
    #return programas(item)

def series(item):
    logger.info("[sexta.py] series y programas")
    itemlist = []
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    
    # Extrae la parte de programas
    patron = '<div class="visor">(.*)<!-- fin clase visor -->'
    episodiosdata = re.compile(patron,re.DOTALL).search(data).group(1);

    # Extrae las series
    patron = '<a[^t]+title="[^"]+" href="([^"]+)"[^<]+'
    patron += '<img title="[^"]+".*?'
    patron += 'src="([^"]+)".*?'
    patron += '<h2><p>([^<]+)</p></h2>'
    matches = re.compile(patron,re.DOTALL).findall(episodiosdata)

    if DEBUG: scrapertools.printMatches(matches)
    
    for scrapedurl, scrapedthumbnail, scrapedtitle in matches:

        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
	scrapedthumbnail = urlparse.urljoin(item.url, scrapedthumbnail)

        itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="years" , url=scrapedurl, thumbnail=scrapedthumbnail , show = scrapedtitle, folder=True))

    return itemlist

def years(item):
    logger.info("[sexta.py] años")
    itemlist = []
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae la parte de programas
    patron = '<dt class="temporada">A(.*)</dd>'

    try:
    	temporadasdata = re.compile(patron,re.DOTALL).search(data).group(1)
    except:
	temporadasdata = ""

    # Extrae las series
    patron = 'href="([^"]+)" >(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(temporadasdata)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches) == 0:
	return temporadas(item)
    else:
    	for scrapedurl, scrapedtitle in matches:
        	scrapedurl = urlparse.urljoin(item.url,scrapedurl)
		scrapedtitle = "Año "+ scrapedtitle.replace("\n","").replace("\t","").replace(" ","")

        	itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="meses" , url=scrapedurl, thumbnail=item.thumbnail , show = scrapedtitle, folder=True))

    	return itemlist

def meses(item):
    logger.info("[sexta.py] meses")
    itemlist = []
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae la parte de programas
    patron = '<dt class="temporada"></dt>(.*)</dl>'
    try:
    	temporadasdata = re.compile(patron,re.DOTALL).search(data).group(1)
    except:
	temporadasdata = ""

    # Extrae las series
    patron  = 'href="([^"]+)"[^>]+>(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(temporadasdata)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches) == 0:
	return episodios(item)
    else:
    	for scrapedurl, scrapedtitle in matches:
        	scrapedurl = urlparse.urljoin(item.url,scrapedurl)
		scrapedtitle = scrapedtitle.replace("\n","").replace("\t","").replace(" ","")

        	itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=item.thumbnail , show = scrapedtitle, folder=True))

    	return itemlist


def temporadas(item):
    logger.info("[sexta.py] temporadas")
    itemlist = []
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae la parte de programas
    patron = '<dt class="temporada">TEMPORADA</dt>(.*)</dl>'
    try:
    	temporadasdata = re.compile(patron,re.DOTALL).search(data).group(1)
    except:
	temporadasdata = ""

    # Extrae las series
    patron  = 'href="([^"]+)" >(.*?)</a>'
    matches = re.compile(patron,re.DOTALL).findall(temporadasdata)
    if DEBUG: scrapertools.printMatches(matches)

    if len(matches) == 0:
	return episodios(item)
    else:
    	for scrapedurl, scrapedtitle in matches:
        	scrapedurl = urlparse.urljoin(item.url,scrapedurl)
		scrapedtitle = "Temporada "+ scrapedtitle.replace("\n","").replace("\t","").replace(" ","")

        	itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=item.thumbnail , show = scrapedtitle, folder=True))

    	return itemlist

def episodios(item):
    logger.info("[sexta.py] episodios")
    itemlist = []
    # Descarga la página
    data = scrapertools.cache_page(item.url)

    # Extrae la parte de programas
    patron = '<div class="visor">(.*)<!-- fin clase visor -->'
    episodiosdata = re.compile(patron,re.DOTALL).search(data).group(1);

    # Extrae las series
    patron  = '<img title="[^"]+"[^s]+'
    patron += 'src="([^"]+)"[^h]+'
    patron += 'href="([^"]+)".*?'
    patron += '<p>([^<]+)</p>'
#    patron += '<h2><p>([^<]+)<'
    matches = re.compile(patron,re.DOTALL).findall(episodiosdata)
    if DEBUG: scrapertools.printMatches(matches)
    
    for scrapedthumbnail, scrapedurl, scrapedtitle in matches:

        scrapedurl = urlparse.urljoin(item.url,scrapedurl)
	scrapedthumbnail = urlparse.urljoin(item.url, scrapedthumbnail)

        itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="partes" , url=scrapedurl, thumbnail=scrapedthumbnail , show = scrapedtitle, folder=True))

    return itemlist

def partes(item):
    logger.info("[sexta.py] partes")
    itemlist = []

    # Descarga la página
    dataplayer = scrapertools.cache_page(item.url)
    logger.info(dataplayer)

    #player_capitulo.xml='/chapterxml//60000001/60000007/2012/10/03/00008.xml';
    patron  = "player_capitulo.xml='([^']+)'"
    partesurl = re.compile(patron,re.DOTALL).search(dataplayer).group(1);
    xmldata = scrapertools.cache_page(urlparse.urljoin('http://www.lasexta.com',partesurl))
    logger.info(xmldata)

    # url prefix
    patron  = '<urlVideoMp4><!\[CDATA\[(.*?)\]\]></urlVideoMp4>'
    prefix  = re.compile(patron,re.DOTALL).search(xmldata).group(1);
    logger.info(prefix)

    patron  = '<archivoMultimedia>[^<]+<archivo><!\[CDATA\[([^\]]+)'
    matches = re.compile(patron,re.DOTALL).findall(xmldata)
    if DEBUG: scrapertools.printMatches(matches)
    logger.info("matches="+str(matches))
    i=1
    if len(matches)>1:
	if "001.mp4" in matches[0]:
        	scrapedurl = "rtmp://antena3tvfs.fplive.net/antena3mediateca/"+matches[0].replace("001.mp4", "000.mp4")
    		itemlist.append( Item(channel=CHANNELNAME, title="(COMPLETO) %s" % item.title , action="play" , url=scrapedurl, thumbnail=item.thumbnail , plot=item.plot , folder=False) )
    for url in matches:
        scrapedtitle = "("+str(i)+") "+item.title
        scrapedurl = urlparse.urljoin(prefix.replace('rtmp:','http:'),url).replace('http:','rtmp:')
        scrapedthumbnail = item.thumbnail
        scrapedplot = item.plot
        itemlist.append( Item(channel=item.channel, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail , show = scrapedtitle, folder=False) )
        i=i+1

    return itemlist
