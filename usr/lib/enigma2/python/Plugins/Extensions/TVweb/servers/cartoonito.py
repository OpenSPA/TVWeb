# -*- coding: utf-8 -*-
#------------------------------------------------------------
# pelisalacarta - XBMC Plugin
# Conector para cartoonito
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/
#------------------------------------------------------------

import urlparse,urllib2,urllib,re
import os

from core import scrapertools
from core import logger
from core import config

import pyamf
from pyamf import remoting
import httplib, socket

def get_video_url( page_url , premium = False , user="" , password="", video_password="", page_data="" ):
    logger.info("[cartoonito.py] get_video_url(page_url='%s')" % page_url)

    #http://cartoonito.cartoonnetwork.es/serie/escuela-de-bomberos/videos/una-fant%C3%A1stica-captura
    data = scrapertools.cache_page(page_url)

    '''
    jQuery.extend(Drupal.settings, {"basePath":"\/","googleanalytics":{"trackOutgoing":1,"trackMailto":1,"trackDownload":1,"trackDownloadExtensions":"7z|aac|arc|arj|asf|asx|avi|bin|csv|doc|exe|flv|gif|gz|gzip|hqx|jar|jpe?g|js|mp(2|3|4|e?g)|mov(ie)?|msi|msp|pdf|phps|png|ppt|qtm?|ra(m|r)?|sea|sit|tar|tgz|torrent|txt|wav|wma|wmv|wpd|xls|xml|z|zip"},"brightcovePlayer":{"params":{"bgcolor":"3a6ea5","width":"600","height":"356","isVid":"true","isUI":"true","dynamicStreaming":"true","autoStart":"true","wmode":"transparent","templateLoadHandler":"turnerOnTemplateLoaded","templateReadyHandler":"turnerOnTemplateReady","templateErrorHandler":"turnerOnTemplateError","externalAds":"true","adServerURL":"http:\/\/adserver.adtech.de\/?adrawdata\/3.0\/606.1\/3320485\/0\/1725\/noperf=1;cc=2;header=yes;alias=myalias;cookie=yes;cookie=info;adct=204;key=key1+key2;grp=[group];misc=[TIMESTAMP]"},"playlist":[{"playerID":1763083646001,"playerKey":"AQ~~,AAAACbuW-Dk~,jONqRziDCugM61nng7gUkSBLrs2oVeK-","@videoPlayer":1085351723001}],"elementId":"brightcoveExperience-345"},"views":{"ajax_path":["\/views\/ajax","\/views\/ajax"],"ajaxViews":[{"view_name":"related_content","view_display_id":"panel_pane_1","view_args":"345\/video\/29\/0","view_path":"node\/345","view_base_path":null,"view_dom_id":1,"pager_element":0},{"view_name":"related_content","view_display_id":"panel_pane_1","view_args":"345\/video\/29\/0","view_path":"node\/345","view_base_path":null,"view_dom_id":1,"pager_element":0}]},"getQ":"node\/345"});
    jQuery.extend(Drupal.settings, {"basePath":"\/","googleanalytics":{"trackOutgoing":1,"trackMailto":1,"trackDownload":1,"trackDownloadExtensions":"7z|aac|arc|arj|asf|asx|avi|bin|csv|doc|exe|flv|gif|gz|gzip|hqx|jar|jpe?g|js|mp(2|3|4|e?g)|mov(ie)?|msi|msp|pdf|phps|png|ppt|qtm?|ra(m|r)?|sea|sit|tar|tgz|torrent|txt|wav|wma|wmv|wpd|xls|xml|z|zip"},"brightcovePlayer":{"params":{"bgcolor":"3a6ea5","width":"600","height":"356","isVid":"true","isUI":"true","dynamicStreaming":"true","autoStart":"true","wmode":"transparent","templateLoadHandler":"turnerOnTemplateLoaded","templateReadyHandler":"turnerOnTemplateReady","templateErrorHandler":"turnerOnTemplateError","externalAds":"true","adServerURL":"http:\/\/adserver.adtech.de\/?adrawdata\/3.0\/606.1\/3320485\/0\/1725\/noperf=1;cc=2;header=yes;alias=myalias;cookie=yes;cookie=info;adct=204;key=key1+key2;grp=[group];misc=[TIMESTAMP]"},"playlist":[{"playerID":1763083646001,"playerKey":"AQ~~,AAAACbuW-Dk~,jONqRziDCugM61nng7gUkSBLrs2oVeK-","@videoPlayer":1085351724001}],"elementId":"brightcoveExperience-346"},"views":{"ajax_path":["\/views\/ajax","\/views\/ajax"],"ajaxViews":[{"view_name":"related_content","view_display_id":"panel_pane_1","view_args":"346\/video\/29\/0","view_path":"node\/346","view_base_path":null,"view_dom_id":1,"pager_element":0},{"view_name":"related_content","view_display_id":"panel_pane_1","view_args":"346\/video\/29\/0","view_path":"node\/346","view_base_path":null,"view_dom_id":1,"pager_element":0}]},"getQ":"node\/346"});
    '''
    
    player_id = scrapertools.get_match(data,'"playerID"\:(\d+)')
    logger.info("player_id="+player_id)
    
    player_key = scrapertools.get_match(data,'"playerKey"\:"([^"]+)"')
    logger.info("player_key="+player_key)
    
    #element_id = scrapertools.get_match(data,'"elementId"\:"brightcoveExperience-(\d+)"')
    #logger.info("element_id="+element_id)
    
    video_player = scrapertools.get_match(data,'"@videoPlayer"\:(\d+)')
    logger.info("video_player="+video_player)
    
    
    response = get_rtmp( player_key , video_player , page_url , player_id)

    string_response = str(response)
    url = scrapertools.get_match(string_response,"'FLVFullLengthURL'\: u'([^']+)'")
    logger.info("url="+url)

    video_urls = []
    video_urls.append( [ "MP4 [cartoonito]" , url ] )

    for video_url in video_urls:
        logger.info("[cartoonito.py] %s - %s" % (video_url[0],video_url[1]))

    return video_urls

def get_rtmp(key, content_id, url, exp_id):
   conn = httplib.HTTPConnection("c.brightcove.com")
   envelope = build_amf_request(key, content_id, url, exp_id)
   logger.info("REQUEST="+str(envelope))
   encoded = remoting.encode(envelope)
   logger.info("encoded="+str(encoded))
   stringenvelope=str(encoded.read())
   logger.info("stringenvelope="+stringenvelope)
   conn.request("POST", "/services/messagebroker/amf?playerKey="+key, stringenvelope,{'content-type': 'application/x-amf'})
   response = conn.getresponse().read()
   logger.info("RESPONSE="+str(response))
   response = remoting.decode(response).bodies[0][1].body
   logger.info("RESPONSE="+str(response))
   return response

class ViewerExperienceRequest(object):
   def __init__(self, URL, contentOverrides, experienceId, playerKey, TTLToken=''):
      self.TTLToken = TTLToken
      self.URL = URL
      self.deliveryType = float(0)
      self.contentOverrides = contentOverrides
      self.experienceId = experienceId
      self.playerKey = playerKey

class ContentOverride(object):
   def __init__(self, contentId, contentType=0, target='videoPlayer'):
      self.contentType = contentType
      self.contentId = contentId
      self.target = target
      self.contentIds = None
      self.contentRefId = None
      self.contentRefIds = None
      self.contentType = 0
      self.featureId = float(0)
      self.featuredRefId = None

def build_amf_request(key, content_id, url, exp_id):
   print 'ContentId:'+content_id
   print 'ExperienceId:'+exp_id
   print 'URL:'+url

   const = '40421d54b4cdb3e933cb99efe6c41f9ef5acff82'
   pyamf.register_class(ViewerExperienceRequest, 'com.brightcove.experience.ViewerExperienceRequest')
   pyamf.register_class(ContentOverride, 'com.brightcove.experience.ContentOverride')
   content_override = ContentOverride(int(content_id))
   viewer_exp_req = ViewerExperienceRequest(url, [content_override], int(exp_id), key)

   env = remoting.Envelope(amfVersion=3)
   env.bodies.append(
      (
         "/1",
         remoting.Request(
            target="com.brightcove.experience.ExperienceRuntimeFacade.getDataForExperience",
            body=[const, viewer_exp_req],
            envelope=env
         )
      )
   )
   return env

# Encuentra vídeos del servidor en el texto pasado
def find_videos(data):
    encontrados = set()
    devuelve = []

    return devuelve
