# Embedded file name: /usr/lib/enigma2/python/Plugins/Extensions/TunerServer/plugin.py
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Network import iNetwork
from Tools.Directories import fileExists
from enigma import eServiceCenter, eServiceReference, eTimer
from shutil import rmtree, move, copy
from Components.Sources.List import List
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry, ConfigNumber, ConfigText, ConfigSelection, ConfigSubsection, configfile, NoSave
import os

config.streamservice = ConfigSubsection()
config.streamservice.streamport = ConfigNumber(default = "8001")
config.streamservice.streampass = ConfigText(default = "openbox",fixed_size = False, visible_width=30)

def testlista():
    lista = 'No Montaje encontrado'
    if os.path.ismount('/media/hdd'):
        lista = '/media/hdd/tuner/'
    elif os.path.ismount('/media/usb'):
        lista = '/media/usb/tuner/'
    return lista

class TunerServer(ConfigListScreen, Screen):
    skin = """
	<screen position="center,center" size="800,505" >
		<widget name="lab1" position="10,4" size="780,400" font="Regular;20" transparent="0"/>
		<widget name="lab2" position="10,400" size="300,30" font="Regular;20" valign="center" halign="right" transparent="0"/>
		<widget name="labstop" position="320,400" size="260,30" font="Regular;20" valign="center" halign="center" backgroundColor="red"/>
		<widget name="labrun" position="320,400" size="260,30" zPosition="1" font="Regular;20" valign="center" halign="center" backgroundColor="green"/>
		<ePixmap pixmap="skin_default/buttons/red.png" position="95,450" size="140,40" alphatest="on"/>
		<ePixmap pixmap="skin_default/buttons/green.png" position="330,450" size="140,40" alphatest="on"/>
		<ePixmap pixmap="skin_default/buttons/yellow.png" position="565,450" size="140,40" alphatest="on" />
		<widget name="key_red" position="95,450" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#9f1313" transparent="1"/>
		<widget name="key_green" position="330,450" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#1f771f" transparent="1"/>
		<widget name="key_yellow" position="565,450" zPosition="1" size="140,40" font="Regular;18" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />
	</screen>"""

    def __init__(self, session):
        Screen.__init__(self, session)
        Screen.setTitle(self, _('Tuner Server setup'))
        mytext = '\nThis plugin implements the Tuner Server feature included. It will allow you to share the tuners of this box with another STB, PC and/or another compatible device in your home network.\nThe server will build a virtual channels list in the folder /media/hdd/tuner or /media/usb/tuner on this box.\nYou can access the tuner(s) of this box from clients on your internal lan using nfs, cifs, UPnP or any other network mountpoint.\nThe tuner of the server (this box) has to be avaliable. This means that if you have ony one tuner in your box you can only stream the channel you are viewing (or any channel you choose if your box is in standby).\nRemember to select the correct audio track in the audio menu if there is no audio or the wrong language is streaming.\nNOTE: The server is built, based on your current ip and the current channel list of this box. If you change your ip or your channel list is updated, you will need to rebuild the server database.\n\n\t\t'
        self['lab1'] = Label(_(mytext))
        self['lab2'] = Label(_('Current Status:'))
        self['labstop'] = Label(_('Server Disabled'))
        self['labrun'] = Label(_('Server Enabled'))
        self['key_red'] = Label(_('close'))
        self['key_green'] = Label(_('Enable Server'))
        self['key_yellow'] = Label(_('Disable Server'))
        self['versionlista'] = Label(_('%s') % testlista())
        self['lab3'] = Label(_('Ubicacion montaje para tuner:'))
        self.my_serv_active = False
        self.ip = '0.0.0.0'
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'ok': self.close,
         'back': self.close,
         'red': self.close,
         'green': self.ServStart,
         'yellow': self.ServStop})
        self.list = []
        self.list.append(getConfigListEntry(_("Stream Tuner port"), config.streamservice.streamport))
        self.list.append(getConfigListEntry(_("Stream Password"), config.streamservice.streampass))
        ConfigListScreen.__init__(self, self.list)
        self["config"].list = self.list
        self.activityTimer = eTimer()
        self.activityTimer.timeout.get().append(self.doServStart)
        self.onClose.append(self.delTimer)
        self.onLayoutFinish.append(self.updateServ)
        
    def ServStart(self):
        if os.path.ismount('/media/hdd'):
            self['lab1'].setText(_('Your server is now building hdd \nPlease wait ...'))
            self.activityTimer.start(10)
        elif os.path.ismount('/media/usb'):
            self['lab1'].setText(_('Your server is now building USB \nPlease wait ...'))
            self.activityTimer.start(10)
        else:
            self.session.open(MessageBox, _("Sorry, but you need to have a device mounted at '/media/hdd' or 'media/usb'"), MessageBox.TYPE_INFO)

    def doServStart(self):
        self.activityTimer.stop()

        if os.path.ismount('/media/hdd'):
            folder = '/media/hdd/tuner'
        elif os.path.ismount('/media/usb'):
            folder = '/media/usb/tuner'

        if os.path.exists(folder):
            rmtree(folder)
        ifaces = iNetwork.getConfiguredAdapters()
        for iface in ifaces:
            ip = iNetwork.getAdapterAttribute(iface, 'ip')
            ipm = '%d.%d.%d.%d' % (ip[0],
             ip[1],
             ip[2],
             ip[3])
            if ipm != '0.0.0.0':
                self.ip = ipm

        os.mkdir(folder, 0755)
        s_type = '1:7:1:0:0:0:0:0:0:0:(type == 1) || (type == 17) || (type == 22) || (type == 25) || (type == 134) || (type == 195)'
        serviceHandler = eServiceCenter.getInstance()
        services = serviceHandler.list(eServiceReference('%s FROM BOUQUET "bouquets.tv" ORDER BY bouquet' % s_type))
        bouquets = services and services.getContent('SN', True)
        count = 1
        for bouquet in bouquets:
            self.poPulate(bouquet, count, folder)
            count += 1

        mytext = "Server avaliable on ip %s\nTo access this box's tuners you can connect via Lan or UPnP.\n\n1) To connect via lan you have to mount the /media/hdd or /media/usb folder of this box in the client /media/hdd folder. Then you can access the tuners server channel list from the client Media player -> Harddisk -> tuner.\n2) To connect via UPnP you need an UPnP server that can manage .m3u files like Mediatomb." % self.ip
        self['lab1'].setText(_(mytext))
        self.session.open(MessageBox, _('Build Complete!'), MessageBox.TYPE_INFO)
        self.updateServ()

    def poPulate(self, bouquet, count, folder):
        config.streamservice.streamport.save()
        config.streamservice.streampass.save()
        configfile.save()
        n = '%03d_' % count
        name = n + self.cleanName(bouquet[1])
        path = folder
        serviceHandler = eServiceCenter.getInstance()
        services = serviceHandler.list(eServiceReference(bouquet[0]))
        channels = services and services.getContent('SN', True)
 
        
        for channel in channels:
            if not int(channel[0].split(':')[1]) & 64:
                filename = path + "/" + n + self.cleanName(bouquet[1]) + ".m3u"
                try:
                    out = open(filename, 'a')
                except:
                    continue

                out.write('#EXTM3U\n')
                out.write('#EXTINF:-1,' + channel[1] + '\n')
                out.write('http://' + 'root' + ':' + str(config.streamservice.streampass.value) + '@' + self.ip + ':' + str(config.streamservice.streamport.value) + '/' + channel[0] + '\n\n')
                out.close()
                

    def cleanName(self, name):
        name = name.replace(' ', '_')
        name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
        name = name.replace('.', '_')
        name = name.replace('<', '')
        name = name.replace('<', '')
        name = name.replace('/', '')
        return name

    def ServStop(self):
        if self.my_serv_active == True:
            self['lab1'].setText(_('Your server is now being deleted\nPlease Wait ...'))

            if os.path.ismount('/media/hdd'):
                folder = '/media/hdd/tuner'
            elif os.path.ismount('/media/usb'):
                folder = '/media/usb/tuner'

            if os.path.exists(folder):
                rmtree(folder)
            mybox = self.session.open(MessageBox, _('Tuner Server Disabled.'), MessageBox.TYPE_INFO)
            mybox.setTitle(_('Info'))
            self.updateServ()
        self.session.open(MessageBox, _('Server now disabled!'), MessageBox.TYPE_INFO)

    def updateServ(self):
        self['labrun'].hide()
        self['labstop'].hide()
        self.my_serv_active = False

        if os.path.ismount('/media/hdd'):
            folder = '/media/hdd/tuner'
        elif os.path.ismount('/media/usb'):
            folder = '/media/usb/tuner'

        if os.path.isdir(folder):
            self.my_serv_active = True
            self['labstop'].hide()
            self['labrun'].show()
        else:
            self['labstop'].show()
            self['labrun'].hide()

    def delTimer(self):
        del self.activityTimer


def settings(menuid, **kwargs):
    if menuid == 'network':
        return [(_('Tuner Server setup'),
          main,
          'tuner_server_setup',
          None)]
    else:
        return []



