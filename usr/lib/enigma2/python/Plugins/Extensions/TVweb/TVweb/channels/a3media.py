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


from hashlib import md5
trans_5C = "".join(chr(x ^ 0x5c) for x in xrange(256))
trans_36 = "".join(chr(x ^ 0x36) for x in xrange(256))
blocksize = md5().block_size

def HmacMD5(key, msg):
	if len(key) > blocksize:
		key = md5(key).digest()
	key += chr(0) * (blocksize - len(key))
	o_key_pad = key.translate(trans_5C)
	i_key_pad = key.translate(trans_36)
	return md5(o_key_pad + md5(i_key_pad + msg).digest())

def isGeneric():
    return True

def mainlist(item):
    logger.info("[a3media.py] mainlist")

    url="http://servicios.atresplayer.com/api/mainMenu"
    data = scrapertools.cachePage(url)
    logger.info(data)
    lista = load_json(data)[0]
    if lista == None: lista =[]
  
    url2="http://servicios.atresplayer.com/api/categorySections/"
    itemlist = []

    itemlist.append( Item(channel=CHANNELNAME, title="Destacados" , action="episodios" , url="http://servicios.atresplayer.com/api/highlights", folder=True) )

    for entry in lista['menuItems']:
	eid = entry['idSection']
	scrapedtitle = entry['menuTitle']
	scrapedurl = url2 + str(eid)
    
        itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="secciones" , url=scrapedurl, folder=True) )

    itemlist.append( Item(channel=CHANNELNAME, title="A.....Z" , action="secciones" , url="http://servicios.atresplayer.com/api/sortedCategorySections", folder=True) )


    return itemlist

def secciones(item):
    logger.info("[a3media.py] secciones")

    data = scrapertools.cachePage(item.url)
    logger.info(data)
    lista = load_json(data)
    if lista == None: lista =[]

    itemlist = []

    for entrys in lista:
	entry = entrys['section']
	extra = entry['idSection']
	scrapedtitle = entry['menuTitle']
	scrapedurl = item.url
	if entry.has_key('storyline'): scrapedplot = entry['storyline']
	else: scrapedplot = ""
	scrapedthumbnail = entry['urlImage'].replace('.jpg','03.jpg')
 
	if entry['drm'] == False: ##solo añade las secciones con visualizacion no protegida  
        	# Añade al listado
        	itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="temporadas" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra=extra, folder=True) )

    return itemlist

def temporadas(item):
    logger.info("[a3media.py] temporadas")

    data = scrapertools.cachePage(item.url)
    logger.info(data)
    lista = load_json(data)
    if lista == None: lista =[]

    url2="http://servicios.atresplayer.com/api/episodes/"
    itemlist = []

    scrapedplot=""
    n = 0
    ids = None
    for entrys in lista:
	entry = entrys['section']
	if entry['idSection'] == item.extra:
	    ids = entry['idSection']
	    if entry.has_key('subCategories'):
		for temporada in entry['subCategories']:
			n += 1
			extra = temporada['idSection']
			scrapedtitle = temporada['menuTitle']
			scrapedurl = url2 + str(extra)
			if temporada.has_key('storyline'): scrapedplot = temporada['storyline']
			else: scrapedplot = item.plot
			scrapedthumbnail = entry['urlImage'].replace('.jpg','03.jpg')
    
        		# Añade al listado
        		itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="episodios" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra=extra, folder=True) )


    if n == 1:  #si solo hay una temporada cargar los episodios
	itemlist = episodios(itemlist[0])

    if n == 0 and ids != None:  #si no hay temporadas pueden ser mas secciones
	item.url = "http://servicios.atresplayer.com/api/categorySections/" + str(ids)
	itemlist = secciones(item)

    return itemlist

def episodios(item):
    logger.info("[a3media.py] episodios")

    data = scrapertools.cachePage(item.url)
    logger.info(data)
    lista = load_json(data)

    if lista == None: lista =[]

    itemlist = []

    if lista.has_key('episodes'):
    	episodes = lista['episodes']
    elif lista.has_key('items'):
    	episodes = lista['items']
    else:
	episodes = []
	
    for entrys in episodes:
    	if entrys.has_key('episode'):
		entry = entrys['episode']
		tipo = entry['type']
		episode = entry['contentPk']
		scrapedtitle = entry['name']
		if tipo == "REGISTER":
			scrapedtitle = scrapedtitle + " (R)"
		elif tipo == "PREMIUM":
			scrapedtitle = scrapedtitle + " (P)"
	
		scrapedurl = "http://servicios.atresplayer.com/api/urlVideo/%s/%s/" % (episode, "android_tablet") 
		extra = episode
		if entry.has_key('storyline'): scrapedplot = entry['storyline']
		else: scrapedplot = item.plot
		scrapedthumbnail = entry['urlImage'].replace('.jpg','03.jpg')
    
		if tipo == "FREE": #solo carga los videos que no necesitan registro ni premium
			# Añade al listado
			itemlist.append( Item(channel=CHANNELNAME, title=scrapedtitle , action="play" , url=scrapedurl, thumbnail=scrapedthumbnail, plot=scrapedplot , extra = extra, folder=False) )

    return itemlist

def play(item):
    logger.info("[a3media.py] play")

    token = d(item.extra, "puessepavuestramerced")
    url = item.url + token

    data = scrapertools.cachePage(url)
    logger.info(data)
    lista = load_json(data)
    itemlist = []
    if lista != None: 
	item.url = lista['resultObject']['es']
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




