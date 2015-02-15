# -*- coding: utf-8 -*-
#------------------------------------------------------------
# tvalacarta - XBMC Plugin
# Canal para Clan TV
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------
import urlparse,re

from core import logger
from core import scrapertools
from core.item import Item
from core import jsontools

DEBUG = True
CHANNELNAME = "clantve"

def isGeneric():
    return True

def mainlist(item):
    logger.info("tvalacarta.channels.clantv mainlist")

    itemlist = []
    #itemlist.append( Item(channel=CHANNELNAME, title="Últimos vídeos añadidos" , url="http://www.rtve.es/infantil/components/TE_INFDEF/videos/videos-1.inc" , action="ultimos_videos" , folder=True) )
    itemlist.append( Item(channel=CHANNELNAME, title="Todos los programas" , url="http://www.rtve.es/api/agr-programas/490/programas.json?size=60&page=1" , action="programas" , folder=True) )
    return itemlist

def programas(item):
    logger.info("tvalacarta.channels.clantv programas")

    itemlist = []

    # Descarga la página
    data = scrapertools.cache_page(item.url)
    logger.info("data="+data)
    json_object = jsontools.load_json(data)
    logger.info("json_object="+repr(json_object))
    json_items = json_object["page"]["items"]

    for json_item in json_items:
        title = json_item["name"]
        url = json_item["uri"]
        thumbnail = json_item["imgPoster"]
        if json_item["description"] is not None:
            plot = json_item["description"]
        else:
            plot = ""
        fanart = json_item["imgPortada"]
        page = url
        if (DEBUG): logger.info(" title=["+repr(title)+"], url=["+repr(url)+"], thumbnail=["+repr(thumbnail)+"] plot=["+repr(plot)+"]")
        itemlist.append( Item(channel=CHANNELNAME, title=title , action="episodios" , url=url, thumbnail=thumbnail, plot=plot , page=page, show=title , fanart=fanart, viewmode="movie_with_plot", folder=True) )

    # Añade el resto de páginas
    current_page = scrapertools.find_single_match(item.url,'page=(\d+)')
    next_page = str( int(current_page)+1 )
    itemlist.append(Item(channel=CHANNELNAME,action="programas",title=">> Página siguiente",url=item.url.replace("page="+current_page,"page="+next_page), folder=True))

    return itemlist

def episodios(item):
    logger.info("tvalacarta.channels.clantv episodios")

    itemlist = []

    # Descarga la página
    url = item.url+"/videos.json"
    data = scrapertools.cache_page(url)
    json_object = jsontools.load_json(data)
    #logger.info("json_object="+json_object)
    json_items = json_object["page"]["items"]

    for json_item in json_items:
        title = json_item["longTitle"]
        url = json_item["uri"]
        thumbnail = item.thumbnail
        if json_item["description"] is not None:
            plot = json_item["description"]
        else:
            plot = ""
        fanart = item.fanart
        page = url
        if (DEBUG): logger.info(" title=["+repr(title)+"], url=["+repr(url)+"], thumbnail=["+repr(thumbnail)+"] plot=["+repr(plot)+"]")
        itemlist.append( Item(channel="rtve", title=title , action="play" , server="rtve", page=page, url=url, thumbnail=thumbnail, fanart=thumbnail, show=item.show , plot=plot , viewmode="movie_with_plot", folder=False) )

    from core import config
    if (config.get_platform().startswith("xbmc") or config.get_platform().startswith("boxee")) and len(itemlist)>0:
        itemlist.append( Item(channel=item.channel, title=">> Opciones para esta serie", url=item.url, action="serie_options##episodios", thumbnail=item.thumbnail, show=item.show, folder=False))

    return itemlist

# Copiado de servers/rtve.py para poder actualizar el canal
def play(item):
    logger.info("tvalacarta.channels.clantv play")

    itemlist = []

    # Extrae el código
    logger.info("url="+item.url)
    codigo = scrapertools.find_single_match(item.url,'http://.*?/([0-9]+)')
    url=""
    itemlist = []
    logger.info("assetid="+codigo)

    # Código sacado de PyDownTV, gracias @aabilio :)
    # https://github.com/aabilio/PyDownTV2/blob/master/spaintvs/tve.py
    # -- Método 24 Mayo 2013
    videoID = codigo
    logger.info("Probando método de 24 de uno de Mayo de 2013")
    tipo = "videos"
    url = "http://www.rtve.es/ztnr/movil/thumbnail/default/%s/%s.png" % (tipo, videoID)

    logger.info("Probando url:"+url)
    logger.info("Manager default")    
    from base64 import b64decode as decode
    tmp_ = decode(scrapertools.cachePage(url))
    if tmp_== "" :
        url = "http://www.rtve.es/ztnr/movil/thumbnail/anubis/%s/%s.png" % (tipo, videoID)
        tmp_ = decode(scrapertools.cachePage(url)) 
        logger.info("Manager anubis") 
    tmp = re.findall(".*tEXt(.*)#[\x00]*([0-9]*).*", tmp_)[0]
    tmp = [n for n in tmp]
    cyphertext = tmp[0]
    key = tmp[1]
    tmp = tmp = [0 for n in range(500)]

    # Créditos para: http://sgcg.es/articulos/2012/09/11/nuevos-cambios-en-el-mecanismo-para-descargar-contenido-multimedia-de-rtve-es-2/
    intermediate_cyphertext = ""
    increment = 1
    text_index = 0
    while text_index < len(cyphertext):
        text_index = text_index + increment
        try: intermediate_cyphertext = intermediate_cyphertext + cyphertext[text_index-1]
        except: pass
        increment = increment + 1
        if increment == 5: increment = 1

    plaintext = ""
    key_index = 0
    increment = 4
    while key_index < len(key):
        key_index = key_index + 1
        text_index = int(key[key_index-1]) * 10
        key_index = key_index + increment
        try: text_index = text_index + int(key[key_index-1])
        except: pass
        text_index = text_index + 1
        increment = increment + 1
        if increment == 5: increment = 1
        try: plaintext = plaintext + intermediate_cyphertext[text_index-1]
        except: pass

    urlVideo = plaintext
    if urlVideo != "":
        url_video = urlVideo.replace("www.rtve.es", "media5.rtve.es")
    else:
        logger.info("No se pudo encontrar el enlace de descarga")
    url=urlVideo
    logger.info("url="+url)

    itemlist.append( Item(channel="rtve", title=title , action="play" , url=url, thumbnail=thumbnail, fanart=thumbnail, show=item.show , plot=plot ,folder=False) )

    return itemlist
