# -*- coding: utf-8 -*-                                                                                                                                                        
#------------------------------------------------------------                                                                                                                     
# pelisalacarta - XBMC Plugin                                                                                                                                                     
# libreria para stormtv                                                                                                                                                         
# http://blog.tvalacarta.info/plugin-xbmc/pelisalacarta/                                                                                                                          
#------------------------------------------------------------                                                                                                                     
import urlparse,urllib2,urllib,re
import xml.dom.minidom as minidom                                                                                                                                                 
import urllib                                                                                                                                                                     
import os
from core import config
__server__ = "oc1.lopezepol.com"

SERVER="https://"+__server__+"/stormtv/public/"
PATH=config.get_data_path()+"stormtv/temp/"
def mkdir_p(path):       
    try:                     
      os.makedirs(path)
    except OSError as exc: # Python >2.5                             
           if exc.errno == errno.EEXIST and os.path.isdir(path):
              pass                                                              
           else: raise 

def getpreferences():
    print "[stormlib.py] getpreferences "                     
    user_id=config.get_setting("stormtvuser")                                   
    user_pass=config.get_setting("stormtvpassword")                             
    #server= "https://"+__server__+"/stormtv_v2/public/"                             
    #path=config.get_data_path()+"stormtv_v2/temp/"
    if not os.path.exists(PATH):                                                
       print "Creating data_path "+PATH                                         
       try:                                                                     
         mkdir_p(PATH)                                                       
       except:                                                                  
         pass
    urllib.urlretrieve (SERVER+"followers/preferences/user/"+user_id+"/pass/"+user_pass, PATH+"preferences.xml")
    #comprobar si hay error de usuario
    xml=PATH+"preferences.xml"
    if not os.path.exists(xml):                                                                                         
       status="1"                                                                                                     
       print "[stormlib.py] getpreferences "+status  
    else: 
	doc = minidom.parse(xml)                                                                                            
	node = doc.documentElement                                                                                          
	error = doc.getElementsByTagName("error")                                                                         
	if (len(error)>0):
		status="1"                                                                                                                  
		print "[stormlib.py] getpreferences "+status
	else:
		status="0"                                                                                                                  
		print "[stormlib.py] getpreferences "+status     	
    return status   
def addfollow(tvs_id):
    print "[stormlib.py] addfollow "+config.get_data_path()
    user_id=config.get_setting("stormtvuser")
    user_pass=config.get_setting("stormtvpassword")
    #server= "https://"+__server__+"/stormtv_v2/public/"
    #path=config.get_data_path()+"stormtv/temp/"                                
    urllib.urlretrieve (SERVER+"tvseries/addfollow/user/"+user_id+"/pass/"+user_pass+"/tvs/"+tvs_id, PATH+"temp.xml")
    print "[stormlib.py] addfollow"

def removefollow(tvs_id):
    user_id=config.get_setting("stormtvuser")
    user_pass=config.get_setting("stormtvpassword")
    #server= "https://"+__server__+"/stormtv/public/"
    #path=config.get_data_path()+"stormtv/temp/"
    urllib.urlretrieve (SERVER+"tvseries/removefollow/user/"+user_id+"/pass/"+user_pass+"/tvs/"+tvs_id, PATH+"temp.xml")
    print "[stormlib.py] Remove follow"

def iswatched(title,chap_dictionary):
    patronchap="([0-9](x|X)[0-9]*)"                                                                                                                                                 
    matcheschap= re.compile(patronchap,re.DOTALL).findall(title)                                                                                                              
    if (len(matcheschap)>0):
    	print matcheschap[0][0]                                                                                                                                                     
    	if (matcheschap[0][0].lower() in chap_dictionary):                                                                                                                                   
       		status=chap_dictionary[matcheschap[0][0].lower()].encode("utf-8")                                                                                                                    
       		#print status                                                                                                                                                      
       		title=title+" ["+status+"]"                                                                                                                                               
       		#print chap_dictionary[matcheschap[0]]+"#"
    return title, matcheschap[0][0].lower()

def getwatched(tvs_id):
    print "[stormlib.py] getwatched"+tvs_id
    user_id=config.get_setting("stormtvuser")
    user_pass=config.get_setting("stormtvpassword")
    chap_dictionary = {}                                                                                                                                                          
    #server= "https://"+__server__+"/stormtv/public/"                                                                                                                               
    #path=config.get_data_path()+"stormtv/temp/"                                                                                            
    urllib.urlretrieve (SERVER+"chapters/getstatus/user/"+user_id+"/pass/"+user_pass+"/tvs/"+tvs_id, PATH+"temp.xml")                                                              
    xml=PATH+"/"+"temp.xml"                                                                                                                                                       
    doc = minidom.parse(xml)                                                                                                                                                      
    node = doc.documentElement                                                                                                                                                    
    chapters = doc.getElementsByTagName("chapter")                                                                                                                                
    for chapter in chapters:                                                                                                                                                      
        number = chapter.getElementsByTagName("number")[0].childNodes[0].data                                                                                                 
        status = chapter.getElementsByTagName("status")[0].childNodes[0].data                                                                                                 
        chap_dictionary[number]=status                                                                                                                                        
        print number+chap_dictionary[number]+"#"
    return chap_dictionary

def getlang():
    print "[stormlib.py] getlang"
    #path=config.get_data_path()+"stormtv/temp/"
    xml=PATH+"/"+"preferences.xml"
    if not os.path.exists(xml):                                                                                         
        status="0"                                                                                                      
    else:                                                                                              
    	doc = minidom.parse(xml)                                                                                            
    	node = doc.documentElement
    	error = doc.getElementsByTagName("error")                                                                                  
    	if (len(error)>0):
    		status="0"                                                                                                         
    	else:                                                                                                                      
    		lang = doc.getElementsByTagName("Lang") 
    		status = lang[0].childNodes[0].data                                                                     
    print "[stormlib.py] getlang"+status
    return status  

def getservers():
    print "[stormlib.py] getlang"                                                                                                   
    #path=config.get_data_path()+"stormtv/temp/"                                                                                     
    xml=PATH+"/"+"preferences.xml"
    if not os.path.exists(xml):
    	status="0"
    else:                                                                                                          
    	doc = minidom.parse(xml)                                                                                                        
    	node = doc.documentElement
    	error = doc.getElementsByTagName("error")                                                                                  
    	if (len(error)>0):                                                                                                         
    	       	status="0"                                                                                                         
        else:                                                                                                      
    		servers = doc.getElementsByTagName("Servers")                                                                                         
    		status = servers[0].childNodes[0].data                                                                                             
    print "[stormlib.py] getservers"+status
    return status

def setwatched (tvs_id,chap_number):
    print"[stormlib.py] setwatched"+tvs_id+" "+chap_number
    user_id=config.get_setting("stormtvuser")
    user_pass=config.get_setting("stormtvpassword")
    #server= "https://"+__server__+"/stormtv/public/"                                                                                                                               
    #path=config.get_data_path()+"stormtv/temp/"
    print"[stormlib.py] setwatched "+SERVER+"chapters/add/tvs/"+tvs_id+"/user/"+user_id+"/pass/"+user_pass+"/chap/"+chap_number
    urllib.urlretrieve (SERVER+"chapters/add/tvs/"+tvs_id+"/user/"+user_id+"/pass/"+user_pass+"/chap/"+chap_number, PATH+"temp.xml")                                          
    
    
def isfollow (tvs_id):
    print "[stormlib.py] isfollow"+ tvs_id
    user_id=config.get_setting("stormtvuser")                                                                                                   
    user_pass=config.get_setting("stormtvpassword")
    #server= "https://"+__server__+"/stormtv/public/"
    # Create data_path if not exists
    #path=config.get_data_path()+"stormtv/temp/"                                
    if not os.path.exists(PATH):                         
       print "Creating data_path "+PATH                                                             
       try:                                                        
           os.mkdir(PATH)                               
       except:                                            
           pass                                                                                                                                
    urllib.urlretrieve (SERVER+"tvseries/isfollow/user/"+user_id+"/pass/"+user_pass+"/tvs/"+tvs_id, PATH+"temp.xml")
    xml=PATH+"/"+"temp.xml"                                                                                                                        
    doc = minidom.parse(xml)                                                                                                                       
    node = doc.documentElement                                                                                                                 
    follow = doc.getElementsByTagName("follow")
    status = follow[0].childNodes[0].data
    print status
    return status

def audio_serieonline(title):
    print "[stormlib.py]audio_serionline "+title
    patron_vo="(audio Inglés, subtitulos no)"
    patron_vos="(audio Versión Original (V.O), subtitulos Español)"
    patron_vos2="(audio Inglés, subtitulos Español)"
    patron_spa="(audio Español, subtitulos no)"
    '''
    matches_vos = re.compile(patron_vos,re.DOTALL).findall(title)
    matches_vo = re.compile(patron_vo,re.DOTALL).findall(title)
    matches_spa = re.compile(patron_spa,re.DOTALL).findall(title)
    '''
    n_title=title.replace(patron_vo,"(VO)")
    n_title=n_title.replace(patron_vos,"(VOS)")
    n_title=n_title.replace(patron_vos2,"(VOS)")
    n_title=n_title.replace(patron_spa,"(EspaÃ±ol)")
    return n_title

def audio_seriesyonkis(title):
	print "[stormlib.py]audio_seriesyonkis "+title
    	patron_vo="[Audio:eng Subs:no]"           
        patron_vos="[Audio:eng Subs:eng]"
        patron_vos2="[Audio:eng Subs:spa]"
        patron_spa="[Audio:spa Subs:no]"
        '''      
        matches_vos = re.compile(patron_vos,re.DOTALL).findall(title)
        matches_vo = re.compile(patron_vo,re.DOTALL).findall(title)
        matches_spa = re.compile(patron_spa,re.DOTALL).findall(title)
        '''
        n_title=title.replace(patron_vo,"(VO)")
        n_title=n_title.replace(patron_vos,"(VOS)")
        n_title=n_title.replace(patron_vos2,"(VOS)")
        n_title=n_title.replace(patron_spa,"(EspaÃ±ol)")
        return n_title
    
