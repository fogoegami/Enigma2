from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen, ConfigList
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from Components.config import config, ConfigSubsection, ConfigBoolean, getConfigListEntry, ConfigSelection, ConfigYesNo, ConfigIP, ConfigNothing
from Components.Network import iNetwork
from Components.Ipkg import IpkgComponent
from enigma import eDVBDB

config.misc.installwizard = ConfigSubsection()
config.misc.installwizard.hasnetwork = ConfigBoolean(default = False)
config.misc.installwizard.ipkgloaded = ConfigBoolean(default = False)

class InstallWizard(Screen, ConfigListScreen):

	STATE_UPDATE = 0
	INSTALL_CHANNELS = 1
	INSTALL_PLUGINS = 2
	SCAN = 3

	def __init__(self, session, args = None):
		Screen.__init__(self, session)

		self.index = args
		self.list = []
		self.doNextStep = False
		ConfigListScreen.__init__(self, self.list)

		if self.index == self.STATE_UPDATE:
			config.misc.installwizard.hasnetwork.value = False
			config.misc.installwizard.ipkgloaded.value = False
			modes = {0: " "}
			self.enabled = ConfigSelection(choices = modes, default = 0)
			self.adapters = [(iNetwork.getFriendlyAdapterName(x),x) for x in iNetwork.getAdapterList()]
			is_found = False
			for x in self.adapters:
				if x[1] == 'eth0' or x[1] == 'eth1':
					if iNetwork.getAdapterAttribute(x[1], 'up'):
						self.ipConfigEntry = ConfigIP(default = iNetwork.getAdapterAttribute(x[1], "ip"))
						iNetwork.checkNetworkState(self.checkNetworkCB)
						if_found = True
					else:
						iNetwork.restartNetwork(self.checkNetworkLinkCB)
					break
			if is_found is False:
				self.createMenu()
		elif self.index == self.INSTALL_CHANNELS:
			self.noplugins = ConfigNothing()
			self.doplugins = ConfigNothing()
			self.createMenu()
		elif self.index == self.INSTALL_PLUGINS:
			self.noplugins = ConfigNothing()
			self.doplugins = ConfigNothing()
			self.createMenu()
		elif self.index == self.SCAN:
			self.noscan = ConfigNothing()
			self.autoscan = ConfigNothing()
			self.manualscan = ConfigNothing()
			self.fastscan = ConfigNothing()
			self.cablescan = ConfigNothing()
			self.createMenu()

	def checkNetworkCB(self, data):
		if data < 3:
			config.misc.installwizard.hasnetwork.value = True
		self.createMenu()

	def checkNetworkLinkCB(self, retval):
		if retval:
			iNetwork.checkNetworkState(self.checkNetworkCB)
		else:
			self.createMenu()

	def createMenu(self):
		try:
			test = self.index
		except:
			return
		self.list = []
		if self.index == self.STATE_UPDATE:
			if config.misc.installwizard.hasnetwork.value:
				self.list.append(getConfigListEntry(_("Your internet connection is working (ip: %s)") % (self.ipConfigEntry.getText()), self.enabled))
			else:
				self.list.append(getConfigListEntry(_("Your receiver does not have an internet connection"), self.enabled))
		elif self.index == self.INSTALL_CHANNELS:
			self.list.append(getConfigListEntry(_("No, I do not want to install channels"), self.noplugins))
			self.list.append(getConfigListEntry(_("Yes, I do want to install channels"), self.doplugins))
		elif self.index == self.INSTALL_PLUGINS:
			self.list.append(getConfigListEntry(_("No, I do not want to install plugins"), self.noplugins))
			self.list.append(getConfigListEntry(_("Yes, I do want to install plugins"), self.doplugins))
		elif self.index == self.SCAN:
			self.list.append(getConfigListEntry(_("I do not want to perform any service scans"), self.noscan))
			self.list.append(getConfigListEntry(_("Do an automatic service scan now"), self.autoscan))
			self.list.append(getConfigListEntry(_("Do a manual service scan now"), self.manualscan))
			self.list.append(getConfigListEntry(_("Do a fast service scan now"), self.fastscan))
			self.list.append(getConfigListEntry(_("Do a cable service scan now"), self.cablescan))
		self["config"].list = self.list
		self["config"].l.setList(self.list)

	def keyLeft(self):
		if self.index == 0:
			return
		ConfigListScreen.keyLeft(self)
		self.createMenu()

	def keyRight(self):
		if self.index == 0:
			return
		ConfigListScreen.keyRight(self)
		self.createMenu()

	def run(self):
		if self.index == self.STATE_UPDATE and config.misc.installwizard.hasnetwork.value:
			self.session.open(InstallWizardIpkgUpdater, self.index, _('Please wait (updating packages)'), IpkgComponent.CMD_UPDATE)
			self.doNextStep = True
		elif self.index == self.INSTALL_CHANNELS:
			if self["config"].getCurrent()[1] == self.doplugins:
				from Plugins.Extensions.nightupdate.plugin import nightupdate_Updater
				self.session.open(nightupdate_Updater)
			self.doNextStep = True
		elif self.index == self.INSTALL_PLUGINS:
			if self["config"].getCurrent()[1] == self.doplugins:
				from PluginBrowser import PluginDownloadBrowser
				self.session.open(PluginDownloadBrowser, 0)
			self.doNextStep = True
		elif self.index == self.SCAN:
			if self["config"].getCurrent()[1] == self.autoscan:
				from Screens.ScanSetup import ScanSimple
				self.session.open(ScanSimple)
			elif self["config"].getCurrent()[1] == self.manualscan:
				from Screens.ScanSetup import ScanSetup
				self.session.open(ScanSetup)
			elif self["config"].getCurrent()[1] == self.fastscan:
				from Plugins.SystemPlugins.FastScan.plugin import FastScanMain
				FastScanMain(self.session)
			elif self["config"].getCurrent()[1] == self.cablescan:
				from Plugins.SystemPlugins.CableScan.plugin import CableScanMain
				CableScanMain(self.session)
			else:
				self.doNextStep = True

class InstallWizardIpkgUpdater(Screen):
	def __init__(self, session, index, info, cmd, pkg = None):
		Screen.__init__(self, session)

		self["statusbar"] = StaticText(info)

		self.pkg = pkg
		self.index = index
		self.state = 0
		
		self.ipkg = IpkgComponent()
		self.ipkg.addCallback(self.ipkgCallback)

		self.ipkg.startCmd(cmd, pkg)

	def ipkgCallback(self, event, param):
		if event == IpkgComponent.EVENT_DONE:
			if self.index == InstallWizard.STATE_UPDATE:
				config.misc.installwizard.ipkgloaded.value = True

				self.close()
				

