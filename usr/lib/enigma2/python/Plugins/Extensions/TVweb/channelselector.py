# -*- coding: utf-8 -*-
import urlparse,urllib2,urllib,re
import os
import sys
from core import scrapertools
from core import config
from core import logger
from core.item import Item
from Components.config import config, ConfigYesNo

DEBUG = True
CHANNELNAME = "channelselector"

config.plugins.TVweb.showadultcontent = ConfigYesNo(default=False)


def getmainlist():
    logger.info("[channelselector.py] getmainlist")
    itemlist = []

    itemlist.append( Item(title=config.get_localized_string(30118) , channel="channelselector" , action="channeltypes") )
    itemlist.append( Item(title=config.get_localized_string(30102) , channel="favoritos" , action="mainlist") )
    itemlist.append( Item(title=config.get_localized_string(30101) , channel="descargas" , action="mainlist") )
    itemlist.append( Item(title=config.get_localized_string(30100) , channel="configuracion" , action="mainlist") )

    return itemlist

def mainlist(params,url,category):
    logger.info("[channelselector.py] mainlist")

    # Verifica actualizaciones solo en el primer nivel
    if config.get_platform()!="boxee":
        try:
            from core import updater
        except ImportError:
            logger.info("[channelselector.py] No disponible modulo actualizaciones")
        else:
            if config.get_setting("updatecheck2") == "true":
                logger.info("[channelselector.py] Verificar actualizaciones activado")
                updater.checkforupdates()
            else:
                logger.info("[channelselector.py] Verificar actualizaciones desactivado")

    itemlist = getmainlist()
    for elemento in itemlist:
        logger.info("[channelselector.py] item="+elemento.title)
        addfolder(elemento.title,elemento.channel,elemento.action)

    # Label (top-right)...
    import xbmcplugin
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def getchanneltypes():
    logger.info("[channelselector.py] getchanneltypes")
    itemlist = []
#    itemlist.append( Item( title=config.get_localized_string(30121) , channel="channelselector" , action="listchannels" , category="*"   , thumbnail="channelselector"))
    itemlist.append( Item( title="Nacionales" , channel="nacionales" , action="listchannels" , category="N"   , thumbnail="nacionales", type="generic"))
    itemlist.append( Item( title="Autonómicos" , channel="autonomicos" , action="listchannels" , category="A"   , thumbnail="autonomicos", type="generic"))
    itemlist.append( Item( title="Locales" , channel="locales" , action="listchannels" , category="L"   , thumbnail="locales", type="generic"))
    itemlist.append( Item( title="Temáticos" , channel="tematicos" , action="listchannels" , category="T"   , thumbnail="tematicos", type="generic"))
    itemlist.append( Item( title="Infantiles" , channel="infantil" , action="listchannels" , category="I"   , thumbnail="infantil", type="generic"))
    itemlist.append( Item( title="Videoclub" , channel="videoclub" , action="listchannels" , category="V" , thumbnail="videoclub", type="generic"))
    if config.plugins.TVweb.showadultcontent.value == True: itemlist.append( Item( title="Adultos" , channel="adultos" , action="listchannels" , category="X" , thumbnail="adultos", type="generic"))
    return itemlist

def channeltypes(params,url,category):
    logger.info("[channelselector.py] channeltypes")

    lista = getchanneltypes()
    for item in lista:
        addfolder(item.title,item.channel,item.action,item.category,item.thumbnail)

    # Label (top-right)...
    import xbmcplugin
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def listchannels(params,url,category):
    logger.info("[channelselector.py] listchannels")

    lista = filterchannels(category)
    for channel in lista:
        if "xbmc" in config.get_platform() and (channel.type=="xbmc" or channel.type=="generic"):
            addfolder(channel.title , channel.channel , "mainlist" , channel.channel)

        elif config.get_platform()=="boxee" and channel.extra!="rtmp":
            addfolder(channel.title , channel.channel , "mainlist" , channel.channel)

    # Label (top-right)...
    import xbmcplugin
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=category )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

def filterchannels(category):
    returnlist = []

    idiomav=""

    if category=="NEW":
        channelslist = channels_history_list()
        for channel in channelslist:
            # Pasa si no ha elegido "todos" y no está en el idioma elegido
            if channel.language<>"" and idiomav<>"" and idiomav not in channel.language:
                #logger.info(channel[0]+" no entra por idioma #"+channel[3]+"#, el usuario ha elegido #"+idiomav+"#")
                continue
            returnlist.append(channel)
    else:
        channelslist = channels_list()
    
        for channel in channelslist:
            # Pasa si no ha elegido "todos" y no está en la categoría elegida
            if category<>"*" and category not in channel.category:
                #logger.info(channel[0]+" no entra por tipo #"+channel[4]+"#, el usuario ha elegido #"+category+"#")
                continue
            # Pasa si no ha elegido "todos" y no está en el idioma elegido
            if channel.language<>"" and idiomav<>"" and idiomav not in channel.language:
                #logger.info(channel[0]+" no entra por idioma #"+channel[3]+"#, el usuario ha elegido #"+idiomav+"#")
                continue
            returnlist.append(channel)

    return returnlist

def channels_history_list():
    itemlist = []
    itemlist.append( Item( title="La Sexta (05/04/2012)"                   , channel="lasexta"        , language="ES" , category="N" , type="generic"  ))  # jesus 05/04/2012
    itemlist.append( Item( title="El Trece TV (05/04/2012)"                , channel="eltrece"        , language="ES" , category="N" , type="generic"  ))  # jesus 05/04/2012
    itemlist.append( Item( title="Mitele (05/04/2012)"                     , channel="mitele"         , language="ES" , category="I" , type="generic"  ))  # jesus, truenon, boludiko 05/04/2012
    itemlist.append( Item( title="Cartoonito (05/04/2012)"                 , channel="cartoonito"     , language="ES" , category="I" , type="generic"  ))  # jesus 05/04/2012
    itemlist.append( Item( title="Kideos (05/04/2012)"                     , channel="kideos"         , language="ES" , category="I" , type="generic"  ))  # jesus 05/04/2012
    itemlist.append( Item( title="Cromokids (05/04/2012)"                  , channel="cromokids"      , language="ES" , category="I" , type="generic"  ))  # jesus 05/04/2012
    itemlist.append( Item( title="Disney Channel Replay (05/04/2012)"      , channel="disneychannel"  , language="ES" , category="I" , type="generic"  ))  # jesus 05/04/2012
    itemlist.append( Item( title="Skai Folders (05/04/2012)"               , channel="skai_folders"   , language="ES" , category="I" , type="generic"  ))  # dusan 04/12/2011
    itemlist.append( Item( title="Aragón TV (25/01/2012)"                  , channel="aragontv"       , language="ES" , category="A" , type="generic"  ))  # jesus 25/01/2012
    itemlist.append( Item( title="Telefe (22/01/2012)"                     , channel="telefe"         , language="ES" , category="N" , type="generic"  ))  # jesus 22/01/2012
    itemlist.append( Item( title="UPV TV (29/03/2011)"                     , channel="upvtv"          , language="ES" , category="T" , type="generic"  ))  # beesop 29/03/2011
    itemlist.append( Item( title="Boing (07/02/2011)"                      , channel="boing"          , language="ES" , category="I" , type="generic"  ))  # juanfran 07/02/2011
    itemlist.append( Item( title="IB3 (Islas Baleares) (20/01/2011)"       , channel="ib3"            , language="ES" , category="A" , type="generic"  ))  # jesus 20/01/2010
    itemlist.append( Item( title="Giralda TV (Sevilla) (20/01/2011)"       , channel="giraldatv"      , language="ES" , category="L" , type="generic"  ))  # jesus 20/01/2010
    return itemlist

def channels_list():
    itemlist = []
    itemlist.append( Item( title="TVE"                        , channel="rtve"                 , language="ES" , category="N"   , type="generic" ))
    #itemlist.append( Item( title="Antena3"                    , channel="antena3"              , language="ES" , category="I,N" , type="generic", extra="rtmp" ))
    itemlist.append( Item( title="A3Media"                    , channel="a3media"              , language="ES" , category="I,N" , type="generic", extra="rtmp" ))
    itemlist.append( Item( title="Aragón TV"                  , channel="aragontv"             , language="ES" , category="A"   , type="generic", extra="rtmp" ))  # jesus 25/01/2012
    itemlist.append( Item( title="Boing"                      , channel="boing"                , language="ES" , category="I"   , type="generic" ))   # juanfran 07/02/2011
    itemlist.append( Item( title="Cartoonito"                 , channel="cartoonito"           , language="ES" , category="I"   , type="generic" ))
    itemlist.append( Item( title="Clan TVE"                   , channel="clantve"              , language="ES" , category="I"   , type="generic" ))
    itemlist.append( Item( title="Disney Channel Replay"      , channel="disneychannel"        , language="ES" , category="I"   , type="generic" ))#  jesus 05/04/2012
    itemlist.append( Item( title="Extremadura TV"             , channel="extremaduratv"        , language="ES" , category="A"   , type="generic", extra="rtmp" ))
    itemlist.append( Item( title="Telemadrid"                 , channel="telemadrid"     , language="ES" , category="A" , type="generic", extra="rtmp" ))  # jesus 17/12/2012
    itemlist.append( Item( title="EITB (País Vasco)"          , channel="eitb"           , language="ES" , category="A" , type="generic", extra="rtmp" )) # jesus 17/12/2012
    itemlist.append( Item( title="Giralda TV (Sevilla)"       , channel="giraldatv"            , language="ES" , category="L"   , type="generic" ))  # jesus 20/01/2010
    itemlist.append( Item( title="Internautas TV"             , channel="internautastv"        , language="ES" , category="T"   , type="generic" ))
    itemlist.append( Item( title="MTV"             , channel="mtv"        , language="ES" , category="T"   , type="generic" ))
    itemlist.append( Item( title="Hogar Util"             , channel="hogarutil"        , language="ES" , category="T"   , type="generic" ))
    itemlist.append( Item( title="ADN Stream"             , channel="adnstream"        , language="ES" , category="T"   , type="generic" ))
   #itemlist.append( Item( title="RojaDirecta"             , channel="rojadirecta"        , language="ES" , category="T"   , type="generic" ))
    itemlist.append( Item( title="Mitele"                     , channel="mitele"               , language="ES" , category="I,N" , type="generic" ))
    itemlist.append( Item( title="RTVA (Andalucia)"           , channel="rtva"                 , language="ES" , category="A"   , type="generic" ))
    itemlist.append( Item( title="RTVV (Valencia)", channel="rtvv"                 , language="ES" , category="A"   , type="generic" ))
    itemlist.append( Item( title="RTVCM (Castilla La Mancha)" , channel="rtvcm"                , language="ES" , category="A" , type="generic"  ))  # jesus 01/01/2013
    #itemlist.append( Item( title="La Sexta"                   , channel="lasexta"              , language="ES" , category="N"   , type="generic" ))  # juanfran 07/02/2011
    itemlist.append( Item( title="TV3 (Cataluña)"             , channel="tv3"                  , language="ES" , category="I,A" , type="generic" ))
    itemlist.append( Item( title="NewDivx"               , channel="newdivx"              , language="ES"    , category="V"     , type="generic"  ))
    itemlist.append( Item( title="Pelis24"               , channel="pelis24"              , language="ES"    , category="V"     , type="generic"  ))
    #itemlist.append( Item( title="Tucinecom"               , channel="tucinecom"              , language="ES"    , category="V"     , type="generic"  ))
    itemlist.append( Item( title="Newpct"               , channel="newpct"              , language="ES"    , category="V"     , type="generic"  ))
    itemlist.append( Item( title="PelisPekes"               , channel="pelispekes"              , language="ES" , category="I"        , type="generic"  ))
    itemlist.append( Item( title="Shurweb"       , channel="shurweb"             , language="ES"      , category="V" , type="generic"    ))
    itemlist.append( Item( title="Series Yonkis"             , channel="seriesyonkis"             , language="ES" , category="V"        , type="generic"  ))
    itemlist.append( Item( title="Peliculas Yonkis"             , channel="peliculasyonkis_generico"             , language="ES" , category="V"        , type="generic"  ))
    itemlist.append( Item( title="Cinetube"             , channel="cinetube"             , language="ES" , category="V"        , type="generic"  ))
    #itemlist.append( Item( title="NewHD"             , channel="newhd"             , language="ES" , category="V"        , type="generic"  ))
    #itemlist.append( Item( title="Cinetux"             , channel="cinetux"             , language="ES" , category="V"        , type="generic"  ))
    itemlist.append( Item( title="DocumaniaTV"           , channel="documaniatv"          , language="ES"    , category="T"       , type="generic"  ))
    itemlist.append( Item( title="vepelis"             , channel="vepelis"             , language="ES" , category="V"        , type="generic"  ))
    if config.plugins.TVweb.showadultcontent.value == True: itemlist.append( Item( title="xhamster"          , channel="xhamster"             , language="ES" , category="X" , type="generic"  ))
    if config.plugins.TVweb.showadultcontent.value == True: itemlist.append( Item( title="PeliculasEroticas"          , channel="peliculaseroticas"             , language="ES" , category="X" , type="generic"  ))
    if config.plugins.TVweb.showadultcontent.value == True: itemlist.append( Item( title="tuporno.tv"          , channel="tupornotv"             , language="ES" , category="X" , type="generic"  ))
    if config.plugins.TVweb.showadultcontent.value == True: itemlist.append( Item( title="Beeg"          , channel="beeg"             , language="ES" , category="X" , type="generic"  ))


    return itemlist

def addfolder(nombre,channelname,accion,category="",thumbnailname=""):
    #print "addfolder"
    if category == "":
        try:
            category = unicode( nombre, "utf-8" ).encode("iso-8859-1")
        except:
            pass
    
    import xbmc

    if config.get_setting("thumbnail_type")=="0":
        IMAGES_PATH = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'resources' , 'images' , 'posters' ) )
    elif config.get_setting("thumbnail_type")=="1":
        IMAGES_PATH = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'resources' , 'images' , 'banners' ) )
    elif config.get_setting("thumbnail_type")=="2":
        IMAGES_PATH = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'resources' , 'images' , 'squares' ) )
    
    if config.get_setting("thumbnail_type")=="0":
        WEB_PATH = "http://tvalacarta.mimediacenter.info/posters/"
    elif config.get_setting("thumbnail_type")=="1":
        WEB_PATH = "http://tvalacarta.mimediacenter.info/banners/"
    elif config.get_setting("thumbnail_type")=="2":
        WEB_PATH = "http://tvalacarta.mimediacenter.info/squares/"

    if config.get_platform()=="boxee":
        IMAGES_PATH="http://tvalacarta.mimediacenter.info/posters/"

    if thumbnailname=="":
        thumbnailname = channelname

    # Preferencia: primero JPG
    thumbnail = thumbnailImage=os.path.join(IMAGES_PATH, thumbnailname+".jpg")
    # Preferencia: segundo PNG
    if not os.path.exists(thumbnail):
        thumbnail = thumbnailImage=os.path.join(IMAGES_PATH, thumbnailname+".png")
    # Preferencia: tercero WEB
    if not os.path.exists(thumbnail):
        thumbnail = thumbnailImage=WEB_PATH+thumbnailname+".png"
    #Si no existe se usa el logo del plugin
    #if not os.path.exists(thumbnail):
    #    thumbnail = thumbnailImage=WEB_PATH+"ayuda.png" #Check: ruta del logo

    import xbmcgui
    import xbmcplugin
    #logger.info("thumbnail="+thumbnail)
    listitem = xbmcgui.ListItem( nombre , iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
    itemurl = '%s?channel=%s&action=%s&category=%s' % ( sys.argv[ 0 ] , channelname , accion , category )
    xbmcplugin.addDirectoryItem( handle = int(sys.argv[ 1 ]), url = itemurl , listitem=listitem, isFolder=True)
