# -*- coding: utf-8 -*-
from Screens.Screen import Screen
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.Console import Console as iConsole
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Components.Language import language
from Tools.LoadPixmap import LoadPixmap
import os
import enigma
from Plugins.SystemPlugins.SoftwareManager.BackupRestore import BackupScreen, RestoreScreen, BackupSelection, getBackupPath, getBackupFilename
from Screens.MessageBox import MessageBox
from Components.Console import Console as iConsole

	
class asistente_openbox(Screen):

	skin = """
		<screen position="center,center" size="1000,600" backgroundColor="white" title="Asistente OpenBox" >
		<widget source="header" render="Label" position="200,30" size="700,300" foregroundColor="black" backgroundColor="white" font="Regular; 40" halign="left" transparent="1" />
		<widget source="contenido" render="Label" position="200,200" size="700,300" foregroundColor="#848484" backgroundColor="white" font="Regular; 30" halign="left" transparent="1" />
		<eLabel name="line" position="200,490" size="750,1" backgroundColor="#aba7a6" />
		<ePixmap name="menu" position="5,5" size="158,600" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/menu.png" zPosition="-5" />
		<ePixmap name="continuar" position="750,520" size="230,61" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/green.png" zPosition="-5" />
		<ePixmap name="salir" position="190,520" size="230,61" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/red.png" zPosition="-5" />
		<widget source="key_green" render="Label" position="770,530" size="200,50" zPosition="1" font="Regular; 30" transparent="1" foregroundColor="white" noWrap="1" />
		<widget source="key_red" render="Label" position="270,530" size="200,50" zPosition="1" font="Regular; 30" transparent="1" foregroundColor="white" noWrap="1" />
		<ePixmap name="ayuda" position="470,520" size="230,61" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/blue.png" zPosition="-5" />
<widget source="key_blue" render="Label" position="520,530" size="200,50" zPosition="1" font="Regular; 30" transparent="1" foregroundColor="white" noWrap="1" />
		</screen>"""

	
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = "asistente_openbox"
		self.setTitle(_("Asistente Instalacion OpenBox"))
		self.indexpos = None
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
		{
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			"blue": self.informacion,
			"green": self.backup,
			
			
		})

		self["key_red"] = StaticText(_("Cancelar"))
		self["key_blue"] = StaticText(_("Ayuda"))
		self["key_green"] = StaticText(_("Continuar"))
		self["header"] = StaticText(_("Bienvenido al Asistente de Instalacion Imagen OpenBox"))
		self["contenido"] = StaticText(_("Has accedido al asistente de instalacion de imagen OpenBox, para proceder a la actualizacion de su receptor a traves de imagen ubicada en unidad montada, pulse <CONTINUAR> si estas seguro, o de lo contrario pulse <CANCELAR>"))
		
	def exit(self):
		self.close()

			
	def backup(self):
		self.session.open(backup)

	def informacion(self):
		self.session.open(ayuda)

######################################################################################

class backup(Screen):

	skin = """
		<screen position="center,center" size="1000,600" backgroundColor="white" title="Asistente OpenBox" >
		<widget source="header" render="Label" position="200,30" size="700,300" foregroundColor="black" backgroundColor="white" font="Regular; 40" halign="left" transparent="1" />
		<widget source="contenido" render="Label" position="200,160" size="700,300" foregroundColor="#848484" backgroundColor="white" font="Regular; 30" halign="left" transparent="1" />
		<eLabel name="line" position="200,490" size="750,1" backgroundColor="#aba7a6" />
		<ePixmap name="menu" position="5,5" size="158,600" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/menu.png" zPosition="-5" />
		<ePixmap name="continuar" position="750,520" size="230,61" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/green.png" zPosition="-5" />
		<ePixmap name="salir" position="190,520" size="230,61" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/red.png" zPosition="-5" />
		<widget source="key_green" render="Label" position="770,530" size="200,50" zPosition="1" font="Regular; 30" transparent="1" foregroundColor="white" noWrap="1" />
		<widget source="key_red" render="Label" position="270,530" size="200,50" zPosition="1" font="Regular; 30" transparent="1" foregroundColor="white" noWrap="1" />
		<ePixmap name="ayuda" position="470,520" size="230,61" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/blue.png" zPosition="-5" />
<widget source="key_blue" render="Label" position="505,530" size="200,50" zPosition="1" font="Regular; 30" transparent="1" foregroundColor="white" noWrap="1" />
		</screen>"""
	
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = "backup"
		self.setTitle(_("Asistente Instalacion OpenBox"))
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
		{
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			"blue": self.selebackup,
			"green": self.paso2,
			
			
		})
		self["header"] = StaticText(_("Realizar copia de Seguridad de la configuracion de nuestro Receptor"))
		self["contenido"] = StaticText(_("Antes de proceder a la instalacion Imagen, tienes la posibilidad de realizar una copia de seguridad de archivos de configuracion de su receptor, pulse <SELECCION> para seleccionar los archivos a copiar, si lo desea pulse boton <CONTINUAR> para seguir con el asistente, o puedes optar por pulsar <CANCELAR> para no continuar"))
		self["key_red"] = StaticText(_("Cancelar"))
		self["key_blue"] = StaticText(_("Seleccion"))
		self["key_green"] = StaticText(_("Continuar"))
		
	def exit(self):
		self.close()

	def paso2(self):
		self.session.openWithCallback(self.backupDone,BackupScreen, runBackup = True)
		
	def selebackup(self):
		self.session.open(BackupSelection)
		

	def backupDone(self,retval = None):
		if retval is True:
			self.session.open(paso2)
		else:
			self.session.open(MessageBox, _("Backup failed."), MessageBox.TYPE_INFO, timeout = 10)

	def startRestore(self, ret = False):
		if (ret == True):
			self.exe = True
			self.session.open(RestoreScreen, runRestore = True)

class paso2(Screen):

	skin = """
		<screen position="center,center" size="1000,600" backgroundColor="white" title="Asistente OpenBox" >
		<widget source="header" render="Label" position="200,30" size="700,300" foregroundColor="black" backgroundColor="white" font="Regular; 40" halign="left" transparent="1" />
		<widget source="contenido" render="Label" position="200,200" size="700,300" foregroundColor="#848484" backgroundColor="white" font="Regular; 30" halign="left" transparent="1" />
		<eLabel name="line" position="200,490" size="750,1" backgroundColor="#aba7a6" />
		<ePixmap name="menu" position="5,5" size="158,600" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/menu.png" zPosition="-5" />
		<ePixmap name="continuar" position="750,520" size="230,61" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/green.png" zPosition="-5" />
		<ePixmap name="salir" position="190,520" size="230,61" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/red.png" zPosition="-5" />
		<widget source="key_green" render="Label" position="770,530" size="200,50" zPosition="1" font="Regular; 30" transparent="1" foregroundColor="white" noWrap="1" />
		<widget source="key_red" render="Label" position="270,530" size="200,50" zPosition="1" font="Regular; 30" transparent="1" foregroundColor="white" noWrap="1" />
		</screen>"""
	
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = "asistente_openbox"
		self.setTitle(_("Asistente Instalacion OpenBox"))
		self.indexpos = None
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
		{
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			"green": self.paso4,
			
			
		})
		self["header"] = StaticText(_("El asistente de copia seguridad de nuestra imagen ha finalizado"))
		self["contenido"] = StaticText(_("Se ha creado copia seguridad de configuracion en unidad montada, dentro de carpeta <BACKUP>, ahora vamos a realizar el ultimo paso, ahora debe pulsar <TERMINAR> y accedera a las imagenes en .zip que tenga en sus unidades montadas, para asi realizar la instalacion, si no lo desea pulse <CANCELAR>"))
		self["key_red"] = StaticText(_("Cancelar"))
		self["key_green"] = StaticText(_("Terminar"))
		
	def exit(self):
		self.close()

	def paso4(self):
		from Screens.FlashImage import SelectImage
		self.session.open(SelectImage)
		


class ayuda(Screen):

	skin = """
		<screen position="center,center" size="1000,600" backgroundColor="white" title="Asistente OpenBox" >
		<widget source="header" render="Label" position="200,30" size="700,300" foregroundColor="black" backgroundColor="white" font="Regular; 40" halign="left" transparent="1" />
		<widget source="contenido" render="Label" position="200,200" size="700,300" foregroundColor="#848484" backgroundColor="white" font="Regular; 30" halign="left" transparent="1" />
		<eLabel name="line" position="200,490" size="750,1" backgroundColor="#aba7a6" />
		<ePixmap name="menu" position="5,5" size="158,600" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/menu.png" zPosition="-5" />
		<ePixmap name="salir" position="190,520" size="230,61" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/asistenteopenbox/red.png" zPosition="-5" />
		<widget source="key_red" render="Label" position="270,530" size="200,50" zPosition="1" font="Regular; 30" transparent="1" foregroundColor="white" noWrap="1" />
		<widget source="HardwareLabel" render="Label" position="460,135" zPosition="2" size="180,22" font="Regular;20" halign="right" valign="center" backgroundColor="background" foregroundColor="#03307dc3" transparent="1" />
		<widget source="Hardware" render="Label" position="675,135" zPosition="2" size="390,22" font="Regular;20" halign="left" valign="center" backgroundColor="background" foregroundColor="foreground" transparent="1" />
		
		</screen>"""

	
	def __init__(self, session):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = "asistente_openbox"
		self.setTitle(_("Asistente Instalacion OpenBox"))
		self.indexpos = None
		self["shortcuts"] = ActionMap(["ShortcutActions", "WizardActions"],
		{
			"cancel": self.exit,
			"back": self.exit,
			"red": self.exit,
			
			
			
		})

		self["key_red"] = StaticText(_("Cancelar"))
		self["header"] = StaticText(_("Ayuda sobre Asistente configuracion Receptor"))
		self["contenido"] = StaticText(_("La utilidad Asistente instalacion Openbox tiene la finalidad poder realizar una instalacion de imagen en nuestro receptor de manera guiada, realizando copia seguridad, debe tener la imagen con extension <<.zip>> en una unidad montada, por lo que debe tener montado un usb o disco duro para la realizacion del backup"))
		
		
		
	def exit(self):
		self.close()

			
	
	

def main(session, **kwargs):
	session.open(asistente_openbox)
	
######################################################################################
def sessionstart(reason,session=None, **kwargs):
	if reason == 0:
		pTools.gotSession(session)
######################################################################################

def Plugins(**kwargs):
	list = [PluginDescriptor(name=_("Asistente Instalacion OpenBox"), description=_("Actualizar imagen con Asistente Instalacion"), where = [PluginDescriptor.WHERE_PLUGINMENU], icon="asistente.png", fnc=main)]
	
	return list
