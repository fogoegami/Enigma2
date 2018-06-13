# -*- coding: utf-8 -*-
# Auto EPG downloader
# Copyright (c) 2boom 2015
# v.03-r3
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.config import config, getConfigListEntry, ConfigText, ConfigInteger, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Sources.List import List
from Components.Language import language
from Components.Sources.StaticText import StaticText
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ
import os
import gettext
from enigma import eEPGCache
from types import *
from enigma import *
import sys, traceback
import time
import new
import _enigma
import enigma
import socket
import gzip
import urllib

lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('epgdd', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/epgdd/locale/'))

def _(txt):
	t = gettext.dgettext('epgdd', txt)
	if t == txt:
		t = gettext.gettext(txt)
	return t
	
def mountp():
	pathmp = []
	if os.path.isfile('/proc/mounts'):
		for line in open('/proc/mounts'):
			if '/dev/sd' in line or '/dev/disk/by-uuid/' in line or '/dev/mmc' in line or '/dev/mtdblock' in line:
				pathmp.append(line.split()[1].replace('\\040', ' ') + '/')
	pathmp.append('/etc/enigma2/')
	pathmp.append('/tmp/')
	return pathmp
	
def logging(line):
	log_file = open('/tmp/epgdd.log', 'a')
	log_file.write(line)
	log_file.close()
	
config.plugins.epgdd = ConfigSubsection()
config.plugins.epgdd.direct = ConfigSelection(choices = mountp())
config.plugins.epgdd.epgname = ConfigText(default='epg.dat', visible_width = 50, fixed_size = False)
config.plugins.epgdd.url = ConfigText(default='http://openbox.boxtvmania.com/epg/epg.dat.gz', visible_width = 80, fixed_size = False)
config.plugins.epgdd.leghtfile = ConfigInteger(default = 0)
#config.plugins.epgdd.menuext = ConfigYesNo(default = False)
config.plugins.epgdd.checkepgfile = ConfigYesNo(default = False)
config.plugins.epgdd.nocheck = ConfigYesNo(default = True)
config.plugins.epgdd.first = ConfigYesNo(default = True)
config.plugins.epgdd.checkp = ConfigSelection(default = '60', choices = [
		('30', _("30 min")),
		('60', _("60 min")),
		('120', _("120 min")),
		('180', _("180 min")),
		('240', _("240 min")),
		])
config.plugins.epgdd.ultimoactualizado = ConfigText(default=_('ultimo epg.dat actualizado - aún no'))

class epgdd(ConfigListScreen, Screen):
	skin = """
<screen name="epgdd" position="center,160" size="850,230" title="">
  <widget position="15,10" size="820,150" name="config" scrollbarMode="showOnDemand" />
  <ePixmap position="10,225" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/epgdd/images/red.png" alphatest="blend" />
  <widget source="key_red" render="Label" position="10,195" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
  <ePixmap position="175,225" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/epgdd/images/green.png" alphatest="blend" />
  <widget source="key_green" render="Label" position="175,195" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
  <ePixmap position="340,225" zPosition="1" size="200,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/epgdd/images/yellow.png" alphatest="blend" />
  <widget source="key_yellow" render="Label" position="340,195" zPosition="2" size="200,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
  <widget source="ultimoactualizado" render="Label" position="20,167" zPosition="2" size="810,24" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="grey" transparent="1" />
<eLabel position="30,162" size="790,2" backgroundColor="grey" />
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		config.plugins.epgdd.direct = ConfigSelection(choices = mountp())
		self.setTitle(_('EPG desde %s') % config.plugins.epgdd.url.value.split('/')[2])
		self.list = []
		self.list.append(getConfigListEntry(_('Select path to save epg.dat'), config.plugins.epgdd.direct))
		self.list.append(getConfigListEntry(_('Set EPG filename'), config.plugins.epgdd.epgname))
		self.list.append(getConfigListEntry(_('Download url'), config.plugins.epgdd.url))
		self.list.append(getConfigListEntry(_('Periodicity checks'),config.plugins.epgdd.checkp))
		self.list.append(getConfigListEntry(_('Check epg.dat exists'), config.plugins.epgdd.checkepgfile))
		#self.list.append(getConfigListEntry(_('Show Auto EPG Downloader in ExtensionMenu'), config.plugins.epgdd.menuext))
		ConfigListScreen.__init__(self, self.list, session=session)
		self['key_red'] = StaticText(_('Close'))
		self['key_green'] = StaticText(_('Save'))
		self['key_yellow'] = StaticText(_('Download EPG'))
		self['ultimoactualizado'] = StaticText()
		self['ultimoactualizado'].text = config.plugins.epgdd.ultimoactualizado.value
		self.timer = enigma.eTimer() 
		self.timer.callback.append(self.updatestatus)
		self.timer.start(3000, True)
		self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'],
		{
			'red': self.cancel,
			'cancel': self.cancel,
			'green': self.save,
			'yellow': self.loadepgdat,
			'ok': self.save
		}, -2)
		
	def updatestatus(self):
		self.timer.stop()
		self['ultimoactualizado'].text = config.plugins.epgdd.ultimoactualizado.value
		self.timer.start(3000, True)

	def save(self):
		for i in self['config'].list:
			i[1].save()
		now = time.localtime(time.time())
		if self.image_is_OA():
			config.misc.epgcachefilename.value = config.plugins.epgdd.epgname.value
			config.misc.epgcachepath.value = config.plugins.epgdd.direct.value
			config.misc.epgcachepath.save()
			config.misc.epgcachefilename.save()
			logging('%02d:%02d:%d %02d:%02d:%02d - set %s\r\n%02d:%02d:%d %02d:%02d:%02d - set %s\r\n' % \
				(now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, config.misc.epgcachepath.value, now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, config.misc.epgcachefilename.value))
		else:
			config.misc.epgcache_filename.value = '%s%s' % (config.plugins.epgdd.direct.value, config.plugins.epgdd.epgname.value)
			config.misc.epgcache_filename.save()
			logging('%02d:%02d:%d %02d:%02d:%02d - set %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, config.misc.epgcache_filename.value))
		logging('%02d:%02d:%d %02d:%02d:%02d - set %s\r\n%02d:%02d:%d %02d:%02d:%02d - set %s min check period\r\n' % \
			(now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, config.plugins.epgdd.url.value, now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, config.plugins.epgdd.checkp.value))
		configfile.save()
		if self.image_is_pli():
			from Components.PluginComponent import plugins
			plugins.reloadPlugins()
		self.mbox = self.session.open(MessageBox,(_('configuration is saved')), MessageBox.TYPE_INFO, timeout = 4 )

	def cancel(self):
		self.close()

	def loadepgdat(self):
		self.session.open(get_epgdat)

	def image_is_OA(self):
		if os.path.isfile('/etc/issue'):
			for line in open('/etc/issue'):
				if 'openatv' in line or 'openhdf' in line or 'openvix' in line.lower():
					return True
		return False

	def image_is_pli(self):
		if os.path.isfile('/etc/issue'):
			for line in open('/etc/issue'):
				if 'openpli' in line.lower():
					return True
		return False

class Check_EPG():
	def __init__(self):
		self.dialog = None

	def gotSession(self, session):
		self.session = session
		self.timer = enigma.eTimer() 
		self.timermin = enigma.eTimer() 
		self.timermin.callback.append(self.check_change_min)
		self.timer.callback.append(self.check_change)
		self.timermin.startLongTimer(30)
		self.timer.startLongTimer(60)

	def check_change(self):
		self.timer.stop()
		now = time.localtime(time.time())
		try:
			lenght_epgfile = int(urllib.urlopen(config.plugins.epgdd.url.value).info()['content-length'])
			logging('%02d:%02d:%d %02d:%02d:%02d - size epg.tar.gz: %d bytes\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, lenght_epgfile))
			if config.plugins.epgdd.leghtfile.value != lenght_epgfile:
				self.loadepgdat()
		except Exception as e:
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec,  str(e)))
		self.timer.startLongTimer(int(config.plugins.epgdd.checkp.value) * 60)

	def check_change_min(self):
		self.timermin.stop()
		now = time.localtime(time.time())
		if config.plugins.epgdd.first.value and config.plugins.epgdd.nocheck.value:
			config.plugins.epgdd.first.value = False
			if os.path.isfile('%s%s' % (config.plugins.epgdd.direct.value, config.plugins.epgdd.epgname.value)):
				epgcache = new.instancemethod(_enigma.eEPGCache_load,None,eEPGCache)
				epgcache = eEPGCache.getInstance().load()
				logging('%02d:%02d:%d %02d:%02d:%02d - reload epg.dat\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
				
		if config.plugins.epgdd.checkepgfile.value and config.plugins.epgdd.nocheck.value:
			if not os.path.isfile('%s%s' % (config.plugins.epgdd.direct.value, config.plugins.epgdd.epgname.value)):
				logging('%02d:%02d:%d %02d:%02d:%02d - restore epg.dat\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
				self.loadepgdat()
		self.timermin.startLongTimer(60)

	def loadepgdat(self):
		config.plugins.epgdd.nocheck.value = False
		now = time.localtime(time.time())
		try:
			if self.isServerOnline():
				config.plugins.epgdd.leghtfile.value = int(urllib.urlopen(config.plugins.epgdd.url.value).info()['content-length'])
				config.plugins.epgdd.leghtfile.save()
				configfile.save()
				urllib.urlretrieve (config.plugins.epgdd.url.value, '/tmp/epg.dat.gz')
				if os.path.isfile('/tmp/epg.dat.gz'):
					inFile = gzip.GzipFile('/tmp/epg.dat.gz', 'rb')
					s = inFile.read()
					inFile.close()
					outFile = file('%s%s' % (config.plugins.epgdd.direct.value, config.plugins.epgdd.epgname.value), 'wb')
					outFile.write(s)
					outFile.close()
					if os.path.isfile('/tmp/epg.dat.gz'):
						os.remove('/tmp/epg.dat.gz')
					epgcache = new.instancemethod(_enigma.eEPGCache_load,None,eEPGCache)
					epgcache = eEPGCache.getInstance().load()
					logging('%02d:%02d:%d %02d:%02d:%02d - Auto Donwload & Unzip epg.dat.gz successful\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
					config.plugins.epgdd.ultimoactualizado.value = _('ultimo epg.dat actualizado - %02d:%02d:%d %02d:%02d:%02d' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
					config.plugins.epgdd.ultimoactualizado.save()
					configfile.save()
			else:
				logging('%02d:%02d:%d %02d:%02d:%02d - %s not respond\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, config.plugins.epgdd.url.value.split('/')[2]))
		except Exception as e:
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, str(e)))
		config.plugins.epgdd.nocheck.value = True

	def isServerOnline(self):
		try:
			socket.gethostbyaddr(config.plugins.epgdd.url.value.split('/')[2])
		except Exception as e:
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, str(e)))
			return False
		return True

SKIN_EPG = """
<screen name="get_epgdat" position="center,140" size="625,35" title="Please wait">
  <widget source="status" render="Label" position="10,5" size="605,22" zPosition="2" font="Regular; 20" halign="center" transparent="2" />
</screen>"""

class get_epgdat(Screen):
	def __init__(self, session, args=None):
		Screen.__init__(self, session)
		self.session = session
		self.skin = SKIN_EPG
		self.setTitle(_('Please wait'))
		self['status'] = StaticText()
		config.plugins.epgdd.nocheck.value = False
		now = time.localtime(time.time())
		if self.isServerOnline():
			try:
				config.plugins.epgdd.leghtfile.value = int(urllib.urlopen(config.plugins.epgdd.url.value).info()['content-length'])
				config.plugins.epgdd.leghtfile.save()
				configfile.save()
				urllib.urlretrieve (config.plugins.epgdd.url.value, '/tmp/epg.dat.gz')
				if os.path.isfile('/tmp/epg.dat.gz'):
					inFile = gzip.GzipFile('/tmp/epg.dat.gz', 'rb')
					s = inFile.read()
					inFile.close()
					outFile = file('%s%s' % (config.plugins.epgdd.direct.value, config.plugins.epgdd.epgname.value), 'wb')
					outFile.write(s)
					outFile.close()
					if os.path.isfile('/tmp/epg.dat.gz'):
						os.remove('/tmp/epg.dat.gz')
					epgcache = new.instancemethod(_enigma.eEPGCache_load,None,eEPGCache)
					epgcache = eEPGCache.getInstance().load()
					self['status'].text = _('Download epg.dat successful')
					logging('%02d:%02d:%d %02d:%02d:%02d - Manual Donwload & Unzip epg.dat.gz successful\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
					config.plugins.epgdd.ultimoactualizado.value = _('ultimo epg.dat actualizado - %02d:%02d:%d %02d:%02d:%02d' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec))
					config.plugins.epgdd.ultimoactualizado.save()
					configfile.save()
			except Exception as e:
				self['status'].text = _('Manual Donwloading epg.dat.gz error')
				logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, str(e)))
		else:
			self['status'].text = _('%s not respond' % config.plugins.epgdd.url.value.split('/')[2])
			logging('%02d:%02d:%d %02d:%02d:%02d - %s not respond\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, config.plugins.epgdd.url.value.split('/')[2]))
		config.plugins.epgdd.nocheck.value = True
		self.timer = enigma.eTimer() 
		self.timer.callback.append(self.endshow)
		self.timer.startLongTimer(3)

	def endshow(self):
		self.timer.stop()
		self.close()
		
	def isServerOnline(self):
		try:
			socket.gethostbyaddr(config.plugins.epgdd.url.value.split('/')[2])
		except Exception as e:
			logging('%02d:%02d:%d %02d:%02d:%02d - %s\r\n' % (now.tm_mday, now.tm_mon, now.tm_year, now.tm_hour, now.tm_min, now.tm_sec, str(e)))
			return False
		return True

def main(session, **kwargs):
	session.open(epgdd)

pEpg = Check_EPG()

def sessionstart(reason,session=None, **kwargs):
	if reason == 0:
		pEpg.gotSession(session)

def Plugins(**kwargs):
	result = [
		PluginDescriptor(
			where = [PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART],
			fnc = sessionstart
		),
		PluginDescriptor(
			name=_("2boom's Auto EPG Downloader"),
			description = _('EPG desde %s') % config.plugins.epgdd.url.value.split('/')[2],
			where = PluginDescriptor.WHERE_PLUGINMENU,
			icon = 'epgdd.png',
			fnc = main
		),
	]
	if config.plugins.epgdd.menuext.value:
		result.append(PluginDescriptor(
			name=_("2boom's Auto EPG Downloader"),
			description = _('EPG desde %s') % config.plugins.epgdd.url.value.split('/')[2],
			where = PluginDescriptor.WHERE_EXTENSIONSMENU,
			fnc = main
			))
	return result

