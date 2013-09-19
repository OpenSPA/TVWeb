#------------------------------------------------------------
# tvalacarta launcher for dreambox adapted for Spaze Team & called TVweb (www.azboxhd.es)
# http://blog.tvalacarta.info/plugin-xbmc/TVweb/
#------------------------------------------------------------
# Based on Multi-Mediathek Plugin for Enigma2 Dreamboxes

from Components.config import config, configfile, getConfigListEntry, ConfigSubsection, ConfigYesNo, ConfigText, ConfigEnableDisable, ConfigSelection, NoSave, ConfigInteger
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.AVSwitch import AVSwitch
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Network import iNetwork
from Components.PluginComponent import plugins
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Slider import Slider
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Task import Task, Job, job_manager as JobManager, Condition
from Components.MenuList import MenuList
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBar import MoviePlayer
from Screens.InputBox import PinInput
from Screens.Standby import TryQuitMainloop
from Screens.TaskView import JobView
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Tools import Notifications, ASCIItranslit
from Tools.Directories import fileExists
from Tools.LoadPixmap import LoadPixmap
from Tools.BoundFunction import boundFunction
from Plugins.Plugin import PluginDescriptor
from ServiceReference import ServiceReference

from enigma import gFont, ePicLoad, eTimer, getDesktop, eConsoleAppContainer, eBackgroundFileEraser, eServiceReference, iServiceInformation, iPlayableService, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_HALIGN_BLOCK
from os import stat as os_stat, listdir as os_listdir, path as os_path, readlink as os_readlink, system as os_system, remove as os_remove
from time import time
from twisted.web.client import getPage, downloadPage
from urllib import urlencode, unquote, quote_plus, quote
from urllib2 import Request, urlopen
from xml.dom.minidom import parse, parseString
from xml.sax.saxutils import unescape
from core.item import Item

import xml.etree.cElementTree


try:
    from Plugins.Extensions.VlcPlayer.VlcPlayer import VlcPlayer
    from Plugins.Extensions.VlcPlayer.VlcServerConfig import vlcServerConfig
    from Tools.BoundFunction import boundFunction
    VLCSUPPORT = True
except Exception, e:
    VLCSUPPORT = False

##############################
#####  CONFIG SETTINGS   #####
##############################

config.plugins.TVweb = ConfigSubsection()
config.plugins.TVweb.storagepath = ConfigText(default="/media/hdd", fixed_size=False)
config.plugins.TVweb.imagecache = ConfigEnableDisable(default=True)
#config.plugins.TVweb.imagescaling = ConfigSelection(default="1", choices = [("0", _("simple")), ("1", _("better"))])
#config.plugins.TVweb.imagescaler = ConfigSelection(default="0", choices = [("0", _("decodePic()")), ("1", _("getThumbnail()"))])
config.plugins.TVweb.showadultcontent = ConfigYesNo(default=False)
config.plugins.TVweb.showsecretcontent = ConfigYesNo(default=False)
config.plugins.TVweb.downloadimages = ConfigYesNo(default=True)
config.plugins.TVweb.version = NoSave(ConfigText(default="1.0.9"))
config.plugins.TVweb.resolution = ConfigSelection(default="360p", choices = ["240p", "360p", "480p", "720p", "1080p"])
config.plugins.TVweb.freemem = ConfigInteger(default=10, limits=(1, 60))

default = config.plugins.TVweb.storagepath.value + "/TVweb/movies"
tmp = config.movielist.videodirs.value
if default not in tmp:
    tmp.append(default)
config.plugins.TVweb.moviedir = ConfigSelection(default=default, choices=tmp)


##############################################

from Components.Language import language
from os import environ
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
import gettext

lang = language.getLanguage()
environ["LANGUAGE"] = lang[:2]
gettext.bindtextdomain("enigma2", resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain("enigma2")
gettext.bindtextdomain("TVweb", "%s%s" % (resolveFilename(SCOPE_PLUGINS), "Extensions/TVweb/locale/"))

def _(txt):
	t = gettext.dgettext("TVweb", txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t

#############

def setResumePoint(session):
	global resumePointCacheLast, resumePointCache
	service = session.nav.getCurrentService()
	ref = session.nav.getCurrentlyPlayingServiceReference()
	if (service is not None) and (ref is not None): # and (ref.type != 1):
		# ref type 1 has its own memory...
		seek = service.seek()
		if seek:
			pos = seek.getPlayPosition()
			if not pos[0]:
				#key = ref.toString()
				key = service.info().getName()
				lru = int(time())
				l = seek.getLength()
				if l:
					l = l[1]
				else:
					l = None
				resumePointCache[key] = [lru, pos[1], l]
				if len(resumePointCache) > 50:
					candidate = key
					for k,v in resumePointCache.items():
						if v[0] < lru:
							candidate = k
					del resumePointCache[candidate]
				#if lru - resumePointCacheLast > 3600:
				saveResumePoints(session)


def getResumePoint(session):
	global resumePointCache
	resumePointCache = loadResumePoints(session)
	service = session.nav.getCurrentService()
	ref = session.nav.getCurrentlyPlayingServiceReference()
	open("/tmp/prueba","w").write(str(resumePointCache))
	#ref = session.nav.getCurrentlyPlayingServiceReference()
	if (ref is not None) and (ref.type != 1):
		try:
			#entry = resumePointCache[ref.toString()]
			entry = resumePointCache[service.info().getName()]
			entry[0] = int(time()) # update LRU timestamp
			return entry[1]
		except KeyError:
			return None

def saveResumePoints(session):
	global resumePointCacheLast, resumePointCache
	service = session.nav.getCurrentService()
	name = str(config.plugins.TVweb.storagepath.value)+"/TVweb/"+ASCIItranslit.legacyEncode(service.info().getName())+".cue"
	import cPickle
	try:
		f = open(name, 'wb')
		cPickle.dump(resumePointCache, f, cPickle.HIGHEST_PROTOCOL)
	except Exception, ex:
		print "[InfoBar] Failed to write resumepoints:", ex
	resumePointCacheLast = int(time())

def loadResumePoints(session):
	service = session.nav.getCurrentService()
	name = str(config.plugins.TVweb.storagepath.value)+"/TVweb/"+ASCIItranslit.legacyEncode(service.info().getName())+".cue"
	import cPickle
	try:
		return cPickle.load(open(name, 'rb'))
	except Exception, ex:
		print "[InfoBar] Failed to load resumepoints:", ex
		return {}

resumePointCache = {}
resumePointCacheLast = int(time())


def limpia_texto(s):
    if not s:
        return ''
    from core.downloadtools import entitydefs
    for key, value in entitydefs.iteritems():
        s = s.replace("&"+key+";", value)
    return s;



#################################
###    Download Movie Task    ###
#################################

class downloadJob(Job):
    def __init__(self, toolbox, cmdline, filename, filetitle):
        print "[TVweb] downloadJob.__init__"
        Job.__init__(self, _("Download Movie"))
        self.filename = filename
        self.toolbox = toolbox
        self.retrycount = 0
        downloadTask(self, cmdline, filename, filetitle)

    def retry(self):
        assert self.status == self.FAILED
        self.retrycount += 1
        self.restart()

    def cancel(self):
        self.abort()
        os_system("rm -f %s" % self.filename)
        
class downloadTask(Task):
    ERROR_CORRUPT_FILE, ERROR_RTMP_ReadPacket, ERROR_SEGFAULT, ERROR_SERVER, ERROR_UNKNOWN = range(5)
    def __init__(self, job, cmdline, filename, filetitle):
        print "[TVweb] downloadTask.__init__"
        Task.__init__(self, job, filetitle)
        self.postconditions.append(downloadTaskPostcondition())
        self.setCmdline(cmdline)
        self.filename = filename
        self.toolbox = job.toolbox
        self.error = None
        self.lasterrormsg = None
	self.progress = 0
	self.tfreemem = eTimer()
        self.tfreemem.callback.append(self.freemem)
        self.tfreemem.start(60000 * config.plugins.TVweb.freemem.value, False)   #libera memoria
        
    def freemem(self):
        os_system("echo 1 > /proc/sys/vm/drop_caches")
	

    def processOutput(self, data):
        try:
            if data.endswith('%)'):
                startpos = data.rfind("sec (")+5
                if startpos and startpos != -1:
                    self.progress = int(float(data[startpos:-4]))
            elif data.find('%') != -1:
                tmpvalue = data[:data.find("%")]
                tmpvalue = tmpvalue[tmpvalue.rfind(" "):].strip()
                tmpvalue = tmpvalue[tmpvalue.rfind("(")+1:].strip()
                self.progress = int(float(tmpvalue))
            else:
                Task.processOutput(self, data)
        except Exception, errormsg:
            print "Error processOutput: " + str(errormsg)
            Task.processOutput(self, data)

    def processOutputLine(self, line):
        line = line[:-1]
        #print "[DownloadTask STATUS MSG] %s" % line
        self.lasterrormsg = line
        if line.startswith("ERROR:"):
            if line.find("RTMP_ReadPacket") != -1:
                self.error = self.ERROR_RTMP_ReadPacket
            elif line.find("corrupt file!") != -1:
                self.error = self.ERROR_CORRUPT_FILE
                os_system("rm -f %s" % self.filename)
            else:
                self.error = self.ERROR_UNKNOWN
        elif line.startswith("wget:"):
            if line.find("server returned error") != -1:
                self.error = self.ERROR_SERVER
        elif line.find("Segmentation fault") != -1:
            self.error = self.ERROR_SEGFAULT
            
    def afterRun(self):
	self.tfreemem.stop()
	self.freemem()
        #FIXME: Only show when we saved movie in background!
        #if self.getProgress() == 0 or self.getProgress() == 100:
        #    Notifications.AddNotification(MessageBox, _("Movie successfully transfered to your HDD!") +"\n"+self.filename, MessageBox.TYPE_INFO, timeout=10)

class downloadTaskPostcondition(Condition):
    RECOVERABLE = True
    def check(self, task):
        if task.returncode == 0 or task.error is None:
            return True
        else:
            return False

    def getErrorMessage(self, task):
        return {
            task.ERROR_CORRUPT_FILE: _("Video Download Failed!\n\nCorrupted Download File:\n%s" % task.lasterrormsg),
            task.ERROR_RTMP_ReadPacket: _("Video Download Failed!\n\nCould not read RTMP-Packet:\n%s" % task.lasterrormsg),
            task.ERROR_SEGFAULT: _("Video Download Failed!\n\nSegmentation fault:\n%s" % task.lasterrormsg),
            task.ERROR_SERVER: _("Video Download Failed!\n\nServer returned error:\n%s" % task.lasterrormsg),
            task.ERROR_UNKNOWN: _("Video Download Failed!\n\nUnknown Error:\n%s" % task.lasterrormsg)
        }[task.error]

###################################################

class TVwebMoviePlayer(MoviePlayer):
    def __init__(self, session, service, movieinfo=None):
        print "[TVweb] TVwebMoviePlayer.__init__"
        MoviePlayer.__init__(self, session, service)
        self.skinName = "MoviePlayer"
        self.movieinfo = movieinfo
	self.end = False
	self.started = False

        self.__event_tracker = ServiceEventTracker(screen=self, eventmap=
            {
                iPlayableService.evUser+10: self.__evAudioDecodeError,
                iPlayableService.evUser+11: self.__evVideoDecodeError,
                iPlayableService.evUser+12: self.__evPluginError,
		iPlayableService.evEOF: self.__evEOF,
		iPlayableService.evStart: self.__serviceStarted,
		iPlayableService.evBuffering: self.__serviceStarted  #for no evstart event
            })


    def __serviceStarted(self):
	if not self.started:
		self.started = True
		service = self.session.nav.getCurrentService()
		seekable = service.seek()
		name = str(config.plugins.TVweb.storagepath.value)+"/TVweb/"+ASCIItranslit.legacyEncode(service.info().getName())+".cue"
		if not fileExists(name):
			open(name,"w").write("")
		last = getResumePoint(self.session)
		if last is None:
			return
		if seekable is None:
			return # Should not happen?
		length = seekable.getLength() or (None,0)
		print "seekable.getLength() returns:", length
		# Hmm, this implies we don't resume if the length is unknown...
		if (last > 900000) and (not length[1]  or (last < length[1] - 900000)):
			self.resume_point = last
			l = last / 90000
			Notifications.AddNotificationWithCallback(self.playLastCB, MessageBox, _("Do you want to resume this playback?") + "\n" + (_("Resume position at %s") % ("%d:%02d:%02d" % (l/3600, l%3600/60, l%60))), timeout=10)
	#self.end = False


    def playLastCB(self, answer):
	if answer == True:
		service = self.session.nav.getCurrentService()
		seekable = service.seek()
		if seekable is not None:
			seekable.seekTo(self.resume_point)


    def __evEOF(self):
	self.end = True

    def leavePlayer(self):
        print "[TVweb] TVwebMoviePlayer.leavePlayer"
	setResumePoint(self.session)
	list = ((_("Yes"), True), (_("No"), False),)
	self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)

    def leavePlayerOnExit(self, answer = None):
	self.leavePlayer()

    def leavePlayerConfirmed(self, answer):
        print "[TVweb] TVwebMoviePlayer.leavePlayerConfirmed"
	answer = answer and answer[1]
        if answer == True:
           	self.close()
	elif self.end == True:
		self.end = False
		self.setSeekState(self.SEEK_STATE_PLAY)


    def doEofInternal(self, playing):
        print "[TVweb] TVwebMoviePlayer.doEofInternal"
	list = ((_("Yes"), True), (_("No"), False),)
	self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, title=_("Stop playing this movie?"), list = list)

    def showMovies(self):
        print "[TVweb] TVwebMoviePlayer.showMovies"
        pass

    def __evAudioDecodeError(self):
        currPlay = self.session.nav.getCurrentService()
        sTagAudioCodec = currPlay.info().getInfoString(iServiceInformation.sTagAudioCodec)
        print "[__evAudioDecodeError] audio-codec %s can't be decoded by hardware" % (sTagAudioCodec)
        self.session.open(MessageBox, _("This STB can't decode %s streams!") % sTagAudioCodec, type=MessageBox.TYPE_INFO, timeout=20)

    def __evVideoDecodeError(self):
        currPlay = self.session.nav.getCurrentService()
        sTagVideoCodec = currPlay.info().getInfoString(iServiceInformation.sTagVideoCodec)
        print "[__evVideoDecodeError] video-codec %s can't be decoded by hardware" % (sTagVideoCodec)
        self.session.open(MessageBox, _("This STB can't decode %s streams!") % sTagVideoCodec, type=MessageBox.TYPE_INFO, timeout=20)

    def __evPluginError(self):
        currPlay = self.session.nav.getCurrentService()
        message = currPlay.info().getInfoString(iServiceInformation.sUser+12)
        print "[__evPluginError]" , message
        if VLCSUPPORT and self.movieinfo is not None:
            self.session.openWithCallback(self.VLCcallback, MessageBox, _("Your STB can't decode this video stream!\n%s\nDo you want to stream it via VLC Server from your PC?") % message[17:], MessageBox.TYPE_YESNO)
        else:
            self.session.open(MessageBox, _("Your STB can't decode this video stream!\n%s") % message, type=MessageBox.TYPE_INFO, timeout=20)

    def VLCcallback(self, answer):
        if answer is True:
            self.close(self.movieinfo)
        else:
            self.close()

#-----mpiero base skin-------------------------------------------------------------------------------------
if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/logoazmed-fs8.png", 'r'):
	logo = "/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/logoazmed-fs8.png"
else:
	logo = "/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/logo.png"
try:
	from Tools.HardwareInfo import HardwareInfo 
	boxime = HardwareInfo().get_device_name()
	if boxime == "me" or boxime == "minime" or boxime == "elite" or boxime == "premium" or boxime == "premium+" or boxime == "ultra":
		BASEX = '63'
	else:
		BASEX = '53'
except:
	BASEX = '53'

BASESKIN=""" 
		<widget source="session.VideoPicture" render="Pig" position=\""""+BASEX+""",97" size="420,236" backgroundColor="transparent" zPosition="-10" /> 
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/fondo-fs8.png" position="0,0" size="1281,721" zPosition="-4" alphatest="blend" />
		<ePixmap pixmap=\""""+logo+"""\" zPosition="2" position="210,37" size="154,39" alphatest="blend" /> 		
		<widget source="version" transparent="1" render="Label" zPosition="2" valign="center" halign="right" position="100,67" size="100,26" font="Regular; 18" backgroundColor="black" foregroundColor="#00dddefa" noWrap="1" />	   
		<widget source="global.CurrentTime" render="Label" position="989,10" size="251,55" backgroundColor="black" foregroundColor="#00ffffff" transparent="1" zPosition="2" font="Regular;24" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2"> 
		<convert type="ClockToText">Format:%-H:%M</convert> 
		</widget> 
		<widget source="global.CurrentTime" render="Label" position="940,30" size="300,55" backgroundColor="black" foregroundColor="#00ffffff" transparent="1" zPosition="2" font="Regular;16" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2"> 
		<convert type="ClockToText">Date</convert>  
		</widget>  
		<widget source="session.CurrentService" render="Label" position="58,101" size="410,20" font="Regular; 17" transparent="0" valign="center" zPosition="1" backgroundColor="#aa000000" foregroundColor="#00ffffa0" noWrap="1" halign="left" borderColor="black" borderWidth="1">
			  <convert type="ServiceName">Name</convert>
			</widget>

	   <widget source="titlemessage" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="40,665" size="1020,25" font="Regular; 19" foregroundColor="#00777777" backgroundColor="white" noWrap="1" />
		<widget source="titletext" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="582,67" size="551,26" font="Regular; 20" backgroundColor="black" foregroundColor="#00dddefa" noWrap="1" />	   
	   """
# -- mpiero para settings y task ---
BASESKIN2=""" 
		<widget source="session.VideoPicture" render="Pig" position="53,97" size="420,236" backgroundColor="transparent" zPosition="-10" /> 
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/fondo-fs8.png" position="0,0" size="1281,721" zPosition="-4" alphatest="blend" />
		<ePixmap pixmap=\""""+logo+"""\" zPosition="2" position="210,37" size="154,39" alphatest="blend" /> 		
		<widget source="version" transparent="1" render="Label" zPosition="2" valign="center" halign="right" position="100,67" size="100,26" font="Regular; 18" backgroundColor="black" foregroundColor="#00dddefa" noWrap="1" />	   
		<widget source="global.CurrentTime" render="Label" position="989,10" size="251,55" backgroundColor="black" foregroundColor="#00ffffff" transparent="1" zPosition="2" font="Regular;24" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2"> 
		<convert type="ClockToText">Format:%-H:%M</convert> 
		</widget> 
		<widget source="global.CurrentTime" render="Label" position="940,30" size="300,55" backgroundColor="black" foregroundColor="#00ffffff" transparent="1" zPosition="2" font="Regular;16" valign="center" halign="right" shadowColor="#000000" shadowOffset="-2,-2"> 
		<convert type="ClockToText">Date</convert>  
		</widget>  
		<widget source="session.CurrentService" render="Label" position="58,101" size="410,20" font="Regular; 17" transparent="0" valign="center" zPosition="1" backgroundColor="#aa000000" foregroundColor="#00ffffa0" noWrap="1" halign="left" borderColor="black" borderWidth="1">
			  <convert type="ServiceName">Name</convert>
			</widget>
		<widget source="Title" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="582,67" size="551,26" font="Regular; 20" backgroundColor="black" foregroundColor="#00dddefa" noWrap="1" />	   
	   """
class TVweb(Screen):
    def __init__(self, session, feedurl="http://www.dreambox-plugins.de/feeds/mediathek/main.xml", feedtitle="Secciones", feedtext="", extra=""):
        print "[TVweb] __init__ (feedurl="+feedurl+")"
        size_w = 1280
        size_h = 720


        if True:
            self.spaceTop = 100
	    self.spaceBottom = 60
            self.spaceLeft = 577
            self.spaceX = 20
            self.spaceY = 12
            self.picX = 240
            self.picY = 120








        # Workaround for UserAgent Settings when MediaPlayer not installed
        try:
            config.mediaplayer.useAlternateUserAgent.value = False
            config.mediaplayer.alternateUserAgent.value = ""
        except Exception, errormsg:
            config.mediaplayer = ConfigSubsection()
            config.mediaplayer.useAlternateUserAgent = ConfigYesNo(default=False)
            config.mediaplayer.alternateUserAgent = ConfigText(default="")

        # Set some default values
        self["titletext"] = StaticText(feedtitle)
        self["titlemessage"] = StaticText(feedtext)
        self["version"] = StaticText(config.plugins.TVweb.version.value)

        self.feedurl = feedurl
        self.feedtitle = feedtitle
        self.feedtext = feedtext
	self.extra = extra
        self.textcolor = "#00000000"
        self.bgcolor = "#00ffffff"
        self.textsize = 20

        # Create Thumblist
        self.thumbsX = (size_w - self.spaceLeft) / (self.spaceX + self.picX) # thumbnails in X
        self.thumbsY = (size_h - self.spaceTop - self.spaceBottom) / (self.spaceY + self.picY) # thumbnails in Y
        self.thumbsC = self.thumbsX * self.thumbsY # all thumbnails

        self.positionlist = []
        skincontent = ""

        posX = -1
        #print "self.thumbsC=%s" % self.thumbsC
        for x in range(self.thumbsC):
            posY = x / self.thumbsX
            posX += 1
            if posX >= self.thumbsX:
                posX = 0

            absX = self.spaceLeft + self.spaceX + (posX*(self.spaceX + self.picX))
            absY = self.spaceTop + self.spaceY + (posY*(self.spaceY + self.picY))
            self.positionlist.append((absX, absY))
            skincontent += "<widget source=\"label" + str(x) + "\" render=\"Label\" position=\"" + str(absX+2) + "," + str(absY+self.picY-self.textsize-10 ) + "\" size=\"" + str(self.picX - 10) + ","  + str((self.textsize)+7) + "\" halign=\"center\" font=\"Regular;" + str(self.textsize) + "\" zPosition=\"5\" transparent=\"1\" backgroundColor=\"#00ffffff\" foregroundColor=\"" + self.textcolor + "\" />"
            skincontent += "<widget name=\"thumb" + str(x) + "\" position=\"" + str(absX)+ "," + str(absY+5) + "\" size=\"" + str(self.picX -5) + "," + str(self.picY - (self.textsize*2)) + "\" zPosition=\"4\" transparent=\"1\" alphatest=\"blend\" />"

        # Screen, backgroundlabel and MovingPixmap
        self.skin = "<screen position=\"0,0\" size=\"" + str(size_w) + "," + str(size_h) + "\" flags=\"wfNoBorder\" title=\"TVweb\"> "+BASESKIN+" \
            <widget name=\"up\"    position=\"828,73\"   zPosition=\"6\" size=\"33,20\" pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/Up.png\" transparent=\"1\" alphatest=\"blend\" /> \
            <widget name=\"down\"    position=\"828,663\"   zPosition=\"6\" size=\"33,20\" pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/Down.png\" transparent=\"1\" alphatest=\"blend\" /> \
            <widget name=\"key_blue\" position=\""+ str(size_w-225+60) +",665\" zPosition=\"3\" size=\"140,24\" font=\"Regular;19\" halign=\"left\" backgroundColor=\"#1f771f\" transparent=\"1\" foregroundColor=\"#00000000\" /> \
            <ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/blue.png\" zPosition=\"2\" position=\""+ str(size_w-200) +",665\" size=\"140,24\" alphatest=\"blend\" /> \
			<ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/linea-fs8.png\" zPosition=\"2\" position=\"574,243\" size=\"551,2\" alphatest=\"blend\" /> \
			<ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/linea-fs8.png\" zPosition=\"2\" position=\"574,373\" size=\"551,2\" alphatest=\"blend\" /> \
			<ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/linea-fs8.png\" zPosition=\"2\" position=\"574,507\" size=\"551,2\" alphatest=\"blend\" /> \
			<ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/lineav-fs8.png\" zPosition=\"2\" position=\"849,100\" size=\"2,555\" alphatest=\"blend\" /> \
			<ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/logospzfs8.png\" zPosition=\"2\" position=\"172,428\" size=\"179,78\" alphatest=\"blend\" /> \
            <widget name=\"frame\" position=\"" + str(size_w) + "," + str(size_h) + "\" size=\"" + str(self.picX - 10) + ","  + str((self.textsize*2)+10) + "\" pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/seleccion.png\" zPosition=\"4\" alphatest=\"blend\" />"  + skincontent + "</screen>"

        Screen.__init__(self, session)

        self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MovieSelectionActions"],
        {
            "cancel": self.Exit,
            "ok": self.key_ok,
            "left": self.key_left,
            "right": self.key_right,
            "up": self.key_up,
            "down": self.key_down,
            "blue": self.selectBookmark,
            "contextMenu": self.key_menu,
        }, -1)

        self.maxPage = 0
        self.maxentry = 1
        self.index = 0
        self.itemlist = False

        self["frame"] = MovingPixmap()
        for x in range(self.thumbsC):
            self["label"+str(x)] = StaticText()
            self["thumb"+str(x)] = Pixmap()

	self["up"] = Pixmap()
	self["down"] = Pixmap()
        self["down"].hide()
	self["up"].hide()
        self["key_blue"] = Button(_("Bookmarks"))

        # Get FrameBuffer Scale for ePicLoad()
        sc = AVSwitch().getFramebufferScale()
        
        # Init Thumb PicLoad
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.showThumbPixmap)
        self.picload.setPara((self.picX-10, self.picY-(self.textsize*2), sc[0], sc[1], 0, 1, "#00e0e0e0"))

        # Init eBackgroundFileEraser
        self.BgFileEraser = eBackgroundFileEraser.getInstance()

        # Check if plugin-update is available
        if self.feedtitle == "Startseite":
            self.onLayoutFinish.append(self.checkforupdate)

        self.onFirstExecBegin.append(self.loadFrame)

    def loadFrame(self):
        print "[TVweb] loadFrame"
        if self.feedtitle == "Secciones":
            if not self.createMediaFolders():
                return

        if self.feedtitle == _("Bookmarks"):
            self.getBookmarks()
        elif self.feedurl.startswith("TVweb"):
            self.getTVwebitems()
        else:
            self.getxmlfeed()

    def createMediaFolders(self):
        print "[TVweb] createMediaFolders"
        # Check if cache folder is on a mountable device and not inside flash-memory
        tmppath = config.plugins.TVweb.storagepath.value
        if tmppath != "/tmp" and tmppath != "/media/ba":
            if os_path.islink(tmppath):
                tmppath = os_readlink(tmppath)
            loopcount = 0
            while not os_path.ismount(tmppath):
                loopcount += 1
                tmppath = os_path.dirname(tmppath)
                if tmppath == "/" or tmppath == "" or loopcount > 50:
                    print "[TVweb] Error: Can not create cache-folders inside flash memory. Check your Cache-Folder Settings!"
                    return False

        # Create Cache Folders ...
        os_system("mkdir -p "+config.plugins.TVweb.storagepath.value+"/TVweb")
        os_system("mkdir -p "+config.plugins.TVweb.storagepath.value+"/TVweb/images")
        os_system("mkdir -p "+config.plugins.TVweb.storagepath.value+"/TVweb/movies")
        os_system("mkdir -p "+config.plugins.TVweb.storagepath.value+"/TVweb/tmp")

        # Check if Cache Folders were created successfully
        if not os_path.exists(config.plugins.TVweb.storagepath.value+"/TVweb"):
            print "[TVweb] Error: No write permission to create cache-folders. Check your Cache-Folder Settings!"
            return False
        else:
            return True

    def checkforupdate(self):
        try:
            getPage("http://www.dreambox-plugins.de/downloads/MultiMediathek/version.txt").addCallback(self.gotUpdateInfo).addErrback(self.getxmlfeedError)
        except Exception, error:
            print "[TVweb]: Could not download HTTP Page\n" + str(error)

    def gotUpdateInfo(self, html):
        tmp_infolines = html.splitlines()
        remoteversion = tmp_infolines[0]
        self.updateurl = tmp_infolines[1]
        '''
        FIXME: Desactivada actualizacion automatica
        if config.plugins.TVweb.version.value < remoteversion:
            self.session.openWithCallback(self.startPluginUpdate,MessageBox,_("An update is available for Mediathek Plugin!\nDo you want to download and install now?"), MessageBox.TYPE_YESNO)
        '''

    def startPluginUpdate(self, answer):
        if answer is True:
            self.container=eConsoleAppContainer()
            self.container.appClosed.append(self.finishedPluginUpdate)
            self.container.execute("opkg install --force-overwrite " + str(self.updateurl))

    def finishedPluginUpdate(self,retval):
        self.session.openWithCallback(self.restartGUI, MessageBox,_("TVweb plugin successfully updated!\nDo you want to restart GUI now?"), MessageBox.TYPE_YESNO)

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)

    def getxmlfeed(self):
        print "[TVweb] getxmlfeed"
        feedurl = self.feedurl
        if self.feedtitle == "Startseite" and (config.plugins.TVweb.showadultcontent.value == True or config.plugins.TVweb.showsecretcontent.value == True):
            feedurl = feedurl + "?"
            if config.plugins.TVweb.showadultcontent.value:
                feedurl = feedurl + "&showadult=1"
            if config.plugins.TVweb.showsecretcontent.value:
                feedurl = feedurl + "&showsecret=1"
        
        '''
        if '-->' in feedurl:
            # Request to download external page
            tmpurls = feedurl.split("-->")
            getpageurl = unquote(tmpurls[1])
            self.postpageurl = unquote(tmpurls[0])
            getPage(getpageurl, agent="Mozilla/5.0 (Windows; U; MSIE 7.0; Windows NT 6.0; en-US)").addCallback(self.ForwardExternalPage).addErrback(self.getxmlfeedError)
        else:
            getPage(feedurl).addCallback(self.gotxmlfeed).addErrback(self.getxmlfeedError)
        '''
        self.gotxmlfeed("")

    def getTVwebitems(self):
        print "[TVweb] getTVwebitems"
        '''
        from core import config
        print "config done"
        from core import logger
        print "logger done"
        from core import scrapertools
        print "scrapertools done"
        from servers import servertools
        print "servertools done"
        '''

        # Lee el canal
        print "feedtitle="+self.feedtitle
        print "feedurl="+self.feedurl
        print "feedtext="+self.feedtext

        #from channels import seriematic 
        from core.item import Item
        from core import downloadtools
        from servers import servertools
        
        partes = self.feedurl.split("|")
        canal = partes[1]
        print "canal="+canal
        accion = partes[2]
        print "accion="+accion
        urlx = partes[3]
        print "url="+urlx
        serverx = partes[4]
        print "server="+serverx
        item = Item(title=self.feedtitle,url=urlx,channel=canal,action=accion, server=serverx, extra=self.extra)

        if accion=="play":
            try:
                exec "from TVweb.channels import "+canal
                exec "itemlista = "+canal+"."+accion+"(item)"
                item = itemlista[0]
            except:
                pass

            exec "from servers import "+item.server+" as servermodule"
            video_urls = servermodule.get_video_url( item.url )
            
            itemlista = []
            for video_url in video_urls:
                itemvideo = Item(title=video_url[0], url=video_url[1], action="__movieplay")
                itemlista.append(itemvideo)

        elif accion=="findvideos":
            try:
                exec "from TVweb.channels import "+canal
                exec "itemlista = "+canal+"."+accion+"(item)"
                for item in itemlista:
                    item.folder=False
            except:
                from core import scrapertools
                data = scrapertools.cache_page(urlx)

               
                # Busca los enlaces a los videos
                listavideos = servertools.findvideos(data)
                
                itemlista = []
                for video in listavideos:
                    scrapedtitle = item.title.strip() + " - " + video[0]
                    scrapedurl = video[1]
                    server = video[2]

                    itemlista.append( Item(channel=item.channel, title=scrapedtitle , action="play" , server=server, page=item.page, url=scrapedurl, thumbnail=item.thumbnail, show=item.show , plot=item.plot , folder=True) )
        else:
            exec "from TVweb.channels import "+canal
            exec "itemlista = "+canal+"."+accion+"(item)"
            print "%d elementos" % len(itemlista)

        index = 0
        framePos = 0
        Page = 0

        self.Thumbnaillist = []
        self.itemlist = []
        self.currPage = -1
        self.maxPage = 0
        
        for item in itemlista:
            if item.action=="__movieplay":
                print "item __movieplay"
                type = "movie"
                name = item.title
                imgurl = item.thumbnail
                url = item.url
            else:
                print "item normal"
                type = "cat"
		try:
                	name = limpia_texto(item.title)
		except:
			name = item.title
                imgurl = item.thumbnail
                url = "TVweb" + "|" + canal + "|" + item.action + "|" + item.url + "|" + item.server

	    try:
			name = name.decode("utf-8").encode("utf-8")
	    except:
			try:
				name = name.decode("iso-8859-1").encode("utf-8")
			except:
				pass
 
            # APPEND ITEM TO LIST
            self.itemlist.append((index, framePos, Page, name, imgurl, url, type, "item",item.extra))
            index += 1
            framePos += 1

            if framePos == 1:
                self.maxPage += 1
            elif framePos > (self.thumbsC-1):
                framePos = 0
                Page += 1

        self.maxentry = len(self.itemlist)-1

        self.paintFrame()
        self["frame"].show()

        
    def gotxmlfeed(self, page=""):
        print "[TVweb] gotxmlfeed"
        print page

        '''        
        self["pageinfo"].setText("Parsing XML Feeds ...")
        xml = parseString(page)
        '''

        index = 0
        framePos = 0
        Page = 0

        self.Thumbnaillist = []
        self.itemlist = []
	self.listado = []
        self.currPage = -1
        self.maxPage = 0

        # Anade los canales de TVweb
        from core.item import Item
        import channelselector
        if self.feedtitle == "Secciones":
            itemlist = channelselector.getchanneltypes()
        else:
            itemlist = channelselector.channels_list()

        for item in itemlist:
            if item.type=="generic":
                type = "cat"
                if self.feedtitle == "Secciones":
                     url = "canales|"+item.channel+"|mainlist|none|"
                else:
                     url = "TVweb|"+item.channel+"|mainlist|none|"
                name = item.title
                imgurl = "/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/"+item.channel+".png"

		self.listado = itemlist
                # APPEND ITEM TO LIST
                if self.feedtitle == "Secciones":
                     self.itemlist.append((index, framePos, Page, name, imgurl, url, type, "item",item.category))
                elif self.extra in item.category:
                     self.itemlist.append((index, framePos, Page, name, imgurl, url, type, "item",""))
                else:
                     continue
                index += 1
                framePos += 1
    
                if framePos == 1:
                    self.maxPage += 1
                elif framePos > (self.thumbsC-1):
                    framePos = 0
                    Page += 1

        self.maxentry = len(self.itemlist)-1

        self.paintFrame()
        self["frame"].show()

    def getBookmarks(self):

        index = 0
        framePos = 0
        Page = 0

        self.Thumbnaillist = []
        self.itemlist = []
        self.currPage = -1
        self.maxPage = 0

        bookmarkfile = "/etc/enigma2/TVweb.bookmarks"
        if fileExists(bookmarkfile, 'r'):
            bookmarklist = []
            bookmarkcount = 0
            tmpfile = open(bookmarkfile, "r")
            for line in tmpfile:
                if ':::' in line:
                    bookmarkcount += 1
                    tmpline = line.split(":::")
                    id = bookmarkcount
                    type = str(tmpline[0])
                    name = str(tmpline[1])
                    url  = str(tmpline[2])
                    imgurl = str(tmpline[3])

                    # APPEND ITEM TO LIST
                    self.itemlist.append((index, framePos, Page, name, imgurl, url, type, "bookmark",""))
                    index += 1
                    framePos += 1

                    if framePos == 1:
                        self.maxPage += 1
                    elif framePos > (self.thumbsC-1):
                        framePos = 0
                        Page += 1

        self.maxentry = len(self.itemlist)-1

        self.paintFrame()
        self["frame"].show()

    def getThumbnail(self):
        self.thumbcount += 1
        self.thumburl = self.Thumbnaillist[self.thumbcount][2]
	if self.thumburl == "":
		self.thumbfile = "/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/item.png"
	elif self.thumburl[0] == "/":
		self.thumbfile = self.thumburl
	else:
        	self.thumbfile = config.plugins.TVweb.storagepath.value+"/TVweb/images/"+str(self.Thumbnaillist[self.thumbcount][3])
        	if not os_path.exists(config.plugins.TVweb.storagepath.value+"/TVweb/images"):
			self.thumbfile = "/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/item.png"


        if fileExists(self.thumbfile, 'r'):
            self.gotThumbnail()
        else:
            downloadPage(self.thumburl, self.thumbfile, agent="Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.2) Gecko/2008091620 Firefox/3.0.2").addCallback(self.gotThumbnail).addErrback(self.showThumbError)

    def gotThumbnail(self, data=""):
#        if config.plugins.TVweb.imagescaler.value == "0":
        self.picload.startDecode(self.thumbfile)
#        elif self.picload.getThumbnail(self.thumbfile) == 1:
#            if self.thumbcount+1 < len(self.Thumbnaillist):
#                self.getThumbnail()
        
    def showThumbPixmap(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr != None:
            self["thumb" + str(self.thumbcount)].instance.setPixmap(ptr.__deref__())
            self["thumb" + str(self.thumbcount)].show()

        if self.thumbcount+1 < len(self.Thumbnaillist):
            self.getThumbnail()

    def showThumbError(self, error):
        if self.thumbcount+1 < self.thumbsC:
            self.getThumbnail()

    def paintFrame(self):
        if self.maxentry < self.index or self.index < 0 or not self.itemlist:
            return

        pos = self.positionlist[self.itemlist[self.index][1]]
        self["frame"].moveTo(pos[0]+2, pos[1]++self.picY-self.textsize-10, 1)
#        self["frame"].moveTo(pos[0]+30, pos[1]+5, 1)
        self["frame"].startMoving()

        if self.currPage != self.itemlist[self.index][2]:
            self.currPage = self.itemlist[self.index][2]
            self.newPage()

    def newPage(self):
        self.Thumbnaillist = []
#        if self.maxPage > 1:
#            self["pageinfo"].setText("Page "+str(self.currPage+1)+" of "+str(self.maxPage))
#        else:
#            self["pageinfo"].setText("")


	if self.currPage + 1 < self.maxPage:
	    self["down"].show()
	else:
	    self["down"].hide()

	if self.currPage > 0:
	    self["up"].show()
	else:
	    self["up"].hide()
	   

        #clear Labels and Thumbnail
        for x in range(self.thumbsC):
            self["label"+str(x)].setText("")
            self["thumb"+str(x)].hide()

        #paint Labels and fill Thumbnail-List
        for x in self.itemlist:
            print "x="+str(x)
            if x[2] == self.currPage:
                self["label"+str(x[1])].setText(x[3])
#		self.picload.startDecode(str(x[4]))
#        	ptr = self.picload.getData()
#        	if ptr != None:
#            		self["thumb" + str(x[1])].instance.setPixmap(ptr.__deref__())
#                self["thumb"+str(x[1])].instance.setPixmapFromFile(str(x[4]))
#                self["thumb"+str(x[1])].instance.setPixmapFromFile(str(x[4]))
#                self["thumb"+str(x[1])].instance.setPixmapFromFile("/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/item.png")
#               	self["thumb"+str(x[1])].show()
		name = x[3]
		try:
			name = name.decode("utf-8").encode("utf-8")
		except:
			try:
				name = name.decode("iso-8859-1").encode("utf-8")
			except:
				pass
                self.Thumbnaillist.append([0, x[1], x[4], ASCIItranslit.legacyEncode(name+"."+x[4].split('.')[-1]).lower()])
        #Get Thumbnails
        self.thumbcount = -1
        self.getThumbnail()

    def selectBookmark(self):
        self.session.open(TVweb2, self.itemlist[self.index][5], _("Bookmarks"), _("Bookmarks from your favorite Movies"),self.listado[self.index],"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/bookmark.png")

    def key_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_right(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def key_up(self):
        self.index -= self.thumbsX
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_down(self):
        self.index += self.thumbsX
        if self.index-self.thumbsX == self.maxentry:
            self.index = 0
        elif self.index > self.maxentry:
            self.index = self.maxentry
        self.paintFrame()

#    def key_info(self):
#        self.session.open(MessageBox,("Coming soon ..."), MessageBox.TYPE_INFO, timeout=10)

    def key_menu(self):
        if self.feedtitle == "Secciones":
            self.session.openWithCallback(self.loadFrame, TVweb_Settings)
        elif self.itemlist:
            self.session.openWithCallback(self.loadFrame, TVweb_MenuOptions, self.itemlist[self.index], self.listado[self.index])

    def key_ok(self):
        if not self.itemlist:
            return

	if self.feedtitle == "Secciones":
            self.session.open(TVweb, self.itemlist[self.index][5], self.itemlist[self.index][3], self.feedtext + " - " + self.itemlist[self.index][3], self.itemlist[self.index][8])
	else:
            self.session.open(TVweb2, self.itemlist[self.index][5], self.itemlist[self.index][3], self.feedtext + " - " + self.itemlist[self.index][3], self.listado[self.index],self.itemlist[self.index][4])

#        if self.itemlist[self.index][6] == "cat":
#            self.session.open(TVweb, self.itemlist[self.index][5], self.itemlist[self.index][3], self.feedtext + " - " + self.itemlist[self.index][3], self.itemlist[self.index][8])
#        elif self.itemlist[self.index][6] == "movie":
#            self.session.open(MovieInfoScreen, self.itemlist[self.index][5])
#        elif self.itemlist[self.index][6] == "switchpage":
#            self.feedurl = self.itemlist[self.index][5]
#            self.index = 0
#            self.getxmlfeed()
#        elif self.itemlist[self.index][6] == "search":
#            self.searchurl = self.itemlist[self.index][5]
#            self.session.openWithCallback(self.SendSearchQuery, VirtualKeyBoard, title = (_("Enter Search Term:")), text = "")

#    def SendSearchQuery(self, query):
#        if query is not None:
#            searchurl = self.itemlist[self.index][5] + "&searchquery=" + quote_plus(str(query))
#            self.session.open(TVweb, searchurl, self.itemlist[self.index][3], self.feedtext + " - " + self.itemlist[self.index][3] + ": " + query)

    def Exit(self):
        if self.feedtitle == "Secciones":
            # Restart old service
            self.session.nav.playService(self.oldService)

            # Clean TEMP Folder
            if os_path.isdir(config.plugins.TVweb.storagepath.value+"/TVweb/tmp"):
                for filename in os_listdir(config.plugins.TVweb.storagepath.value+"/TVweb/tmp"):
                    filelocation = "%s/TVweb/tmp/%s" % (config.plugins.TVweb.storagepath.value,filename)
                    self.BgFileEraser.erase(filelocation)

            # Clean Image Cache
            if os_path.isdir(config.plugins.TVweb.storagepath.value+"/TVweb/images"):
                for filename in os_listdir(config.plugins.TVweb.storagepath.value+"/TVweb/images"):
                    filelocation = "%s/TVweb/images/%s" % (config.plugins.TVweb.storagepath.value,filename)
		    self.BgFileEraser.erase(filelocation)
                    #statinfo = os_stat(filelocation)
                    #if statinfo.st_mtime < (time()-86400.0):
                    #    self.BgFileEraser.erase(filelocation)

        del self.picload
        self.close()


#------------------------------------------------------------------------------------------

def tvlistEntry(entry):
	print entry
	res = [ (entry[1], entry[0]) ]
	# mpiero checqueo de texto para personalizar icono
	textoparaicono=entry[0].replace("...","").lower()
	name = str(config.plugins.TVweb.storagepath.value)+"/TVweb/"+ASCIItranslit.legacyEncode(entry[0])+".cue"
	if fileExists(name):
		tn="3"
	if textoparaicono=="search" or textoparaicono=="buscar":
		png = LoadPixmap(cached=True, path="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/search.png")
	elif textoparaicono.startswith(">>") or textoparaicono=="next page" or "gina siguiente" in textoparaicono:
		png = None
	elif fileExists(name):
		png = LoadPixmap(cached=True, path="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/checkok.png")
	elif entry[2]:
		if entry[1]:
			png = LoadPixmap(cached=True, path="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/iBookmark.png")
		else:
			png = LoadPixmap(cached=True, path="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/iBookmark_movie2.png")
	elif entry[1]:
		png = LoadPixmap(cached=True, path="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/directory2.png")
	else:
		png = LoadPixmap(cached=True, path="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/movie2.png")
	# mpiero posicion icono
	textoposx=35
	if png is not None:
		# mpiero TYPE_PIXMAP_ALPHABLEND para fundido icono
		res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND, 5, 3, 24, 24, png))
	else:
		textoposx=3
	res.append((eListboxPythonMultiContent.TYPE_TEXT,textoposx,4,640,30,0,RT_HALIGN_LEFT,entry[0]))
	return res 

#------------------------------------------------------------------------------------------

class TVweb2(Screen):
    def __init__(self, session, feedurl="http://www.dreambox-plugins.de/feeds/mediathek/main.xml", feedtitle="Secciones", feedtext="", item=None, img1=None):
        print "[TVweb] __init__ (feedurl="+feedurl+")"
        
        size_w = 1280
        size_h = 720

        # Workaround for UserAgent Settings when MediaPlayer not installed
        try:
            config.mediaplayer.useAlternateUserAgent.value = False
            config.mediaplayer.alternateUserAgent.value = ""
        except Exception, errormsg:
            config.mediaplayer = ConfigSubsection()
            config.mediaplayer.useAlternateUserAgent = ConfigYesNo(default=False)
            config.mediaplayer.alternateUserAgent = ConfigText(default="")

        # Set some default values
        self["titletext"] = StaticText(feedtitle)
        self["titlemessage"] = StaticText(feedtext)
        self["version"] = StaticText(config.plugins.TVweb.version.value)

        self.feedurl = feedurl
        self.feedtitle = feedtitle
        self.feedtext = feedtext
        self.textcolor = "#00000000"
        self.bgcolor = "#00ffffff"
        self.textsize = 20
	self.olditem = item
	self.index = 0


        # Screen, backgroundlabel and MovingPixmap
        self.skin = "<screen position=\"0,0\" size=\"" + str(size_w) + "," + str(size_h) + "\" flags=\"wfNoBorder\" title=\"TVweb\">"+BASESKIN+" \
            <widget name=\"image1\" position=\"496,23\" size=\"79,73\" zPosition=\"4\" transparent=\"1\" alphatest=\"blend\" /> \
			<ePixmap name=\"linea4\" position=\"58,488\" size=\"410,2\" pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/linea-fs8.png\" alphatest=\"blend\" /> \
			<ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/marcotv-fs8.png\" zPosition=\"5\" position=\"490,16\" size=\"89,84\" alphatest=\"blend\" /> \
            <widget name=\"thumbnail\" position=\"63,342\" size=\"162,139\" zPosition=\"4\" transparent=\"1\" alphatest=\"blend\" /> \
	    <widget name=\"seltitle\" position=\"230,342\" size=\"230,139\" zPosition=\"5\" valign=\"center\" halign=\"left\" backgroundColor=\"#00e0e0e0\" font=\"Regular;19\" transparent=\"1\" foregroundColor=\"#00134270\" /> \
	    <widget name=\"selplot\" position=\"63,496\" size=\"397,143\" zPosition=\"5\" backgroundColor=\"#00e0e0e0\" font=\"Regular;17\" transparent=\"1\" foregroundColor=\"" + self.textcolor + "\" /> \
            <widget name=\"key_blue\" position=\""+ str(size_w-225+60) +",665\" zPosition=\"3\" size=\"140,24\" font=\"Regular;19\" halign=\"left\" backgroundColor=\"#1f771f\" transparent=\"1\" foregroundColor=\"#00000000\" /> \
            <ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/blue.png\" zPosition=\"2\" position=\""+ str(size_w-200) +",665\" size=\"140,24\" alphatest=\"blend\" /> \
			<ePixmap pixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/scroll-fs8.png\" zPosition=\"3\" position=\"1099,98\" size=\"25,558\" alphatest=\"blend\" /> \
	   <widget name=\"listado\" transparent=\"1\" position=\"575,98\" zPosition=\"2\" size=\"549,558\" scrollbarMode=\"showAlways\" foregroundColor=\"#000000\" backgroundColor=\"#00e0e0e0\" selectionPixmap=\"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/sel.png\" foregroundColorSelected=\"#00dddefa\"/> \
           </screen>"

        Screen.__init__(self, session)

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions", "DirectionActions", "MovieSelectionActions"],
        {
            "cancel": self.Exit,
            "ok": self.key_ok,
            "blue": self.selectBookmark,
            "contextMenu": self.key_menu,
        }, -1)


	self.ItemsList = []
	self["seltitle"] = Label()
	self["selplot"] = Label()

	self.ItemsMenuList = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
	self.ItemsMenuList.l.setFont(0, gFont('Regular', 18))
	# mpiero cambiado a 31 para que el alto de la lista no permita lineas cortadas 558/31 de numero exacto
	self.ItemsMenuList.l.setItemHeight(31) 
	self.thumbnails = {}
	self.picload2 = ePicLoad()
	self.picload2.PictureData.get().append(self.finish_decode)
	self["thumbnail"] = Pixmap()
	self.img0="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/item.png"
	if fileExists(self.img0):
		sc = AVSwitch().getFramebufferScale()
		self.picload2.setPara((162, 139, sc[0], sc[1], False, 1, "#00e0e0e0"))
		self.picload2.startDecode(self.img0)
	self.inicio=True


        if self.feedtitle == _("Bookmarks"):
            self.getBookmarks()
        else:
	    self.getitems()

	self["listado"] = self.ItemsMenuList
	self.ItemsMenuList.setList(map(tvlistEntry, self.ItemsList))
	self.img1 = img1
	self["listado"].onSelectionChanged.append(self.SelectionChanged)

        self["key_blue"] = Button(_("Bookmarks"))
		

	self["image1"] = Pixmap()
	self.picload = ePicLoad()
	self.picload.PictureData.get().append(self.paintimgs)
	if img1 != None:
		if fileExists(img1):
			sc = AVSwitch().getFramebufferScale()
			# mpiero icono arriba tamano
			self.picload.setPara((79,73, sc[0], sc[1], 0, 1, "#00e0e0e0"))
			self.picload.startDecode(img1)
	self.onShow.append(self.relist)
	

    def relist(self):
	#self.ItemsList = templist
	self["listado"] = self.ItemsMenuList
	self.ItemsMenuList.setList(map(tvlistEntry, self.ItemsList))
	self["listado"].show()


    def paintimgs(self, picInfo=None):
	ptr = self.picload.getData()
	if ptr != None:
		self["image1"].instance.setPixmap(ptr.__deref__())
		self["image1"].show()


    def getBookmarks(self):

        index = 0
        framePos = 0
        Page = 0


        self.Thumbnaillist = []
	#self.thumbnails = {}
        self.itemlist = []
        self.currPage = -1
        self.maxPage = 0
	self.listado = []
	templist = []
	self.ItemsList = []

	self.olditem = Item(channel="" , title="" , action="" , server="", page=1, url="", thumbnail="", show="" , plot="", extra="" , folder=True)

        bookmarkfile = "/etc/enigma2/TVweb.bookmarks"
        if fileExists(bookmarkfile, 'r'):
            bookmarklist = []
            bookmarkcount = 0
            tmpfile = open(bookmarkfile, "r")
            for line in tmpfile:
                if ':::' in line:
                    bookmarkcount += 1
                    tmpline = line.split(":::")
                    id = bookmarkcount
                    type = str(tmpline[0])
                    name = str(tmpline[1])
                    url  = str(tmpline[2])
                    imgurl = str(tmpline[3])
		    plot = str(tmpline[4])

        	    partes = url.split("|") #self.feedurl.split("|")
        	    canal = partes[1]
        	    print "canal="+canal
        	    accion = partes[2]
        	    print "accion="+accion
        	    urlx = partes[3]
        	    print "url="+urlx
        	    serverx = partes[4]
		    print "server="+serverx


                    # APPEND ITEM TO LIST
                    self.itemlist.append((index, framePos, Page, name, imgurl, url, type, "bookmark",""))
		    if type == "movie":
			f = False
		    else:
			f = True
	    	    templist.append((name, f, True))
		    self.listado.append(Item(channel=canal, title=name , action=accion , server=serverx, page=1, url=urlx, thumbnail=imgurl, show="" , plot=plot, extra="" , folder=True))


	    	    if imgurl != "":
			if imgurl[1] == "/":
				filename = imgurl
				if os_path.exists(filename) == True:
					self.thumbnails[index] = filename
				else:
					self.thumbnails[index]="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/item.png"
				if index == self.index:
					self.PrintImg(self.index)
			else:
                		filename = config.plugins.TVweb.storagepath.value+"/TVweb/images/" + ASCIItranslit.legacyEncode(name+"."+imgurl.split('.')[-1]).lower()
				if not config.plugins.TVweb.downloadimages.value:
					if os_path.exists(filename) == True:
						self.thumbnails[index] = filename
					else:
						self.thumbnails[index]="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/item.png"
					if index == self.index:
						self.PrintImg(self.index)
				elif os_path.exists(filename) == True and config.plugins.TVweb.imagecache.value == True:
					self.thumbnails[index] = filename
					if index == self.index:
						self.PrintImg(self.index)
				else:
            				downloadPage(imgurl, filename, agent="Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.2) Gecko/2008091620 Firefox/3.0.2").addCallback(self.finishdownload,filename, index).addErrback(self.showThumbError, filename, imgurl,index)
	    	    else:
			self.thumbnails[index]="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/item.png"
			if index == self.index:
				self.PrintImg(self.index)

                    index += 1
                    framePos += 1

	    tmpfile.close()

	self.ItemsList = templist
	self["listado"] = self.ItemsMenuList
	self.ItemsMenuList.setList(map(tvlistEntry, self.ItemsList))
	self["listado"].show()
        self.total = len(self.itemlist)
	if self.total == self.index:
		self.index = self.index-1
		if self.index>-1:
			self.PrintImg(self.index)
		else:
			self["thumbnail"].hide()
			self["seltitle"].hide()
			self["selplot"].hide()			



    def getitems(self):
        # Lee el canal
        print "feedtitle="+self.feedtitle
        print "feedurl="+self.feedurl
        print "feedtext="+self.feedtext

        from core import downloadtools
        from servers import servertools
        
        partes = self.feedurl.split("|")
        canal = partes[1]
        print "canal="+canal
        accion = partes[2]
        print "accion="+accion
        urlx = partes[3]
        print "url="+urlx
        serverx = partes[4]
        print "server="+serverx
	item = self.olditem
	item.title = self.feedtitle
	item.url = urlx
	item.channel = canal
	item.action = accion
	item.server = serverx

        if accion=="play":
            try:
                exec "from TVweb.channels import "+canal
                exec "itemlista = "+canal+"."+accion+"(item)"
                item = itemlista[0]
            except:
                pass

            exec "from servers import "+item.server+" as servermodule"
            video_urls = servermodule.get_video_url( item.url )
            
            itemlista = []
            for video_url in video_urls:
                itemvideo = Item(title=video_url[0], url=video_url[1], action="__movieplay")
                itemlista.append(itemvideo)

        elif accion=="findvideos":
            try:
                exec "from TVweb.channels import "+canal
                exec "itemlista = "+canal+"."+accion+"(item)"
                for item in itemlista:
                    item.folder=False
            except:
                from core import scrapertools
                data = scrapertools.cache_page(urlx)
                
                # Busca los enlaces a los videos
                listavideos = servertools.findvideos(data)

          
                itemlista = []
                for video in listavideos:
                    scrapedtitle = item.title.strip() + " - " + video[0]
                    scrapedurl = video[1]
                    server = video[2]

                    itemlista.append( Item(channel=item.channel, title=scrapedtitle , action="play" , server=server, page=item.page, url=scrapedurl, thumbnail=item.thumbnail, show=item.show , plot=item.plot , folder=True) )
        else:
            itemlista = []
	    if accion == "search":
	        partes = self.feedurl.split("@")
		if len(partes)>1:
			text = partes[1]
		else:
			text = ""
	    try:
       	    	exec "from TVweb.channels import "+canal
	    	if accion == "search":
            		exec "itemlista = "+canal+"."+accion+"(item, text)"
	    	else:
           		exec "itemlista = "+canal+"."+accion+"(item)"
	    except:
	    	itemlista.append(Item(title="ERROR in module "+canal))
            print "%d elementos" % len(itemlista)

	self.total = len(itemlista)

        index = 0
        framePos = 0
        Page = 0

        self.Thumbnaillist = []
	self.thumbnails = {}
        self.itemlist = []
	self.listado = []
        self.currPage = -1
        self.maxPage = 0
        
        for item in itemlista:
            if item.action=="__movieplay":
                print "item __movieplay"
                type = "movie"
                name = item.title
                imgurl = item.thumbnail
                url = item.url
            else:
		if item.action == "search":
			print "item de busqueda"
			type = "search"
		else:
                	print "item normal"
                	type = "cat"
                imgurl = item.thumbnail
                url = "TVweb" + "|" + item.channel + "|" + item.action + "|" + item.url + "|" + item.server


	    ###### limpia titulo y pasa a utf8
	    try:
               	name = limpia_texto(item.title)
	    except:
		name = item.title
 	    try:
		name = name.decode("utf-8").encode("utf-8")
	    except:
		try:
			name = name.decode("iso-8859-1").encode("utf-8")
		except:
			pass
 
	    if accion == "mirrors" or accion == "findvideos":   ### change title for tucinecom
		item.title = self.feedtitle
		imgurl = self.olditem.thumbnail
		item.plot = self.olditem.plot

	    ###### pasa imgurl a utf8
 	    try:
		imgurl = imgurl.decode("utf-8").encode("utf-8")
	    except:
		try:
			imgurl = imgurl.decode("iso-8859-1").encode("utf-8")
		except:
			pass

	    ###### limpia detalle y pasa a utf8
	    try:
               	item.plot = limpia_texto(item.plot)
	    except:
		pass
 	    try:
		item.plot = item.plot.decode("utf-8").encode("utf-8")
	    except:
		try:
			item.plot = item.plot.decode("iso-8859-1").encode("utf-8")
		except:
			pass


            # APPEND ITEM TO LIST
	    self.listado.append(item)
            self.itemlist.append((index, framePos, Page, name, imgurl, url, type, "item"))
	    self.ItemsList.append((name, item.folder, False))
	    if imgurl != "" and imgurl!=None:
                filename = config.plugins.TVweb.storagepath.value+"/TVweb/images/" + ASCIItranslit.legacyEncode(name+"_"+imgurl.split(':')[-1]).lower()[25:]
		if not config.plugins.TVweb.downloadimages.value:
			if os_path.exists(filename) == True:
				self.thumbnails[index] = filename
			else:
				self.thumbnails[index]=self.img0
			if index == 0:
				self.PrintImg(0)
		elif os_path.exists(filename) == True and config.plugins.TVweb.imagecache.value == True:
			self.thumbnails[index] = filename
			if index == 0:
				self.PrintImg(0)
		else:
            		downloadPage(imgurl, filename, agent="Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.0.2) Gecko/2008091620 Firefox/3.0.2").addCallback(self.finishdownload,filename, index).addErrback(self.showThumbError, filename, imgurl,index)
	    else:
		self.thumbnails[index]=self.img0
		#if index == 0:
		#	self.PrintImg(0)

            index += 1

    def PrintImg(self,index):
	sc = AVSwitch().getFramebufferScale()
	filename = self.thumbnails[index]
	if fileExists(filename) and not self.inicio:
		print "[TVweb] DECODING THUMBNAIL file: " +filename
		self.picload2.setPara((162, 139, sc[0], sc[1], False, 1, "#00e0e0e0"))
		self.picload2.startDecode(filename)
	self.inicio=False
	self["seltitle"].setText(self.itemlist[index][3])
	self["selplot"].setText(self.listado[index].plot)
	

	

    def finishdownload(self, data, filename, index):
	self.inicio=False
	self.thumbnails[index]=filename
	if index == 0:
		self.PrintImg(0)



    def showThumbError(self, error, filename, imgurl, index):
	print "[TVweb] ERROR download " + imgurl + " -> " + filename + " " + error.getErrorMessage()
	self.thumbnails[index]="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/item.png"
	if index == 0:
		self.PrintImg(0)


    def finish_decode(self, info):
	ptr = self.picload2.getData()
	if ptr != None:
		self["thumbnail"].instance.setPixmap(ptr.__deref__())
		self["thumbnail"].show()


    def SelectionChanged(self):
	index = self["listado"].l.getCurrentSelectionIndex()
	if self.total>0:
		if index<len(self.thumbnails):
			try:
				self.PrintImg(index)
			except:
				filename = "/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/item.png"
				print "[TVweb] DECODING THUMBNAIL file: " +filename
				sc = AVSwitch().getFramebufferScale()
				self.picload2.setPara((162,139, sc[0], sc[1], False, 1, "#00e0e0e0"))
				self.picload2.startDecode(filename)
				self["seltitle"].setText(self.itemlist[index][3])
				self["selplot"].setText(self.listado[index].plot)


    def key_ok(self):
        if not self.itemlist:
            return
	self.index = self["listado"].l.getCurrentSelectionIndex()
 
        partes = self.itemlist[self.index][5].split("|")
        canal = partes[1]
        accion = partes[2]
        urlx = partes[3]
        serverx = partes[4]
	if not self.listado:
		extra = ""
	else:
		extra = self.listado[self.index].extra
        item = Item(title=self.feedtitle,url=urlx,channel=canal,action=accion, server=serverx, extra=extra)
        #if (accion=="findvideos" and canal!="seriesyonkis"): ## or (accion=="detail" and canal=="peliculaseroticas"):
        #    try:
        #        exec "from TVweb.channels import "+canal
        #        exec "itemlista = "+canal+"."+accion+"(item)"
	#	n = 0
	#	i = -1
	#	url = ""
	#	server = ""
        #        for items in itemlista:
        #            items.folder=False
		    # comprueba el primer server que funciona
	#	    video_urls = []
	#	    if (i == -1 or "vk" in items.server) and items.server != server:
	#	    	try:
        #    			exec "from servers import "+items.server+" as servermodule"
        #    			video_urls = servermodule.get_video_url( items.url )
	#			if len(video_urls)>0:
	#				i = n
        #    	    	except:
	#			pass
	#	    server = items.server
	#	    n = n+1
 	#	item = itemlista[i]
        #    except:
        #        from core import scrapertools
        #        data = scrapertools.cache_page(urlx)
                
                # Busca los enlaces a los videos
        #	from servers import servertools
        #        listavideos = servertools.findvideos(data)

	#	n=0
	#	m=0
	#	for videos in listavideos:
	#		if "vk" in videos[0]:
	#			n=m
	#			break
	#		m = m+1
           
	#	if len(listavideos)>0:                
	#		scrapedtitle = item.title.strip() + " - " + listavideos[n][0]
        #        	item.url = listavideos[n][1]
        #        	item.server = listavideos[n][2]

	#    accion = "play" 

	if accion == "play" or (accion=="capitulo" and canal=="mitele"):
            try:
                exec "from TVweb.channels import "+canal
                exec "itemlista = "+canal+"."+accion+"(item)"
                item = itemlista[0]
            except:
                pass


	    title = self.feedtitle
	    item.server = item.server.lower()
	    if item.server != "directo":
	    	video_urls = []
	    	try:
            		exec "from servers import "+item.server+" as servermodule"
            		video_urls = servermodule.get_video_url( item.url )
            	except:
			pass
            	itemlista = []
	    	n=-1
	    	res = -1
            	for video_url in video_urls:
			n = n+1
                	itemvideo = Item(title=video_url[0], url=video_url[1], action="__movieplay")
                	itemlista.append(itemvideo)
			if config.plugins.TVweb.resolution.value in video_url[0] and not "webm" in video_url[0].lower():
			    if item.server!="youtube" or (item.server=="youtube" and not "flv" in video_url[0].lower()):
				res = n
				break
	    	if res ==-1: res=len(video_urls)-1
	    	if len(itemlista)>0:
			try:
	    			self.session.open(MovieInfoScreen, itemlista[res].url, self.listado[self.index], self.thumbnails[self.index], self.listado[self.index].title, self.img1,self.feedtext, itemlista[res].title)
#	    			self.session.open(MovieInfoScreen, itemlista[res].url, self.listado[self.index], self.thumbnails[self.index], self.itemlist[self.index][3], self.img1,self.feedtext, itemlista[res].title)
			except:
				self.SelectionChanged()
	    else:
		try:
			self.session.open(MovieInfoScreen, item.url, self.listado[self.index], self.thumbnails[self.index], self.listado[self.index].title, self.img1,self.feedtext, item.title)
#			self.session.open(MovieInfoScreen, item.url, self.listado[self.index], self.thumbnails[self.index], self.itemlist[self.index][3], self.img1,self.feedtext, item.title)
		except:
			pass

	else:	
	    if (">>" in self.itemlist[self.index][3]) or ("play" in self.itemlist[self.index][3].lower()) or ("siguiente" in self.itemlist[self.index][3].lower()):
		title = self.feedtitle
		text = self.feedtext
	    else:
		title = self.listado[self.index].title ##self.itemlist[self.index][3]
		text = self.feedtext + " - " + self.itemlist[self.index][3]
            if self.itemlist[self.index][6] == "cat":
	        self.session.open(TVweb2, self.itemlist[self.index][5], title, text, self.listado[self.index],self.img1)
            elif self.itemlist[self.index][6] == "movie":
		try:
            		self.session.open(MovieInfoScreen, self.itemlist[self.index][5], self.listado[self.index], self.thumbnails[self.index], title, self.img1, self.feedtext)
		except:
			pass
            elif self.itemlist[self.index][6] == "search":
            	self.searchurl = self.itemlist[self.index][5]
		if fileExists("/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzVirtualKeyboard.pyo"):
			from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
			self.session.openWithCallback(self.SendSearchQuery, spzVirtualKeyboard, titulo = _("Enter Search Term:"), texto = "")
		else:
   	        	self.session.openWithCallback(self.SendSearchQuery, VirtualKeyBoard, title = (_("Enter Search Term:")), text = "")

    def SendSearchQuery(self, query):
	self.index = self["listado"].l.getCurrentSelectionIndex()
        if query is not None:
            searchurl = self.itemlist[self.index][5] + "@" + quote_plus(str(query))
            self.session.open(TVweb2, searchurl, self.itemlist[self.index][3], self.feedtext + " - " + self.itemlist[self.index][3] + ": " + query, self.listado[self.index],self.img1)


    def loadframe(self):
        if self.feedtitle == _("Bookmarks"):
		self["listado"].hide()
		#self["thumbnail"].hide()
		self.total = 0
       		self.getBookmarks()

    def key_menu(self):
        if self.itemlist:
	    self.index = self["listado"].l.getCurrentSelectionIndex()
            self.session.openWithCallback(self.loadframe, TVweb_MenuOptions, self.itemlist[self.index], self.listado[self.index])

    def selectBookmark(self):
	if self.feedtitle!=_("Bookmarks"):
		#self.index = self["listado"].l.getCurrentSelectionIndex()
        	#self.session.open(TVweb2, self.itemlist[self.index][5], _("Bookmarks"), _("Bookmarks from your favorite Movies"),self.listado[self.index],"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/bookmark.png")
        	self.session.open(TVweb2, "", _("Bookmarks"), _("Bookmarks from your favorite Movies"),None,"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/bookmark.png")

    def Exit(self):
        del self.picload
        self.close()



#------------------------------------------------------------------------------------------

class MovieInfoScreen(Screen):
    skin = """<screen name="MovieInfoScreen" position="0,0" size="1280,720" flags="wfNoBorder" title="TVweb" backgroundColor="black">"""+BASESKIN + """
        <widget name="image1" position="496,23" size="79,73" zPosition="4" transparent="1" alphatest="blend" /> 
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/marcotv-fs8.png" zPosition="5" position="490,16" size="89,84" alphatest="blend" /> 
	   <widget name="trailerimg" position="587,143" zPosition="3" size="304,205" transparent="1" alphatest="blend" /> 
		<widget source="trailertitle" transparent="1" render="Label" zPosition="2" valign="center" halign="left" position="587,106" size="528,26" font="Regular; 19" backgroundColor="white" foregroundColor="#00134270" noWrap="1" /> 
		<widget source="message" transparent="1" render="Label" zPosition="2" position="904,143" size="211,110" font="Regular;18" backgroundColor="white" foregroundColor="#00555555" halign="right" /> 
		<widget source="urltitle" transparent="1" render="Label" zPosition="2" position="587,584" size="46,20" font="Regular;18" backgroundColor="white" foregroundColor="#00777777" noWrap="1" halign="left" /> 
		<widget source="url" transparent="1" render="Label" zPosition="2" position="587,604" size="533,43" font="Regular;17" backgroundColor="white" foregroundColor="black" /> 
		<widget source="trailertext" transparent="1" render="Label" zPosition="2" valign="top" halign="left" position="587,365" size="532,205" font="Regular; 20" backgroundColor="white" foregroundColor="black" /> 
    	         
		<widget name="key_green" position="115,385" zPosition="3" size="278,24" font="Regular; 20" halign="left" backgroundColor="white" transparent="1" foregroundColor="black" valign="center" /> 
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/green.png" zPosition="2" position="85,385" size="24,24" alphatest="blend" /> 
		<widget name="key_yellow" position="115,445" zPosition="3" size="280,24" font="Regular;20" halign="left" backgroundColor="white" transparent="1" foregroundColor="black" valign="center" /> 
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/yellow.png" zPosition="2" position="85,445" size="24,24" alphatest="blend" /> 
		<widget name="key_blue" position="115,505" zPosition="3" size="280,24" font="Regular;20" halign="left" backgroundColor="white" transparent="1" foregroundColor="black" valign="center" /> 
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/blue.png" zPosition="2" position="85,505" size="24,24" alphatest="blend" /> 
		<widget name="key_red" position="115,565" zPosition="3" size="280,24" font="Regular;20" halign="left" backgroundColor="white" transparent="1" foregroundColor="black" valign="center" /> 
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/red.png" zPosition="2" position="85,565" size="24,24" alphatest="blend" /> 
				
		<ePixmap name="linea" position="575,356" size="548,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/linea-fs8.png" alphatest="blend" />
		<ePixmap name="linea2" position="575,136" size="548,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/linea-fs8.png" alphatest="blend" />
		<ePixmap name="linea3" position="575,576" size="548,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/linea-fs8.png" alphatest="blend" />
	</screen>
    """
    def __init__(self, session, movieurl, item, fileimage, name, img1=None, message="", tipo=""):
        print "[TVweb] MovieInfoScreen.__init__(movieurl="+movieurl+", fileimage="+fileimage+", name="+name+")"
        Screen.__init__(self, session, item)

        size_w = 1280
        size_h = 720

        self["trailertitle"] = StaticText(name)
        self["trailertext"] = StaticText(item.plot)
        self["trailerimg"] = Pixmap()
	self["image1"] = Pixmap()
        self["titlemessage"] = StaticText(message)
        self["message"] = StaticText(tipo)
	url = movieurl
	###### pasa imgurl a utf8
 	try:
		url = url.decode("utf-8").encode("utf-8")
	except:
		try:
			url = url.decode("iso-8859-1").encode("utf-8")
		except:
			pass
        self["url"] = StaticText(url)
        self["urltitle"] = StaticText("Url:")
        self["version"] = StaticText(config.plugins.TVweb.version.value)

        self["key_red"] = Button(_("Save on HDD"))
        self["key_green"] = Button(_("Direct Play"))
        self["key_yellow"] = Button(_("Cached Play"))
        self["key_blue"] = Button(_("Bookmark"))

    	try:
		name = name.decode("utf-8").encode("utf-8")
	except:
		try:
			name = name.decode("iso-8859-1").encode("utf-8")
		except:
			pass
 
        self.url = movieurl
	self.title = name
	self.item = item
        self.action = None
	if "flv" in movieurl.lower() or "flv" in message.lower():
		ext = 'flv'
	elif "mp4" in movieurl.lower() or "mp4" in message.lower():
		ext = 'mp4'
	elif len(movieurl.split('.')[-1].lower().replace("'","")) == 3:
		ext = movieurl.split('.')[-1].lower().replace("'","")
	else:
		ext = 'avi' 
	filename = ASCIItranslit.legacyEncode(name+"."+ext).lower().replace("'","")
	self.movieinfo = ((name,movieurl,filename,item.thumbnail))
	

        self.useragent = "QuickTime/7.6.2 (qtver=7.6.2;os=Windows NT 5.1Service Pack 3)"
        config.mediaplayer.useAlternateUserAgent.value = True
        config.mediaplayer.alternateUserAgent.value = self.useragent
        config.mediaplayer.useAlternateUserAgent.save()
        config.mediaplayer.alternateUserAgent.save()
        config.mediaplayer.save()

        self.moviefolder = config.plugins.TVweb.moviedir.value
        self.imagefolder = config.plugins.TVweb.storagepath.value+"/TVweb/images"

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
        {
            "cancel": self.Exit,
            "red": self.keyRed,
            "green": self.keyGreen,
            "yellow": self.keyYellow,
            "blue": self.keyBlue
        }, -1)

        # Get FrameBuffer Scale for ePicLoad()
        sc = AVSwitch().getFramebufferScale()
        
        # Init ePicLoad
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.showPosterPixmap)
        self.picload.setPara((310,219, sc[0], sc[1], 0, 1, "#00e0e0e0"))
        
        self.picload.startDecode(fileimage)
        #self.onFirstExecBegin.append(self.GetMovieInfo)

	self.picload2 = ePicLoad()
	self.picload2.PictureData.get().append(self.paintimgs)
	if img1 != None:
		if fileExists(img1):
			sc = AVSwitch().getFramebufferScale()
			# mpiero icono arriba tamano
			self.picload2.setPara((79,73, sc[0], sc[1], 0, 1, "#00e0e0e0"))
			self.picload2.startDecode(img1)


    def paintimgs(self, picInfo=None):
	ptr = self.picload2.getData()
	if ptr != None:
		self["image1"].instance.setPixmap(ptr.__deref__())
		self["image1"].show()


    def keyRed(self):
        self.action = "savemovie"
        self.movieSelectCallback(self.movieinfo)

    def keyGreen(self):
        self.action = "directplayback"
        self.movieSelectCallback(self.movieinfo)

    def keyYellow(self):
        self.action = "cachedplayback"
        self.movieSelectCallback(self.movieinfo)

    def keyBlue(self):
        url = "TVweb" + "|" + self.item.channel + "|" + self.item.action + "|" + self.item.url + "|" + self.item.server
        if self.movieinfo is not None:
            os_system("echo 'movie:::%s:::%s:::%s:::%s' >> /etc/enigma2/TVweb.bookmarks" % (self.movieinfo[0], url, self.movieinfo[3], self.item.plot))
            self.session.open(MessageBox, _("Bookmark added!"), MessageBox.TYPE_INFO, timeout=5)


    def showPosterPixmap(self, picInfo=None):
        ptr = self.picload.getData()
        if ptr != None:
	    	self["trailerimg"].instance.setPixmap(ptr.__deref__())
            	self["trailerimg"].show()
            
    def movieSelectCallback(self, movieinfo):
            if self.action == "cachedplayback":
                self.session.open(PlayMovie, movieinfo, self.url, self.useragent)
            elif self.action == "directplayback":

		str = '4097:0:0:0:0:0:0:0:0:0:%s:%s' % (quote(movieinfo[1]), quote(movieinfo[0]))
		sref = eServiceReference(str)

                sref.setName(movieinfo[0])
                self.session.openWithCallback(self.MoviePlayerCallback, TVwebMoviePlayer, sref, movieinfo)
            elif self.action == "vlcplayback" and VLCSUPPORT:
                try:
                    if vlcServerConfig.getDefaultServer() is None:
                        self.session.open(MessageBox, _("No Default Server configured in VLC Settings"), MessageBox.TYPE_ERROR)
                    else:
                        vlcServerConfig.getDefaultServer().play(self.session, media=self.url, name=self.title, currentList=None, player=boundFunction(VlcPlayer))
                except Exception, error:
                    self.session.open(MessageBox, _("VLC Plugin Error") % error, MessageBox.TYPE_ERROR)

            elif self.action == "savemovie":
                self.saveMovie(movieinfo[0], movieinfo[1], movieinfo[2], movieinfo[3])


    def MoviePlayerCallback(self, response=None):
        if response is not None:
            tmpinfo = []
            tmpinfo.append((response[0]))
            tmpinfo.append((response[1]))
            tmpinfo.append((response[2]))
            tmpinfo.append((response[3]))
            self.action = "vlcplayback"
            self.movieSelectCallback(tmpinfo)

    def saveMovie(self, title, url, filename, fileid):
        if '(VLC)' in title and VLCSUPPORT:
            try:
                if vlcServerConfig.getDefaultServer() is None:
                    self.session.open(MessageBox, _("No Default Server configured in VLC Settings"), MessageBox.TYPE_ERROR)
                else:
                    url = vlcServerConfig.getDefaultServer().playFile(url, 0x44, 0x45)
            except Exception, error:
                self.session.open(MessageBox,("VLC Plugin Error: %s") % error, MessageBox.TYPE_ERROR)

        #if title:
            #if fileid > 1:
            #    addfilenumber = "_"+str(fileid)
            #else:
            #    addfilenumber = ""
            #filename = ASCIItranslit.legacyEncode(title+"."+filename.split('.')[-1]).lower().replace("'","")

        if url[0:4] == "http" or url[0:3] == "ftp":
            if config.mediaplayer.useAlternateUserAgent.value:
                useragentcmd = "--header='User-Agent: %s'" % self.useragent
            else:
                useragentcmd = ""
                
            JobManager.AddJob(downloadJob(self, "wget %s -c '%s' -O '%s/%s'" % (useragentcmd, url, self.moviefolder, filename), self.moviefolder+"/"+filename, title))
            self.LastJobView()
        elif url[0:4] == "rtmp":
	    partes=url.split(" ")
	    urlf=partes[0]
	    if urlf[-1:] == "\"" or urlf[-1:] == "'":
		pass
	    else:
		urlf = "\""+urlf+"\""
	    playpath=""
	    swfurl=""
   	    pageurl=""
	    live=""
	    for parte in partes:
		if "playpath=" in parte.lower():
			playpath=parte.replace("playpath="," -y ")
			if playpath[-1:] == "\"" or playpath[-1:] == "'":
				pass
			else:
				playpath = playpath[:4]+"\""+playpath[4:]+"\""
		if "swfurl=" in parte.lower():
			swfurl=parte.replace("swfUrl="," -s ")
		if "pageurl=" in parte.lower():
			pageurl=parte.replace("pageUrl="," -p ")
		if "live=" in parte.lower():
			live=" -v"
	    urlf = urlf+playpath+swfurl+pageurl+live

            JobManager.AddJob(downloadJob(self, "rtmpdump -r %s -o '%s/%s' -e" % (urlf, self.moviefolder, filename), self.moviefolder+"/"+filename, title))
            self.LastJobView()
        else:
            self.session.open(MessageBox, _("Sorry, this Video can not get saved on HDD.\nOnly HTTP, FTP and RTMP streams can get saved on HDD!"), MessageBox.TYPE_ERROR)
	    self.tfreemem.stop()

    def LastJobView(self):
        currentjob = None
        for job in JobManager.getPendingJobs():
            currentjob = job

        if currentjob is not None:
            self.session.open(JobView, currentjob)

    def error(self, error):
        self.session.open(MessageBox, _("Unexpected Error:\n%s") % (error), MessageBox.TYPE_ERROR)

    def Exit(self):
        del self.picload
        self.close()

#------------------------------------------------------------------------------------------


class PlayMovie(Screen):
    skin = """
        <screen position="center,center" size="400,240" title="Caching Video ..." >
            <widget source="label_filename" transparent="1" render="Label" zPosition="2" position="10,10" size="380,20" font="Regular;19" />
            <widget source="label_destination" transparent="1" render="Label" zPosition="2" position="10,35" size="380,20" font="Regular;19" />
            <widget source="label_speed" transparent="1" render="Label" zPosition="2" position="10,60" size="380,20" font="Regular;19" />
            <widget source="label_timeleft" transparent="1" render="Label" zPosition="2" position="10,85" size="380,20" font="Regular;19" />
            <widget source="label_progress" transparent="1" render="Label" zPosition="2" position="10,110" size="380,20" font="Regular;19" />
            <widget name="activityslider" position="10,150" size="380,30" zPosition="3" transparent="0" />
            <widget name="key_green" position="50,200" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />
            <widget name="key_red" position="200,200" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />
            <ePixmap pixmap="/usr/share/enigma2/skin_default/buttons/green.png" position="50,200" size="140,40" alphatest="on" />
            <ePixmap pixmap="/usr/share/enigma2/skin_default/buttons/red.png" position="200,200" size="140,40" alphatest="on" />
        </screen>"""

    def __init__(self, session, movieinfo, movietitle, useragent):
        self.skin = PlayMovie.skin
        Screen.__init__(self, session)

        self.url = movieinfo[1]
        self.title = movieinfo[0]
        self.filename = movieinfo[2]
        self.movietitle = movietitle
        self.movieinfo = movieinfo
        self.destination = config.plugins.TVweb.storagepath.value+"/TVweb/tmp/"
        self.useragent = useragent

        self.streamactive = False

        self.container=eConsoleAppContainer()
        self.container.appClosed.append(self.copyfinished)
        self.container.stdoutAvail.append(self.progressUpdate)
        self.container.stderrAvail.append(self.progressUpdate)
        self.container.setCWD(self.destination)

        self.oldService = self.session.nav.getCurrentlyPlayingServiceReference()

        self.BgFileEraser = eBackgroundFileEraser.getInstance()

        try:
            req = Request(self.url)
            req.add_header('User-agent',self.useragent)
            usock = urlopen(req)
            filesize =  usock.info().get('Content-Length')
        except Exception, e:
            filesize = 0

        if filesize is None:
            filesize = 0

        self.filesize = float(filesize) # in bytes

        self.dummyfilesize = False
        self.lastcmddata = None
        self.lastlocalsize = 0

        self["key_green"] = Button(_("Play now"))
        self["key_red"] = Button(_("Cancel"))

        self["label_filename"] = StaticText("File: %s" % (self.filename))
        self["label_destination"] = StaticText("Destination: %s" % (config.plugins.TVweb.storagepath.value))
        self["label_progress"] = StaticText("Progress: N/A")
        self["label_speed"] = StaticText("Speed: N/A")
        self["label_timeleft"] = StaticText("Time left: N/A")

        self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
        {
            "cancel": self.exit,
            "ok": self.okbuttonClick,
            "red": self.exit,
            "green": self.playfile
        }, -1)

        self.StatusTimer = eTimer()
        self.StatusTimer.callback.append(self.UpdateStatus)

        self.activityslider = Slider(0, 100)
        self["activityslider"] = self.activityslider

	self.tfreemem = eTimer()
        self.tfreemem.callback.append(self.freemem)
        self.tfreemem.start(60000 * config.plugins.TVweb.freemem.value, False)   #libera memoria
        self.onFirstExecBegin.append(self.firstExecBegin)
        
    def freemem(self):
        os_system("echo 1 > /proc/sys/vm/drop_caches")

    def firstExecBegin(self):
        self.progressperc = 0
        self.copyfile()

    def okbuttonClick(self):
        self.StatusTimer.start(5000, True)
        self.UpdateStatus()

    def UpdateStatus(self):
        if fileExists(self.destination + self.filename, 'r'):
            self.localsize = os_path.getsize(self.destination + self.filename)
        else:
            self.localsize = 0

        if self.filesize > 0 and not self.dummyfilesize:
            self.progressperc = round((self.localsize / self.filesize) * 100, 2)

        if int(self.progressperc) > 0:
            self["activityslider"].setValue(int(self.progressperc))

        if self.lastlocalsize != 0:
            transferspeed = round(((self.localsize - self.lastlocalsize) / 1024.0) / 5, 0)
            kbytesleft = round((self.filesize - self.localsize) / 1024.0,0)
            if transferspeed > 0:
                timeleft = round((kbytesleft / transferspeed) / 60,2)
            else:
                timeleft = 0
        else:
            transferspeed = 0
            kbytesleft = 0
            timeleft = 0

        self.lastlocalsize = self.localsize

        self["label_speed"].setText("Speed: " + str(transferspeed) + " KBit/s")
        self["label_progress"].setText("Progress: " + str(round(((self.localsize / 1024.0) / 1024.0), 2)) + "MB of " + str(round(((self.filesize / 1024.0) / 1024.0), 2)) + "MB (" + str(self.progressperc) + "%)")
        self["label_timeleft"].setText("Time left: " + str(timeleft) + " Minutes")
        self.StatusTimer.start(5000, True)


    def copyfile(self):
        if self.url[0:4] == "http" or self.url[0:3] == "ftp":
            if config.mediaplayer.useAlternateUserAgent.value:
                useragentcmd = "--header='User-Agent: %s'" % self.useragent
            else:
                useragentcmd = ""
            cmd = "wget %s -q '%s' -O '%s/%s' &" % (useragentcmd, self.url, self.destination, self.filename)
        elif self.url[0:4] == "rtmp":
	    partes=self.url.split(" ")
	    url=partes[0]
	    if url[-1:] == "\"" or url[-1:] == "'":
		pass
	    else:
		url = "\""+url+"\""
	    playpath=""
	    swfurl=""
   	    pageurl=""
	    live=""
	    for parte in partes:
		if "playpath=" in parte.lower():
			playpath=parte.replace("playpath="," -y ")
			if playpath[-1:] == "\"" or playpath[-1:] == "'":
				pass
			else:
				playpath = playpath[:4]+"\""+playpath[4:]+"\""
		if "swfurl=" in parte.lower():
			swfurl=parte.replace("swfUrl="," -s ")
		if "pageurl=" in parte.lower():
			pageurl=parte.replace("pageUrl="," -p ")
		if "live=" in parte.lower():
			live=" -v"
	    url = url+playpath+swfurl+pageurl+live

            cmd = "rtmpdump -r %s -o '%s/%s'" % (url, self.destination, self.filename)
        else:
            self.session.openWithCallback(self.exit, MessageBox, _("This stream can not get saved on HDD\nProtocol %s not supported :(") % self.url[0:5], MessageBox.TYPE_ERROR)
            return

        if fileExists(self.destination + self.filename, 'r'):
            self.localsize = os_path.getsize(self.destination + self.filename)
            if self.localsize > 0 and self.localsize >= self.filesize:
                cmd = "echo File already downloaded! Skipping download ..."
            elif self.localsize == 0:
                self.BgFileEraser.erase(self.destination + self.filename)

        self.StatusTimer.start(1000, True)
        self.streamactive = True

        print "[TVweb] execute command: " + cmd
        self.container.execute(cmd)

    def progressUpdate(self, data):
        self.lastcmddata = data
        if data.endswith('%)'):
            startpos = data.rfind("sec (")+5
            if startpos and startpos != -1:
                self.progressperc = int(float(data[startpos:-4]))

                if self.lastlocalsize > 0 and self.progressperc > 0:
                    self.filesize = int(float(self.lastlocalsize/self.progressperc)*100)
                    self.dummyfilesize = True

    def copyfinished(self,retval):
        self.streamactive = False
        self["label_progress"].setText("Progress: 100%")
        self["activityslider"].setValue(100)
	self.tfreemem.stop()
        self.playfile()

    def playfile(self):
        if self.lastlocalsize > 0:
            self.StatusTimer.stop()
            sref = eServiceReference(0x1001, 0, self.destination + self.filename)
            sref.setName(self.movietitle)
            self.session.openWithCallback(self.MoviePlayerCallback, TVwebMoviePlayer, sref, self.movieinfo)
        else:
            self.session.openWithCallback(self.exit, MessageBox, _("Error downloading file:\n%s") % self.lastcmddata, MessageBox.TYPE_ERROR)

    def MoviePlayerCallback(self, response=None):
        self.UpdateStatus()
        if response is not None and VLCSUPPORT:
            try:
                ipaddress = self.convertIP(iNetwork.getAdapterAttribute("eth0", "ip"))
                streamurl = "http://" + ipaddress + ":" + str(config.plugins.Webinterface.http.port.value) + "/file?file=" + self.destination + self.filename
                #self.session.openWithCallback(self.exit, MessageBox, _("START VLC-STREAM:\n%s") % streamurl, MessageBox.TYPE_INFO)
                if vlcServerConfig.getDefaultServer() is None:
                    self.session.openWithCallback(self.exit, MessageBox, _("No Default Server configured in VLC Settings"), MessageBox.TYPE_ERROR)
                else:
                    vlcServerConfig.getDefaultServer().play(self.session, media=streamurl, name=self.movietitle, currentList=None, player=boundFunction(VlcPlayer))
            except Exception, error:
                self.session.openWithCallback(self.exit, MessageBox, _("VLC Plugin Error: %s") % error, MessageBox.TYPE_ERROR)

    def convertIP(self, list):
        if len(list) == 4:
            retstr = "%s.%s.%s.%s" % (list[0], list[1], list[2], list[3])
        else:
            retstr = "0.0.0.0"
        return retstr

    def exit(self, retval=None):
        self.container.kill()
        self.BgFileEraser.erase(self.destination + self.filename)

        self.StatusTimer.stop()
	self.tfreemem.stop()
	self.freemem()
        self.session.nav.playService(self.oldService)
        self.close()

#------------------------------------------------------------------------------------------

class TVweb_MenuOptions(Screen):
    def __init__(self, session, movieinfo, item):
        Screen.__init__(self, session)

        self.skin = """
            <screen position="0,0" size="1280,720" title="TVweb - Menu Options" flags="wfNoBorder">"""+BASESKIN2 + """
                <widget source="itemname" transparent="1" render="Label" halign="center" zPosition="2" position="63,342" size="397,243" backgroundColor="#00ffffff" foregroundColor="#00134270" font="Regular;22" valign="center" />
                <widget source="menu" render="Listbox" zPosition="5" transparent="1" position="585,108" size="529,538" scrollbarMode="showOnDemand" backgroundColor="#00ffffff" foregroundColor="#00000000" foregroundColorSelected="#00dddefa" backgroundColorSelected="#003d3e5a" >
                    <convert type="StringList" />
                </widget>
            </screen>"""

        list = []
        self.movieinfo = movieinfo
	self.item = item
        if self.movieinfo[7] == "bookmark":
            list.append((_("Delete selected bookmark"), "delbookmark", "menu_delbookmark", "50"))
        elif self.movieinfo[6] == "movie":
            list.append((_("Bookmark selected movie"), "addbookmark", "menu_addbookmark", "50"))
        elif self.movieinfo[6] == "cat":
            list.append((_("Bookmark selected category"), "addbookmark", "menu_addbookmark", "50"))
        list.append((_("View Bookmarks"), "viewbookmarks", "menu_viewbookmarks", "50"))
        list.append((_("View Downloads"), "viewdownloads", "menu_viewdownloads", "50"))
        list.append((_("TVweb Settings"), "settingsmenu", "menu_settings", "50"))

        self["menu"] = List(list)
        self["version"] = StaticText(config.plugins.TVweb.version.value)
        self["itemname"] = StaticText(self.movieinfo[3])

        self["actions"] = ActionMap(["OkCancelActions"],
        {
            "cancel": self.Exit,
            "ok": self.okbuttonClick
        }, -1)

    def okbuttonClick(self):
        selection = self["menu"].getCurrent()
        if selection:
            if selection[1] == "addbookmark":
                os_system("echo '%s:::%s:::%s:::%s:::%s' >> /etc/enigma2/TVweb.bookmarks" % (self.movieinfo[6], self.movieinfo[3], self.movieinfo[5], self.movieinfo[4],""))
                self.Exit()
            if selection[1] == "delbookmark":
                bookmarkfile = "/etc/enigma2/TVweb.bookmarks"
                if fileExists(bookmarkfile, 'r'):
                    tmpdata = ""
                    tmpfile = open(bookmarkfile, "r")
                    for line in tmpfile:
                        if self.movieinfo[5] not in line:
                            tmpdata = tmpdata + line

                    tmpfile.close()
                    os_system("echo '%s' > %s" % (tmpdata,bookmarkfile))
                self.Exit()
            elif selection[1] == "viewbookmarks":
                self.session.open(TVweb2, self.movieinfo[5], _("Bookmarks"), _("Bookmarks from your favorite Movies"),self.item,"/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/bookmark.png")
            elif selection[1] == "viewdownloads":
                self.session.openWithCallback(self.Exit, TVweb_TaskViewer)
            elif selection[1] == "settingsmenu":
                self.session.openWithCallback(self.Exit, TVweb_Settings)
            else:
                self.Exit()
        else:
            self.Exit()

    def Exit(self, retval=None):
        self.close()


#------------------------------------------------------------------------------------------


class TVweb_TaskViewer(Screen):
    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        
        self.skin = """
            <screen name="MediathekTasksScreen" position="0,0" size="1280,720" title="TVweb - Active Downloads"  flags="wfNoBorder">"""+BASESKIN2 + """
                <widget source="tasklist" render="Listbox" position="585,108" size="529,538" zPosition="7" scrollbarMode="showOnDemand" transparent="1" backgroundColor="#00ffffff" foregroundColor="#00000000" foregroundColorSelected="#00dddefa" backgroundColorSelected="#003d3e5a">
                    <convert type="TemplatedMultiContent">
                        {"template": [
                                MultiContentEntryText(pos = (0, 1), size = (200, 24), font=1, flags = RT_HALIGN_LEFT, text = 1), # index 1 is the name
                                MultiContentEntryText(pos = (210, 1), size = (150, 24), font=1, flags = RT_HALIGN_RIGHT, text = 2), # index 2 is the state
                                MultiContentEntryProgress(pos = (370, 1), size = (100, 24), percent = -3), # index 3 should be progress 
                                MultiContentEntryText(pos = (480, 1), size = (100, 24), font=1, flags = RT_HALIGN_RIGHT, text = 4), # index 4 is the percentage
                            ],
                        "fonts": [gFont("Regular", 22),gFont("Regular", 18)],
                        "itemHeight": 25
                        }
                    </convert>
                </widget>
                 <widget name="key_red" position="115,565" zPosition="3" size="280,24" font="Regular;20" halign="left" backgroundColor="white" transparent="1" foregroundColor="black" valign="center" /> 
				<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/red.png" zPosition="2" position="85,565" size="24,24" alphatest="blend" />
            </screen>"""
        
        self["shortcuts"] = ActionMap(["SetupActions", "ColorActions"],
        {
            "ok": self.keyOK,
            "cancel": self.keyClose,
            "red": self.keyClose
        }, -1)

        self["tasklist"] = List([])
        self["key_red"] = Button(_("Close"))
        self["version"] = StaticText(config.plugins.TVweb.version.value)
        
        self.Timer = eTimer()
        self.Timer.callback.append(self.TimerFire)

        self.onLayoutFinish.append(self.layoutFinished)
        self.onClose.append(self.__onClose)
        
    def __onClose(self):
        del self.Timer

    def layoutFinished(self):
        self.Timer.startLongTimer(2)

    def TimerFire(self):
        self.Timer.stop()
        self.rebuildTaskList()
    
    def rebuildTaskList(self):
        self.tasklist = []
        for job in JobManager.getPendingJobs():
            self.tasklist.append((job, job.name, job.getStatustext(), int(100*job.progress/float(job.end)) ,str(100*job.progress/float(job.end)) + "%" ))
        self['tasklist'].setList(self.tasklist)
        self['tasklist'].updateList(self.tasklist)
        self.Timer.startLongTimer(2)

    def keyOK(self):
        current = self["tasklist"].getCurrent()
        if current:
            job = current[0]
            self.session.openWithCallback(self.JobViewCB, JobView, job)
    
    def JobViewCB(self, why):
        pass

    def keyClose(self):
        self.close()

#------------------------------------------------------------------------------------------

class TVweb_Settings(Screen, ConfigListScreen):
    skin = """
        <screen name="MultiMediathekSettings" position="0,0" size="1280,720" title="TVweb - Settings"  flags="wfNoBorder" > """+BASESKIN2 + """
            <widget name="config" position="585,108" size="529,538" transparent="1" scrollbarMode="showOnDemand"  backgroundColor="#00ffffff" foregroundColor="#00000000" foregroundColorSelected="#00dddefa" backgroundColorSelected="#003d3e5a"  />
 		<widget name="key_red" position="115,385" zPosition="3" size="280,24" font="Regular;20" halign="left" backgroundColor="white" transparent="1" foregroundColor="black" valign="center" /> 
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/red.png" zPosition="2" position="85,385" size="24,24" alphatest="blend" />
 
 		<widget name="key_green" position="115,445" zPosition="3" size="278,24" font="Regular; 20" halign="left" backgroundColor="white" transparent="1" foregroundColor="black" valign="center" /> 
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/green.png" zPosition="2" position="85,445" size="24,24" alphatest="blend" /> 
		
		<widget name="key_yellow" position="115,565" zPosition="3" size="280,24" font="Regular;20" halign="left" backgroundColor="white" transparent="1" foregroundColor="black" valign="center" /> 
		<!--<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/yellow.png" zPosition="2" position="85,565" size="24,24" alphatest="blend" /> -->
		
		<widget name="key_blue" position="115,505" zPosition="3" size="280,24" font="Regular;20" halign="left" backgroundColor="white" transparent="1" foregroundColor="black" valign="center" /> 
		<!--<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/TVweb/images/blue.png" zPosition="2" position="85,505" size="24,24" alphatest="blend" /> -->
        </screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)

        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("OK"))
        self["key_yellow"] = Button("")
        self["key_blue"] = Button("")
        self["version"] = StaticText(config.plugins.TVweb.version.value)

        self["actions"] = ActionMap(["SetupActions", "ColorActions"],
        {
            "ok": self.keySave,
            "green": self.keySave,
            "red": self.keyCancel,
            "cancel": self.keyCancel
        }, -2)

        self.setTitle("TVweb v%s - Settings" % config.plugins.TVweb.version.value)

        self.oldadultcontentvalue = config.plugins.TVweb.showadultcontent.value
        self.oldstoragepathvalue = config.plugins.TVweb.storagepath.value

        self.cfglist = []
        self.cfglist.append(getConfigListEntry(_("Thumbnail Caching:"), config.plugins.TVweb.imagecache))
        self.cfglist.append(getConfigListEntry(_("Show Adult Content:"), config.plugins.TVweb.showadultcontent))
        self.cfglist.append(getConfigListEntry(_("Download Images?:"), config.plugins.TVweb.downloadimages))
        self.cfglist.append(getConfigListEntry(_("Download Directory:"), config.plugins.TVweb.moviedir))
        self.cfglist.append(getConfigListEntry(_("Cache Folder:"), config.plugins.TVweb.storagepath))
        self.cfglist.append(getConfigListEntry(_("Default Resolution:"), config.plugins.TVweb.resolution))
        self.cfglist.append(getConfigListEntry(_("In downloads, Memory free every (min):"), config.plugins.TVweb.freemem))
        ConfigListScreen.__init__(self, self.cfglist, session)

    def keySave(self):
        config.plugins.TVweb.save()

        if config.ParentalControl.configured.value and config.plugins.TVweb.showadultcontent.value and config.plugins.TVweb.showadultcontent.value != self.oldadultcontentvalue:
            pinList = self.getPinList()
            self.session.openWithCallback(self.pinEntered, PinInput, pinList=pinList, triesEntry=config.ParentalControl.retries.setuppin, title = _("Please enter the correct pin code"), windowTitle = _("Enter pin code"))

        if not os_path.isdir(config.plugins.TVweb.storagepath.value):
            self.session.open(MessageBox, "The directory %s does not exist!" % config.plugins.TVweb.storagepath.value, MessageBox.TYPE_ERROR)
            return

        if config.plugins.TVweb.storagepath.value != self.oldstoragepathvalue:
            os_system("rm -rf "+self.oldstoragepathvalue+"/TVweb")
            os_system("mkdir -p "+config.plugins.TVweb.storagepath.value+"/TVweb")
            os_system("mkdir -p "+config.plugins.TVweb.storagepath.value+"/TVweb/images")
            os_system("mkdir -p "+config.plugins.TVweb.storagepath.value+"/TVweb/movies")
            os_system("mkdir -p "+config.plugins.TVweb.storagepath.value+"/TVweb/tmp")

        configfile.save()
        self.close()

    def keyCancel(self):
        for item in self.cfglist:
            item[1].cancel()
        self.close()

    def getPinList(self):
        pinList = []
        pinList.append(config.ParentalControl.setuppin.value)
        for x in config.ParentalControl.servicepin:
            pinList.append(x.value)
        return pinList

    def pinEntered(self, result):
        if result is None:
            config.plugins.TVweb.showadultcontent.value = False
            config.plugins.TVweb.save()
        elif not result:
            config.plugins.TVweb.showadultcontent.value = False
            config.plugins.TVweb.save()

#------------------------------------------------------------------------------------------
def menu(menuid, **kwargs):
    if menuid == "mainmenu":
	return [("TVweb", main, "TVweb", 4)]
    return []

def main(session, **kwargs):
    print "[TVweb] main"
    session.open(TVweb)

def Plugins(**kwargs):
    print "[TVweb] Plugins"
    return [
        PluginDescriptor(name = "TVweb", description = "TVweb 1.0", icon="plugin-icon.png", where = PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]
