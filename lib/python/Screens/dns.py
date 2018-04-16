from Screens.Screen import Screen
from Screens.Standby import TryQuitMainloop
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.config import config, getConfigListEntry, ConfigText, ConfigPassword, ConfigClock, ConfigIP, ConfigInteger, ConfigDateTime, ConfigSelection, ConfigSubsection, ConfigYesNo, configfile, NoSave
from Components.ConfigList import ConfigListScreen
from Components.Harddisk import harddiskmanager
from Components.Pixmap import Pixmap
from Components.Sources.List import List
from Components.Input import Input
from Tools.LoadPixmap import LoadPixmap
from Screens.Console import Console
from Components.Console import Console as iConsole
from Components.Label import Label
from Components.MenuList import MenuList
from Components.ActionMap import ActionMap, NumberActionMap
from Plugins.Plugin import PluginDescriptor
from Components.Language import language
from Components.ScrollLabel import ScrollLabel
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from time import *
from enigma import eEPGCache
from types import *
from enigma import *
import sys, traceback
import re
import new
import _enigma
import enigma
import time
from time import localtime, strftime
import datetime
from os import environ
import os
import gettext
import glob
import socket
import gzip
import urllib
import stat

config.dnsserver = ConfigSelection(default = '1', choices = [
		('1', _("no-ip.com")),
		('2', _("changeip.com")),
		])
config.dnsuser = ConfigText(default="xxxxx", visible_width = 70, fixed_size = False)
config.dnspass = ConfigText(default="*****", visible_width = 70, fixed_size = False)
config.dnshost = ConfigText(default="xxx.xxx.xxx", visible_width = 70, fixed_size = False)
config.dnstime = ConfigSelection(default = '0', choices = [
		('0', _("Off")),
		('15', _("15 min")),
		('30', _("30 min")),
		('45', _("45 min")),
		('1', _("60 min")),
		('2', _("120 min")),
		('3', _("180 min")),
		])

def cronpath():
	path = "/etc/cron/crontabs/root"
	if fileExists("/etc/cron/crontabs"):
		return "/etc/cron/crontabs/root"
	elif fileExists("/etc/bhcron"):
		return "/etc/bhcron/root"
	elif fileExists("/etc/crontabs"):
		return "/etc/crontabs/root"
	elif fileExists("/var/spool/cron/crontabs"):
		return "/var/spool/cron/crontabs/root"
	return path

class ddnsmenu(ConfigListScreen, Screen):
	skin = """
<screen name="ddnsmenu" position="center,160" size="750,370" title="dns dinamico">
	<widget position="15,10" size="720,200" name="config" scrollbarMode="showOnDemand" />
	<ePixmap position="10,358" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/boxpanel/images/red.png" alphatest="blend" />
	<widget source="key_red" render="Label" position="10,328" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<ePixmap position="175,358" zPosition="1" size="165,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/boxpanel/images/green.png" alphatest="blend" />
	<widget source="key_green" render="Label" position="175,328" zPosition="2" size="165,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
	<ePixmap position="340,358" zPosition="1" size="195,2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/boxpanel/images/yellow.png" alphatest="blend" />
	<widget source="key_yellow" render="Label" position="340,328" zPosition="2" size="195,30" font="Regular;20" halign="center" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
</screen>"""

	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.list = []
		self.iConsole = iConsole()
		self.path = cronpath()
		self["key_red"] = StaticText(_("Close"))
		self["key_green"] = StaticText(_("Save"))
		self["key_yellow"] = StaticText(_("Update"))
		self["setupActions"] = ActionMap(["SetupActions", "ColorActions", "EPGSelectActions"],
		{
			"red": self.cancel,
			"cancel": self.cancel,
			"green": self.save_values,
			"yellow": self.UpdateNow,
			"ok": self.save_values
		}, -2)
		self.list.append(getConfigListEntry(_("Select DDNS server"), config.dnsserver))
		self.list.append(getConfigListEntry(_("Username"), config.dnsuser))
		self.list.append(getConfigListEntry(_("Password"), config.dnspass))
		self.list.append(getConfigListEntry(_("Hostname"), config.dnshost))
		self.list.append(getConfigListEntry(_("Update Time"), config.dnstime))
		ConfigListScreen.__init__(self, self.list)
		self.onShow.append(self.Title)
		
	def Title(self):
		self.setTitle(_("DNS dinamico"))

	def cancel(self):
		for i in self["config"].list:
			i[1].cancel()
		self.close()

	def save_values(self):
		if not fileExists(self.path):
			open(self.path, 'a').close()
		for i in self["config"].list:
			i[1].save()
		configfile.save()
		if fileExists(self.path):
			remove_line(self.path, 'no-ip.py')
		if config.dnstime.value is not '0':
			self.cron_setup()
			self.create_script()
		self.mbox = self.session.open(MessageBox,(_("configuration is saved")), MessageBox.TYPE_INFO, timeout = 4 )
		
	def create_script(self):
		updatestr = ''
		if config.dnsserver.value is '1':
			updatestr = "http://%s:%s@dynupdate.no-ip.com/nic/update?hostname=%s" % (config.dnsuser.value, config.dnspass.value, config.dnshost.value)
		else:
			updatestr = "https://%s:%s@nic.changeip.com/nic/update?cmd=update&set=$CIPSET&hostname=%s" % (config.dnsuser.value, config.dnspass.value, config.dnshost.value)
		with open('/usr/bin/no-ip.py', 'w') as update_script:
			update_script.write('#!/usr/bin/env python\n# -*- coding: utf-8 -*-\n# Copyright (c) 2boom 2014\n\n')
			update_script.write('import requests\n\n')
			update_script.write('res = requests.get("%s")\n' % updatestr)
			update_script.write('print res.text\n')
			update_script.close()

	def cron_setup(self):
		if config.dnstime.value is not '0':
			with open(self.path, 'a') as cron_root:
				if config.dnstime.value not in ('1', '2', '3'):
					cron_root.write('*/%s * * * * python /usr/bin/no-ip.py\n' % config.dnstime.value)
				else:
					cron_root.write('1 */%s * * * python /usr/bin/no-ip.py\n' % config.dnstime.value)
				cron_root.close()
			with open('%scron.update' % self.path[:-4], 'w') as cron_update:
				cron_update.write('root')
				cron_update.close()

	def UpdateNow(self):
		if not fileExists('/usr/bin/no-ip.py'):
			self.create_script()
		if fileExists('/usr/bin/no-ip.py'):
			self.session.open(Console, title = _("DNS updating..."), cmdlist = ["python /usr/bin/no-ip.py"], closeOnSuccess = False)
		else:
			self.mbox = self.session.open(MessageBox,(_("update script not found...")), MessageBox.TYPE_INFO, timeout = 4 )
