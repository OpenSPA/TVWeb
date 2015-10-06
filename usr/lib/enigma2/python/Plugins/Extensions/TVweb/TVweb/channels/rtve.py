# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para RTVE
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse, re

from core import config
from core import logger
from core import scrapertools
from core.item import Item

import urllib 
logger.info("[rtve.py] init")

DEBUG = True
CHANNELNAME = "rtve"

def isGeneric():
    return True

def mainlist(item):
    logger.info("[rtve.py] mainlist")

    itemlist = []
    
    # El primer nivel de menú es un listado por canales
    itemlist.append( Item(channel=CHANNELNAME, title="Secciones" , action="secciones" , thumbnail = "" , url="http://www.rtve.es/alacarta/programas/tve/todos/1/", extra=""))
    itemlist.append( Item(channel=CHANNELNAME, title="Canales" , action="canales" , thumbnail = "" , url="http://www.rtve.es/m/alacarta/tve/canales/?app=", extra=""))
    itemlist.append( Item(channel=CHANNELNAME, title="Telediario" , action="telediario" , thumbnail = "" , url="http://www.rtve.es/rss/mobile/android/v3/navigation-v3.xml", extra=""))

    return itemlist


def telediario(item):
    logger.info("[rtve.py] telediario")

    itemlist = []
    data = scrapertools.cachePage(item.url)

    # Extrae las paginas de telediario
    '''
	<outline type="rss" version="mandatory" text="Telediario" id="1" xmlUrl="http://www.rtve.es/aoa/agregator/telediarios.mrss"/>
	<outline type="rss" version="mandatory" text="Telediario" id="1" xmlUrl="http://www.rtve.es/aoa/agregator/secciones.mrss"/>
    '''    
    patron  = '<outline type="rss" version="mandatory" text="Telediario" id="[^"]+" xmlUrl="([^"]+)"/>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    for match in matches:
	data = scrapertools.cachePage(match)
	'''
      	<title>Telediario 2 en cuatro minutos - 19/07/12</title>
      	<link>http://www.rtve.es/alacarta/videos/telediario/telediario-2-cuatro-minutos-19-07-12/1470813/</link>
      	<description>&lt;div&gt;&lt;img src="http://img.irtve.es/imagenes/telediario-2-cuatro-minutos-19-07-12/1342725790971.jpg" /&gt;&lt;/div&gt;&lt;P&gt;Ya están en España los cooperantes Enric Gonyalons y Ainhoa Fernández, liberados ayer en Mali tras nueve meses de secuestro. --  Miles de personas se manifiestan por las calles de numerosas ciudades españolas, lo están haciendo a esta hora, contra las medidas aprobadas por el gobierno: la subida del IVA, la supresión de la extra de Navidad a los funcionarios, y la reducción de prestaciones a los nuevos parados a partir del séptimo mes. Unas medidas que hoy ha convalidado el Congreso con los votos del Partido Popular. Ajena al debate en el Congreso, la prima de riesgo, la diferencia entre el bono español y el alemán, ha marcado un nuevo récord al cierre, 580 puntos, cuatro más que ayer. Y hoy también es noticia la detención de tres históricos miembros del GRAPO, acusados del secuestro en 1995 de Publio Cordón. Según ha contado el ministro del Interior, el empresario murió a los 15 días, cuando intentó huir del zulo saltando desde un balcón y resultó malherido. Con esta operación, Interior da por resuelto el caso, a falta de localizar el cadáver. Su hija decía que ahora los jueces tienen que hacer su trabajo. -- La televisión siria ha emitido las primeras imágenes de Bachar al Assad con el nuevo ministro de Defensa, al parecer en Damasco, para acallar los rumores sobre su paradero, después del atentado de ayer. Hoy la capital sigue convertida en un campo de batalla, mientras Rusia y China han vetado por tercera vez la resolución del Consejo de Seguridad de la ONU para imponer sanciones a Siria. -- Se vende el monasterio de San Paio de Albeos, en Pontevedra. De origen prerrománico, sus propietarios piden 300.000 euros. Ahora está casi en la ruina porque se ha usado, entre otras cosas, como establo.&lt;/P&gt;&lt;div&gt;&lt;br/&gt;&lt;a href="http://www.rtve.es/alacarta/videos/telediario/telediario-2-cuatro-minutos-19-07-12/1470813/"&gt;Ver vídeo&lt;/a&gt;&lt;/div&gt;&lt;img src="http://secure-uk.imrworldwide.com/cgi-bin/m?ci=es-rssrtve&amp;cg=F-N-B-null&amp;si=http://www.rtve.es/alacarta/videos/telediario/telediario-2-cuatro-minutos-19-07-12/1470813/" alt=""/&gt;</description>
      	<pubDate>Thu, 19 Jul 2012 19:19:00 GMT</pubDate>
	'''
	patron = '<title>([^<]+)</title>[^<]+'
	patron += '<link>([^<]+)</link>[^<]+'
	patron += '<description>&lt;div&gt;&lt;img src="([^"]+)" /&gt;&lt;/div&gt;&lt;P&gt;([^&]+)&lt;/P&gt;&lt;div&gt;&lt;br/&gt;&lt;'

    	matches2 = re.findall(patron,data,re.DOTALL)
    	if DEBUG: scrapertools.printMatches(matches2)
	for entry in matches2:
       		scrapedtitle = entry[0]
       		scrapedurl = entry[1]
       		scrapedthumbnail = entry[2]
       		scrapedplot = entry[3]
       		scrapedextra = ""
       		if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
		itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = "" , category = scrapedtitle ) )

   
    return itemlist


def canales(item):
    logger.info("[rtve.py] canales")

    itemlist = []
    data = scrapertools.cachePage(item.url)

    # Extrae los canales
    '''
	<h3>La 1</h3>
	<p class="thumb"><img src="/css/alacarta20/mobile/i/content/channel_la_1.png" alt="La 1"></p>
	<a href="/m/alacarta/tve/la1/?modl=canales" class="action arrow"><span>ver este canal</span></a>
    '''    
    patron  = '<h3>([^<]+)</h3>[^<]+'
    patron += '<p class="thumb"><img src="([^"]+)" alt="[^"]+"></p>[^<]+'
    patron += '<a href="/m/alacarta/tve/([^"]+)" class="action arrow"><span>ver este canal</span></a>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    for match in matches:
        scrapedtitle = match[0]
        scrapedurl = "http://www.rtve.es/m/alacarta/programsbychannel/?media=tve&programType=&channel="+match[2].split("/")[0]+"&modl=canales&filterFindPrograms=todas"
        scrapedthumbnail = urlparse.urljoin("http://www.rtve.es",match[1])
        scrapedplot = ""
        scrapedextra = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="programas" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = "" , category = scrapedtitle ) )

   
    return itemlist

def secciones(item):
    logger.info("[rtve.py] secciones")

    itemlist = []
    # Descarga la página que tiene el desplegable de categorias de programas
    #item.url = "http://www.rtve.es/alacarta/programas/tve/todos/1/"
    data = scrapertools.cachePage(item.url)

    # Extrae las categorias de programas
    #patron  = '<li><a title="Seleccionar[^"]+" href="/alacarta/programas/tve/([^/]+)/1/"><span>([^<]+)</span></a></li>'
    patron = 'href="/alacarta/programas/tve/([^/]+)/1/"[^<]+<span>([^<]+)</span></a>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    append = True
    for match in matches:
        scrapedtitle = match[1]
        scrapedurl = match[1]
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedextra = match[0]
        scrapedurl = "http://www.rtve.es/m/alacarta/programsbycategory/?media=tve&programType="+match[0]+"&channel=&modl=categorias&filterFindPrograms=todas" 
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
	if "Música" in scrapedtitle: append = False  # No añade las secciones d emusica
	if "Informativo" in scrapedtitle: append = True # añade los informativos
	if "Documentales" in scrapedtitle: append = True
	if "Series" in scrapedtitle: append = True
	if scrapedtitle != "Infantiles" and append == True:  # No añade tampoco la seccion Infantil que esta en ClanTV      
		itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="programas" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = item.extra + "/" + scrapedextra + "/1" , category = scrapedtitle ) )

   
    return itemlist


def programas(item):
    logger.info("[rtve.py] programas")

    #item.url = "http://www.rtve.es/m/alacarta/programsbycategory/?media=tve&programType="+prog+"&channel=&modl=categorias&filterFindPrograms=todas"    

    '''
    <li class="video">
    <p class="tag">Programas</p>
    <h3>Abuela de verano</h3>
	<p class="thumb"><img src="http://img.irtve.es/imagenes/abuela-verano/1310715902531.png" alt="Abuela de verano"/></p>
	<a href="/m/alacarta/videos/abuela-de-verano/?media=tve" class="action arrow"><span>ver este programa</span></a>
    '''

    patron = '<li class="video">[^<]+'
    patron +='<p class="tag">Programas</p>[^<]+'
    patron +='<h3>([^<]+)</h3>[^<]+'
    patron +='<p class="thumb"><img src="([^"]+)" alt="[^"]+"/></p>[^<]+'
    patron +='<a href="/m([^"]+)"'

    itemlist = []
    data = scrapertools.cachePage(item.url)
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)


    # Crea una lista con las entradas
    for match in matches:
        scrapedtitle = match[0]
        scrapedurl = match[2]
	scrapedthumbnail = match[1]
        scrapedplot = ""
        scrapedextra = ""
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="temporadas" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = scrapedextra, show=scrapedtitle, category = item.category) )

    return itemlist


def temporadas(item):
    logger.info("[rtve.py] temporadas")

    # Busca el id del programa si no tiene la url definida
    if not item.url.startswith("http"):
    	url = "http://www.rtve.es"+item.url.split("?")[0]
    	data = scrapertools.cachePage(url)
    	'''
	<li class="favoritos" name="48910">
    	'''
    	patron = '<li class="favoritos" name="([^"]+)">'
    	matches = re.findall(patron,data,re.DOTALL)
    	ctx=""
    	if len(matches)>0:
        	ctx = matches[0]
	prog=item.url.split("/")[3]
	item.extra = ctx
    else:
	ctx=""
	prog = ""

    # lista de temporadas
    # http://www.rtve.es/m/alacarta/multimedialist.shtml?contentKey=&media=tve&programName=cuentame-como-paso&contentType=videos&seasonFilter=-1&sectionFilter=

    item.url = "http://www.rtve.es/m/alacarta/multimedialist.shtml?contentKey=&media=tve&programName="+prog+"&contentType=videos&seasonFilter=-1&sectionFilter="

    '''
	<option value="-1" selected="selected">Todas las temporadas</option>
	<option value="40034">T1</option>
	<option value="40017">T2</option>
	<option value="40018">T3</option>
    '''

    itemlist = []
    data = scrapertools.cachePage(item.url)


    ### <select id="season" name="seasonFilter">
    patron = '<select id="season" name="seasonFilter">(.*?)'
    patron += '</div>'

 
    matches = re.findall(patron,data,re.DOTALL)
    if len(matches)>0:
    	patron  = '<option value="([^"]+)".*?>([^<]+)</option>'
	matches = re.findall(patron,matches[0],re.DOTALL)
    	for match in matches:
		scrapedtitle = match[1]
		scrapedthumbnail = item.thumbnail
		scrapedplot = ""
		scrapedurl = "http://www.rtve.es/alacarta/interno/contenttable.shtml?ctx="+ctx+"&locale=es&pageSize=20&seasonFilter="+match[0]+"&pbq=1"
        	itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = item.extra, show=scrapedtitle, category = item.category) )

    ### <select id="section" name="sectionFilter">
    patron = '<select id="section" name="sectionFilter">(.*?)'
    patron += '</div>'

    matches = re.findall(patron,data,re.DOTALL)
    if len(matches)>0:
    	patron  = '<option value="([^"]+)".*?>([^<]+)</option>'
	matches = re.findall(patron,matches[0],re.DOTALL)
    	for match in matches:
		scrapedtitle = match[1]
		scrapedthumbnail = item.thumbnail
		scrapedplot = ""
		scrapedurl = "http://www.rtve.es/alacarta/interno/contenttable.shtml?ctx="+ctx+"&locale=es&pageSize=20&sectionFilter="+match[0]+"&pbq=1"
		if match[0] != "-1":
        		itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = item.extra, show=scrapedtitle, category = item.category) )

    if len(itemlist)==0:
	item.url = "http://www.rtve.es/alacarta/interno/contenttable.shtml?ctx="+ctx+"&pageSize=20&pbq=1"
	itemlist = episodios(item)	

    return itemlist

def episodios(item):
    logger.info("[rtve.py] episodios")
    
    # En la paginación la URL vendrá fijada, si no se construye aquí la primera página
    if item.url=="":
        # El ID del programa está en item.extra (ej: 1573)
        # La URL de los vídeos de un programa es
        # http://www.rtve.es/alacarta/interno/contenttable.shtml?ctx=1573&locale=es&pageSize=20&seasonFilter=40024
        item.url = "http://www.rtve.es/alacarta/interno/contenttable.shtml?ctx="+item.extra+"&pageSize=20&pbq=1"
    data = scrapertools.cachePage(item.url)

    itemlist = []

    # Extrae los vídeos
    patron  = '<li class="[^"]+">.*?'
    patron += '<span class="col_tit" id="([^"]+)"[^>]+>[^<]+'
    patron += '<a href="([^"]+)">(.*?)</a>[^<]+'
    patron += '</span>[^<]+'
    patron += '<span class="col_tip">(.*?)'
    patron += '<span class="col_dur">([^<]+)</span>.*?'
    patron += '<span class="col_fec">([^<]+)</span>.*?'
    patron += '<span class="detalle">([^>]+)</span>'

    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    ############# eliminado - tarda mucho ################################################################################################################
    # Extrae videos de otra pagina para las imagenes
    # http://www.rtve.es/alacarta/videoslide.shtml?ctx=1573&locale=es&pageSize=-1&seasonFilter=-1
    #url = "http://www.rtve.es/alacarta/videoslide.shtml?ctx="+item.extra+"&locale=es&pageSize=-1&seasonFilter=-1" 
    #'''
	#<a title="Cuéntame cómo pasó - T1 - Capítulo 2 " href="/alacarta/videos/cuentame-como-paso/cuentame-como-paso-t1-capitulo-2/385758/" id="385758">
	#<img title="Cuéntame cómo pasó - T1 - Capítulo 2 " alt="Cuéntame cómo pasó - T1 - Capítulo 2 " src="http://img.irtve.es/imagenes/cuentame-como-paso-t1-capitulo-2/1232619332424.jpg"/>
    #'''
    #patron2 = '<a title="[^"]+" href="[^"]+" id="([^"]+)">[^<]+'
    #patron2 += '<img title="[^"]+" alt="[^"]+" src="([^"]+)"/>'
    
    #data2 = scrapertools.cachePage(url)
    #matches2 = re.findall(patron2,data2,re.DOTALL)
    #if DEBUG: scrapertools.printMatches(matches2)
    ########################################################################################################################################################

    # Crea una lista con las entradas
    for match in matches:
        if not "developer" in config.get_platform():
            scrapedtitle = match[2]+" ("+match[4].strip()+" - "+match[5]+")"
        else:
            scrapedtitle = match[2]
        scrapedtitle = scrapedtitle.replace("<em>Nuevo</em>&nbsp;","")
        scrapedtitle = scrapertools.unescape(scrapedtitle)
        scrapedurl = urlparse.urljoin(item.url,match[1])
	# Busca la imagen
	scrapedthumbnail = item.thumbnail
	#pid=match[0]
	#for imgs in matches2:
	#	if imgs[0].strip() == pid:
	#		scrapedthumbnail = imgs[1]
	#		continue
        scrapedplot = scrapertools.unescape(match[6].strip())
        scrapedplot = scrapertools.htmlclean(scrapedplot).strip()
        scrapedextra = match[3]

        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , show=item.show, category = item.category, extra=scrapedextra, folder=False) )

    # Extrae la paginación
    patron = '<a name="paginaIR" href="([^"]+)"><span>Siguiente</span></a>'
    matches = re.findall(patron,data,re.DOTALL)
    if DEBUG: scrapertools.printMatches(matches)

    # Crea una lista con las entradas
    for match in matches:
        scrapedtitle = "!Página siguiente"
        scrapedurl = urlparse.urljoin(item.url,match).replace("&amp;","&")
        scrapedthumbnail = ""
        scrapedplot = ""
        scrapedextra = item.extra
        if (DEBUG): logger.info("title=["+scrapedtitle+"], url=["+scrapedurl+"], thumbnail=["+scrapedthumbnail+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = scrapedextra, category = item.category, show=item.show) )

    return itemlist

########### funcion para decodificar texto ofuscado: Paso1 - extrae el subtexto
def first_pass (cyphertext):
    intermediate_cyphertext = ""
    increment = 1
    text_index = 0
    while text_index < len(cyphertext):
    	intermediate_cyphertext = intermediate_cyphertext + cyphertext[text_index]
    	increment = increment + 1
    	if increment == 5: increment = 1
    	text_index = text_index + increment
    return intermediate_cyphertext


########### funcion para decodificar texto ofuscado: Paso2 - decodifica la url
def second_pass (key, cyphertext):
    plaintext = ""
    key_index = -1
    increment = 4
    while key_index < len(key):
    	key_index = key_index + 1
	if key_index < len(key):
    		text_index = int(key[key_index]) * 10
    		key_index = key_index + increment
		if key_index < len(key):
    			text_index = text_index + int(key[key_index])
    			increment = increment + 1
    			if (increment == 5): increment = 1;
			if text_index < len(cyphertext):
    				plaintext = plaintext + cyphertext[text_index]

    return plaintext





def play(item):
    logger.info("[rtve.py] play")

    # Extrae el código
    #http://www.rtve.es/mediateca/videos/20100410/telediario-edicion/741525.shtml
    #http://www.rtve.es/alacarta/videos/espana-entre-el-cielo-y-la-tierra/espana-entre-el-cielo-y-la-tierra-la-mancha-por-los-siglos-de-los-siglos/232969/
    logger.info("url="+item.url)
    patron = 'http://.*?/([0-9]+)/'
    data = item.url.replace(".shtml","/")
    matches = re.compile(patron,re.DOTALL).findall(data)
    scrapertools.printMatches(matches)
    codigo = matches[0]
    logger.info("assetid="+codigo)


    thumbnail = item.thumbnail

    ##### Nuevo metodo Octubre 2012
    #### Descargamos imagen con metadatos
    #### http://www.rtve.es/ztnr/movil/thumbnail/mandulis/videos/1538906.png
    #### direccion manager: http://www.rtve.es/odin/loki/TW96aWxsYS81LjAgKExpbnV4OyBVOyBBbmRyb2lkIDQuMC4zOyBlcy1lczsgTlZTQkwgVk9SVEVYIEJ1aWxkL0lNTDc0SykgQXBwbGVXZWJLaXQvNTM0LjMwIChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi80LjAgTW9iaWxlIFNhZmFyaS81MzQuMzA=/
    #urlimg = 'http://www.rtve.es/ztnr/movil/thumbnail/mandulis/videos/'+codigo+'.png'

    try :        
#        from lib import simplejson
        data = scrapertools.cachePage("http://www.rtve.es/odin/loki/TW96aWxsYS81LjAgKExpbnV4OyBVOyBBbmRyb2lkIDQuMC4zOyBlcy1lczsgTlZTQkwgVk9SVEVYIEJ1aWxkL0lNTDc0SykgQXBwbGVXZWJLaXQvNTM0LjMwIChLSFRNTCwgbGlrZSBHZWNrbykgVmVyc2lvbi80LjAgTW9iaWxlIFNhZmFyaS81MzQuMzA=/")                        
#        json_data = simplejson.loads(data)
#        manager=json_data["manager"]
	patron = '{"manager":"([^"]+)"}'
	matches = re.compile(patron,re.DOTALL).findall(data)
	manager = matches[0]
    except:
	manager="mandulis"

    urlimg = 'http://www.rtve.es/ztnr/movil/thumbnail/'+manager+'/videos/'+codigo+'.png'
    data = scrapertools.cachePage(urlimg)   ### descarga png con metadatos
    data = data.decode("base-64")        ### decodifica en base64
    patron = 'tEXt([^#]+)#'
    matches = re.compile(patron,re.DOTALL).findall(data)   ## extrae el texto ofuscado
    try:
    	cyphertext = matches[0]
    except:
    	cyphertext = ""
    try:
    	key = data.split('#')[1]
    	key = key[1:]         ## extrae la clave
	clave = ""
	for x in key:
		if x.isdigit():
			clave = clave + x
		else:
			break
    except:
	clave = ""

    try:
    	intermediate_cyphertext = first_pass(cyphertext)    ## primer paso: extrae el texto intermediario
    	url = second_pass (clave, intermediate_cyphertext)  ## segundo paso: decodifica la url
	if url.endswith("mp4"):
		url = url.replace("http://flash1.akamaihd.net.rtve.es/resources/TE_NGVA","http://mvod1.akcdn.rtve.es/resources/TE_GLUCA")
    except:
	url= ""
    #################################################################################


    if url == "":
    	try:
	   # Compone la URL
	   #http://www.rtve.es/api/videos/1311573/config/alacarta_videos.xml
	   url = 'http://www.rtve.es/api/videos/'+codigo+'/config/alacarta_videos.xml'
           logger.info("[rtve.py] url="+url)
           # Descarga el XML y busca el DataId
           #<cdnAssetDataId>828164</cdnAssetDataId>
           data = scrapertools.cachePage(url)
           patron = '<cdnAssetDataId>([^<]+)</cdnAssetDataId>'
           matches = re.compile(patron,re.DOTALL).findall(data)
           scrapertools.printMatches(matches)
	   url = ""
           if len(matches)>0:
           	codigo = matches[0]
           else:
           	codigo = ""
           logger.info("assetDataId="+codigo)
	   if codigo != "":
           	#url = http://www.rtve.es/ztnr/preset.jsp?idpreset=828164&lenguaje=es&tipo=video
	   	url = 'http://www.rtve.es/ztnr/preset.jsp?idpreset='+codigo+'&lenguaje=es&tipo=video'	
           	data = scrapertools.cachePage(url)
	   	# Busca la url del video
	   	# <li><em>File Name</em>&nbsp;<span class="titulo">mp4/4/8/1328228115384.mp4</span></li>
           	patron = '<li><em>File Name</em>.*?"titulo">([^<]+)</span></li>'
           	matches = re.compile(patron,re.DOTALL).findall(data)
           	scrapertools.printMatches(matches)
           	if len(matches)>0:
			# match = mp4/4/8/1328228115384.mp4
           	 	#http://www.rtve.es/resources/TE_NGVA/mp4/4/8/1328228115384.mp4
           	 	url = "http://www.rtve.es/resources/TE_NGVA/"+matches[0]
	   	else:
	   		url = ""

        except:
	   url =""

    if url == "":
    	try:
           # Compone la URL
           #http://www.rtve.es/swf/data/es/videos/alacarta/5/2/5/1/741525.xml
           url = 'http://www.rtve.es/swf/data/es/videos/alacarta/'+codigo[-1:]+'/'+codigo[-2:-1]+'/'+codigo[-3:-2]+'/'+codigo[-4:-3]+'/'+codigo+'.xml'
           logger.info("[rtve.py] url="+url)

           # Descarga el XML y busca el vídeo
           #<file>rtmp://stream.rtve.es/stream/resources/alacarta/flv/6/9/1270911975696.flv</file>
           data = scrapertools.cachePage(url)
           #print url
           #print data
           patron = '<file>([^<]+)</file>'
           matches = re.compile(patron,re.DOTALL).findall(data)
           scrapertools.printMatches(matches)
           if len(matches)>0:
          	#url = matches[0].replace('rtmp://stream.rtve.es/stream/','http://www.rtve.es/')
            	url = matches[0]
           else:
           	url = ""
        
           patron = '<image>([^<]+)</image>'
           matches = re.compile(patron,re.DOTALL).findall(data)
           scrapertools.printMatches(matches)
           #print len(matches)
           #url = matches[0].replace('rtmp://stream.rtve.es/stream/','http://www.rtve.es/')
           thumbnail = matches[0]
    	except:
           url = ""
    
    # Hace un segundo intento
    if url=="":
        try:
            # Compone la URL
            #http://www.rtve.es/swf/data/es/videos/video/0/5/8/0/500850.xml
            url = 'http://www.rtve.es/swf/data/es/videos/video/'+codigo[-1:]+'/'+codigo[-2:-1]+'/'+codigo[-3:-2]+'/'+codigo[-4:-3]+'/'+codigo+'.xml'
            logger.info("[rtve.py] url="+url)

            # Descarga el XML y busca el vídeo
            #<file>rtmp://stream.rtve.es/stream/resources/alacarta/flv/6/9/1270911975696.flv</file>
            data = scrapertools.cachePage(url)
            patron = '<file>([^<]+)</file>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            scrapertools.printMatches(matches)
            #url = matches[0].replace('rtmp://stream.rtve.es/stream/','http://www.rtve.es/')
            url = matches[0]
        except:
            url = ""
    
    if url=="":

        try:
            # Compone la URL
            #http://www.rtve.es/swf/data/es/videos/video/0/5/8/0/500850.xml
            url = 'http://www.rtve.es/swf/data/es/videos/video/'+codigo[-1:]+'/'+codigo[-2:-1]+'/'+codigo[-3:-2]+'/'+codigo[-4:-3]+'/'+codigo+'.xml'
            logger.info("[rtve.py] url="+url)

            # Descarga el XML y busca el assetDataId
            #<plugin ... assetDataId::576596"/>
            data = scrapertools.cachePage(url)
            #logger.info("[rtve.py] data="+data)
            patron = 'assetDataId\:\:([^"]+)"'
            matches = re.compile(patron,re.DOTALL).findall(data)
            scrapertools.printMatches(matches)
            #url = matches[0].replace('rtmp://stream.rtve.es/stream/','http://www.rtve.es/')
            codigo = matches[0]
            logger.info("assetDataId="+codigo)
            
            #url = http://www.rtve.es/scd/CONTENTS/ASSET_DATA_VIDEO/6/9/5/6/ASSET_DATA_VIDEO-576596.xml
            url = 'http://www.rtve.es/scd/CONTENTS/ASSET_DATA_VIDEO/'+codigo[-1:]+'/'+codigo[-2:-1]+'/'+codigo[-3:-2]+'/'+codigo[-4:-3]+'/ASSET_DATA_VIDEO-'+codigo+'.xml'
            logger.info("[rtve.py] url="+url)
            
            data = scrapertools.cachePage(url)
            #logger.info("[rtve.py] data="+data)
            patron  = '<field>[^<]+'
            patron += '<key>ASD_FILE</key>[^<]+'
            patron += '<value>([^<]+)</value>[^<]+'
            patron += '</field>'
            matches = re.compile(patron,re.DOTALL).findall(data)
            scrapertools.printMatches(matches)
            codigo = matches[0]
            logger.info("[rtve.py] url="+url)
            
            #/deliverty/demo/resources/mp4/4/3/1290960871834.mp4
            #http://media4.rtve.es/deliverty/demo/resources/mp4/4/3/1290960871834.mp4
            #http://www.rtve.es/resources/TE_NGVA/mp4/4/3/1290960871834.mp4
            url = "http://www.rtve.es/resources/TE_NGVA"+codigo[-26:]

        except:
            url = ""
    logger.info("[rtve.py] url="+url)

    itemlist = []
    if url=="":
        logger.info("[rtve.py] Extrayendo URL tipo iPad")
        headers = []
        headers.append( ["User-Agent","Mozilla/5.0 (iPad; U; CPU OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B334b Safari/531.21.10"] )
        location = scrapertools.get_header_from_response(item.url,headers=headers,header_to_get="location")
        logger.info("[rtve.py] location="+location)
        
        data = scrapertools.cache_page(location,headers=headers)
        #<a href="/usuarios/sharesend.shtml?urlContent=/resources/TE_SREP63/mp4/4/8/1334334549284.mp4" target
        url = scrapertools.get_match(data,'<a href="/usuarios/sharesend.shtml\?urlContent\=([^"]+)" target')
        logger.info("[rtve.py] url="+url)
        #http://www.rtve.es/resources/TE_NGVA/mp4/4/8/1334334549284.mp4
        url = urlparse.urljoin("http://www.rtve.es",url)
        logger.info("[rtve.py] url="+url)

    if url!="":
        itemlist.append( Item(channel=CHANNELNAME, title=item.title , action="play" , url=url, thumbnail=thumbnail , plot=item.plot , server = "directo" , show = item.title , folder=False) )

    return itemlist
