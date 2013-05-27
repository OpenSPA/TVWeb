# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# Gestión de parámetros de configuración - dreambox
#-------------------------------------------------------------------------------
# tvalacarta
# http://blog.tvalacarta.info/plugin-xbmc/tvalacarta/
#-------------------------------------------------------------------------------
# Creado por: 
# Jesús (tvalacarta@gmail.com)
# Licencia: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
#-------------------------------------------------------------------------------

print "Using DREAMBOX config 3.2"

def get_system_platform():
    return "dreambox"
    
def get_platform():
    return "dreambox"
    
def open_settings():
    return

def get_setting(name, channel=""):
    if name=="debug":
        return "true"
    elif name=="cache.mode":
        return "2"
    elif name=="cache.dir":
        return "/tmp"
    elif name=="cookies.dir":
        return "/tmp"
    elif channel!="":
        import os,re
        nombre_fichero_config_canal = os.path.join( get_data_path() , channel+".xml" )
        if os.path.exists( nombre_fichero_config_canal ):
            config_canal = open( nombre_fichero_config_canal )
            data = config_canal.read()
            config_canal.close();
        
            patron = "<"+name+">([^<]+)</"+name+">"
            matches = re.compile(patron,re.DOTALL).findall(data)
            if len(matches)>0:
                dev = matches[0]
            else:
                dev = ""
        else:
            dev = ""
    
        return dev
    else:
        return ""
def set_setting(name,value):
    return

def get_localized_string(code):
    return ""
    
def get_library_path():
    # Una forma rápida de lanzar un error
    import noexiste
    return ""

def get_temp_file(filename):
    import os
    return os.path.join(get_data_path(),filename)

def get_data_path():
    return "/etc"

def get_runtime_path():
    import os
    return os.getcwd()

def get_cookie_data():
    import os
    ficherocookies = os.path.join( get_data_path(), 'cookies.lwp' )

    cookiedatafile = open(ficherocookies,'r')
    cookiedata = cookiedatafile.read()
    cookiedatafile.close();

    return cookiedata
