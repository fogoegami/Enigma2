from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Label import Label
from Tools.LoadPixmap import LoadPixmap
import os
from Components.config import config, ConfigText, ConfigSubsection, getConfigListEntry, NoSave
from Components.ConfigList import ConfigListScreen
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from random import Random
import string
from os import environ
from telnetlib import Telnet
import gettext
from Screens.VirtualKeyBoard import VirtualKeyBoard


class SetPasswd(Screen):
    skin = '\n\t<screen position="center,center" size="700,300" title="Centro Password Openbox">\n\t\t<widget name="lab1" position="20,20" size="660,215" font="Regular;24" halign="center" valign="center" transparent="1"/><widget name="key_red" position="280,250" zPosition="2" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="red" transparent="1" /></screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self['lab1'] = Label(_('You have accessed the Password control center to access your Receiver, choose the desired option.'))
        self['lab2'] = Label(_('OPENBOX'))
        self['lab3'] = Label(_('Access Password Center'))
        self['lab4'] = Label(_('Password Center'))
        self['key_red'] = Label(_('Reset'))
        self['key_green'] = Label(_('Change'))
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'back': self.close,
         'red': self.passwd,'green': self.change})

    def change(self):
        self.session.open(SetPasswdMain)

    def passwd(self):
        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('The Password will be deleted.\nAre you sure you want to delete the password and restart the receiver?'), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Do you want to delete the decoder Password?'))

    def restartGUI(self, answer):
        if answer is True:
            os.system('passwd -d root')
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

class SetPasswdMain(Screen, ConfigListScreen):
	skin = """
		<screen position="center,center" size="800,600" title="Set Root Password" flags="wfNoBorder" >
		<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ChangeRootPassword/backg.png" position="0,0" size="800,600" alphatest="on" />
		<widget name="config" position="100,200" zPosition="1" size="600,60" scrollbarMode="showOnDemand" transparent="1" />
	</screen>"""

	def __init__(self, session):
		Screen.__init__(self, session)
		
		self.skin = SetPasswdMain.skin
		self.list = []
		ConfigListScreen.__init__(self, self.list)
		self["lab1"] = Label(_("OPENBOX"))
		self["lab2"] = Label(_("Access Password Center"))
		self["lab3"] = Label(_("Password Center"))
		self["key_red"] = Label(_("Change"))
		self["key_green"] = Label(_("Generate"))
		self["key_blue"] = Label(_("Cancel"))

		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"red": self.DoConnectPass,
			"green": self.greenPressed,
			"blue": self.close,
			"cancel": self.close
		}, -1)
	
		self.newpass = self.buildPass()
		self.oldp = NoSave(ConfigText(fixed_size = False, default = ""))
		self.newp = NoSave(ConfigText(fixed_size = False, default = self.newpass))
		self.updateList()
	
	def updateList(self):
		self.list = []
		self.list.append(getConfigListEntry(_('Enter old passwd'), self.oldp))
		self.list.append(getConfigListEntry(_('Enter new passwd'), self.newp))
		self["config"].list = self.list
		self["config"].l.setList(self.list)
		
	def buildPass(self):
		passwd = string.letters + string.digits
		return ''.join(Random().sample(passwd, 8)) 

	def greenPressed(self):
		self.newp.value = self.buildPass()
		self.updateList()
		
	def yellowPressed(self):
		sel = self["config"].getCurrent()
		value = self.oldp.value
		self.valuetype = 0
		if sel[0] == "Enter new Password":
			value = self.newp.value
			self.valuetype = 1	
		self.session.openWithCallback(self.virtualKeybDone, VirtualKeyBoard, title=sel[0], text=value)
		
	
	def virtualKeybDone(self, passw):
		if self.valuetype == 0:
			self.oldp.value = passw
		else:
			self.newp.value = passw
		self.updateList()

	def DoConnectPass(self):
		self.session.open(SetPasswdDo, self.oldp.value, self.newp.value)


class SetPasswdDo(Screen):
	skin = """
		<screen position="center,center" size="700,424" title="Set Root Password" flags="wfNoBorder" >
			<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/ChangeRootPassword/backg2.png" position="0,0" size="700,424" alphatest="on" />
			<widget name="lab" position="40,20" size="620,384" font="Regular;20" zPosition="1" transparent="1" />
		</screen>"""

	def __init__(self, session, oldp, newp):
		Screen.__init__(self, session)
				
		self["lab"] = Label("")
		self["actions"] = ActionMap(["WizardActions"],
			{
				"ok": self.end,
				"back": self.end,
			}, -1)
		
		self.oldp = oldp
		self.newp = newp
		self.connected = True
		self.connect()
		
	def connect(self):
		tn = Telnet("localhost")
		out = tn.read_until("login:", 3)
		tn.write("root\n")
		check = tn.read_until("Password:", 2)
		out += check
		if check.__contains__("Password:"):
			tn.write(self.oldp + "\n")
			check = tn.read_until("~#", 2)
			out += check
		if check.__contains__("~#"):
			tn.write("passwd\n")
			out += tn.read_until("password", 2)
			tn.write(self.newp + "\n")
			out += tn.read_until("password", 2)
			tn.write(self.newp + "\n")
			out += tn.read_until("xxx", 1)
			tn.write("exit\n")
			out += tn.read_all()
		else:
			out += "\nLogin incorrect, wrong password."
			tn.close()
		
		self.connected = False
		self["lab"].setText(out)
	
	def end(self):
		if self.connected == False:
			self.close()
