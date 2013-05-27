# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Canal para newdivx.net by Bandavi
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os, sys

from core import logger
from core import config
from core import scrapertools
from core.item import Item
from servers import servertools
#from core import downloadtools

__channel__ = "newdivxonline"
__category__ = "F,D"
__type__ = "generic"
__title__ = "NewDivxOnLine"
__language__ = "ES"

__URL__="http://www.newdivxonline.com"

DEBUG = config.get_setting("debug")

def mainlist(item):
	logger.info("[newdivxonline.py] mainlist")

	itemlist = []

	url ="http://www.newdivxonline.com/index.php"
	data = scrapertools.cachePage(url)

	'''
                  <map name="Map">
                <area shape="circle" coords="22,20,17" href="http://www.newdivxonline.com/index.php" alt="Espa&ntilde;ol">
              <area shape="circle" coords="64,20,17" href="http://www.newdivxonline.com/lat/index.php" alt="Latino">
              <area shape="circle" coords="104,20,17" href="http://www.newdivxonline.com/eng/index.php" alt="English">
              <area shape="circle" coords="143,20,17" href="http://www.newdivxonline.com/vos/index.php" alt="Subtituladas Espa&ntilde;ol">
              <area shape="circle" coords="185,19,17" href="http://www.newdivxonline.com/sub/index.php" alt="Subtitled English">
              </map>

	'''

	# Patron de las entradas
	patronvideos = '<area shape="circle" coords="[^"]+" href="([^"]+)" alt="([^"]+)">'

	matches = re.compile(patronvideos,re.DOTALL).findall(data)
	scrapertools.printMatches(matches)

	# Añade las entradas encontradas
	for scrapedurl, scrapedtitle in matches:
        	# Atributos
		scrapedthumbnail = ""
        	scrapedplot = ""
        	if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        	itemlist.append( Item(channel=__channel__, action="categorias", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )
#       itemlist.append( Item(channel=__channel__, action="search", title="Buscar" , url="http://www.newdivxonline.com/?do=video&act=search" , thumbnail="" , plot="" , folder=True) )
	return itemlist

def categorias(item):
	logger.info("[newdivxonline.py] categorias")

	itemlist = []

	data = scrapertools.cachePage(item.url)

	#Ultimos
	'''
  		<div class="list-items bwrbs">
	      <table width="100%"><tr><td width="81%"><div class="title">
					<h3>Ultimo A&ntilde;adido...</h3>
	'''
	# Patron de las entradas
	patronvideos  = '<div class="list-items bwrbs">.*?'
	patronvideos += '<div class="title">[^<]+'
	patronvideos += '<h3>([^<]+)</h3>[^<]+'

	matches = re.compile(patronvideos,re.DOTALL).findall(data)
	scrapertools.printMatches(matches)

	scrapedurl=item.url
	scrapedtitle=matches[0]
	scrapedthumbnail = ""
       	scrapedplot = ""
       	if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
       	itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )
		

	#resto generos
	'''
				<ul class="genres">
	<li><a title="Accion" href="?do=video&act=category&name=accion">Accion</a></li>
                       <li> <a title="Adolescencia" href="?do=video&act=category&name=adolescencia">Adolescencia</a></li>
                        <li> <a title="Aventuras" href="?do=video&act=category&name=aventuras">Aventuras</a></li>
                         <li> <a title="Animaci&oacute;n" href="?do=video&act=category&name=animacion">Animaci&oacute;n</a></li>
                        <li> <a title="Biografico" href="?do=video&act=category&name=biografico">Biogr&aacute;fico</a></li>
	'''
	#patronvideos  = '<ul class="genres">[^<]+'
	patronvideos = '<a title="[^"]+" href="([^"]+)">([^<]+)</a></li>'

	matches = re.compile(patronvideos,re.DOTALL).findall(data)
	scrapertools.printMatches(matches)
	for scrapedurl, scrapedtitle in matches:
        	scrapedurl = urlparse.urljoin(item.url,scrapedurl)
		scrapedthumbnail = ""
        	scrapedplot = ""
        	if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        	itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )
	return itemlist

def peliculas(item):
	logger.info("[newdivxonline.py] peliculas")

	itemlist = []


	data = scrapertools.cachePage(item.url)

	pos = data.find('TOP 20')
	if pos > 0:
		data = data[:pos]

	'''
	<div class="dlemovie-video" style="background-image:url('/uploads/dlemovie/5c9e7ee381b273a9be97619eb56621a7.jpg');">
		<div class="dlemovie-video-header">
			<div class="dlemovie-video-header-text"><a href="/?do=video&act=view&video_id=461">El vuelo del Fénix (2004)</a></div>
	'''

	# Patron de las entradas
	patronvideos  = '<div class="dlemovie-video" style="background-image:url\(\'([^\']+)[^"]+">[^<]+'
	patronvideos += '<div class="dlemovie-video-header">[^<]+'
	patronvideos += '<div class="dlemovie-video-header-text"><a href="([^"]+)">([^<]+)'

	matches = re.compile(patronvideos,re.DOTALL).findall(data)
	scrapertools.printMatches(matches)
	for match in matches:
		scrapedtitle = match[2]
        	scrapedurl = urlparse.urljoin(__URL__,match[1])
		if match[0][:4] == "http":
			scrapedthumbnail = match[0]
		elif match[0][0] == "/":
			scrapedthumbnail =  __URL__ + match[0]
		else:
			scrapedthumbnail =  urlparse.urljoin(__URL__,match[0])

        	scrapedplot = ""
        	if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        	itemlist.append( Item(channel=__channel__, action="findvideos", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )

	# paginacion
	'''
	<div class="pagination">
		<span>Back</span>
		<span>1</span> <a href="http://www.newdivxonline.com/?do=video&act=category&name=accion&page=2">2</a> <a href="http://www.newdivxonline.com/?do=video&act=category&name=accion&page=3">3</a> <a href="http://www.newdivxonline.com/?do=video&act=category&name=accion&page=4">4</a> <a href="http://www.newdivxonline.com/?do=video&act=category&name=accion&page=5">5</a> 
		 <a href="http://www.newdivxonline.com/?do=video&act=category&name=accion&page=2">Next</a>
	'''

	# Patron de las entradas
	patronvideos = '<a href="([^"]+)">Next</a>'

	matches = re.compile(patronvideos,re.DOTALL).findall(data)
	scrapertools.printMatches(matches)
	if len(matches)>0:
		scrapedurl=urlparse.urljoin(__URL__,matches[0])
        	scrapedtitle = "Página siguiente >>"
		scrapedthumbnail = ""
        	scrapedplot = ""
        	if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        	itemlist.append( Item(channel=__channel__, action="peliculas", title=scrapedtitle , url=scrapedurl , thumbnail=scrapedthumbnail , plot=scrapedplot , folder=True) )



	return itemlist

 		


