# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para disney channel
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

def get_video_url( page_url , premium = False , user="" , password="", video_password="" ):
    logger.info("[disneychannel.py] get_video_url(page_url='%s')" % page_url)
    video_urls = []

    # Descarga la página
    # http://replay.disneychannel.es/phineas-y-ferb/el-lado-doof-de-la-luna.html
    data = scrapertools.cache_page(page_url)
    patron = "player_\d+_DISNEYCHAPTER_\d+.xml='([^']+)'"
    matches = re.findall(patron,data,re.DOTALL)
    if len(matches)==0:
        return []
    url = matches[0]

    # Descarga el xml
    # http://replay.disneychannel.es/chapterxml/10/2011/11/17/00022.xml
    url = urlparse.urljoin(page_url,url)
    data = scrapertools.cache_page(url)
    logger.info("data="+data)
    '''
    <?xml version="1.0" encoding="UTF-8"?><dataViewer>
    <url>
    <urlImg><![CDATA[http://replay.disneychannel.es/]]></urlImg>
    <urlVideoFlv><![CDATA[rtmp://antena3fs.fplive.net/videos/swf/]]></urlVideoFlv>
    <urlVideoMp4><![CDATA[rtmp://flashstreaming.disneyinternational.com/ondemand/antena3tv/]]></urlVideoMp4>
    <urlHttpVideo><![CDATA[http://replay.disneychannel.es/antena3tv/]]></urlHttpVideo>
    <urlSmil><![CDATA[http://www.antena3.com/player/]]></urlSmil>
    <fullDuration><![CDATA[687]]></fullDuration>
    <aliases>
    <alias device="samsung" value="tvsamsung"/>
    <alias device="philips" value="tvphilips"/>
    <alias device="sharp" value="tvsharp"/>
    <alias device="lg" value="tvlg"/>
    <alias device="ps3" value="tvps3"/>
    <alias device="ipad" value="tvipad"/>
    <alias device="iphone" value="tviphone"/>
    </aliases>
    </url>
    <multimedias>
    <multimedia isEmbeb="0" tipo="2">
    <nombre><![CDATA[El Lado Doof de la Luna]]></nombre>
    <descripcion><![CDATA[Phineas y Ferb son dos hermanastros que quieren disfrutar al máximo de las vacaciones de verano haciendo, básicamente, travesuras (para fastidio de su hermana Candace). ]]></descripcion>
    <seccion><![CDATA[Phineas y Ferb]]></seccion>
    <info><![CDATA[El Lado Doof de la Luna]]></info>
    <clasificacion><![CDATA[]]></clasificacion>
    <aspecto><![CDATA[16/9]]></aspecto>
    <duration><![CDATA[687]]></duration>
    <urlShared><![CDATA[]]></urlShared>
    <urlEmbebed><![CDATA[]]></urlEmbebed>
    <archivoMultimedia>
    <archivo><![CDATA[mp_seriesh2/2011/11/17/00022/001.mp4]]></archivo>
    <alt><![CDATA[]]></alt>
    </archivoMultimedia>
    <archivoMultimediaMaxi>
    <archivo><![CDATA[clipping/2011/11/17/00021/8.jpg]]></archivo>
    <alt><![CDATA[]]></alt>
    </archivoMultimediaMaxi>
    </multimedia>
    <relacionados/>
    </multimedias>
    </dataViewer>
    '''
    try:
        url_base = scrapertools.get_match( data,"<urlHttpVideo><\!\[CDATA\[([^\]]+)\]\]></urlHttpVideo>" )
        patron_url_video = "<archivoMultimedia>[^<]+<archivo><\!\[CDATA\[([^\]]+)\]\]></archivo>"
        matches = re.compile(patron_url_video,re.DOTALL).findall(data)
        #if DEBUG: scrapertools.printMatches(matches)
        parte = 1
        for url_video in matches:
            url = url_base + url_video
            logger.info("url="+url)

            if len(matches)>1:
                video_urls.append( [ "(parte "+str(parte)+") [disneychannel]" , url ] )
                parte = parte + 1
            else:
                video_urls.append( [ "[disneychannel]" , url ] )
    except:
        import traceback
        logger.info(traceback.format_exc())

    for video_url in video_urls:
        logger.info("[disneychannel.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    patronvideos  = '(http://replay.disneychannel.es/[^/]+/.*?.html)'
    logger.info("[disneychannel.py] find_videos #"+patronvideos+"#")
    matches = re.compile(patronvideos,re.DOTALL).findall(data)

    for match in matches:
        titulo = "[disneychannel]"
        url = match
        if url not in encontrados:
            logger.info("  url="+url)
            devuelve.append( [ titulo , url , 'disneychannel' ] )
            encontrados.add(url)
        else:
            logger.info("  url duplicada="+url)
            
            
    return devuelve

