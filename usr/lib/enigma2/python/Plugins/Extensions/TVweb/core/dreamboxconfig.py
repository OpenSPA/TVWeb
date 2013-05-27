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
    
def open_settings():
    return

def get_setting(name):
	if name=="debug":
		return "true"
	elif name=="megavideopremium":
	    return "false"
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
    import os
    return os.getcwd()

def get_runtime_path():
    import os
    return os.getcwd()
