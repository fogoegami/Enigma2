# 2016.09.18 10:47:13 Jerusalem Daylight Time
PLUGIN_PATH='/usr/lib/enigma2/python/Plugins/Extensions/NetSpeedTest'
from Screens.Screen import Screen
from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Tools.Directories import copyfile, fileExists
from enigma import getDesktop
from Plugins.Plugin import PluginDescriptor
import os
from Screens.Standby import TryQuitMainloop
from enigma import eConsoleAppContainer
class NetSpeedTestScreen(Screen):
 

    
    skin = '''  <screen name="NetSpeedTestScreen"  backgroundColor="#380038" position="center,center" size="900,520" title="Net Speed Test"   >
                <ePixmap position="0,0"  size="900,520" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/NetSpeedTest/logo.png"     zPosition="1" transparent="1" alphatest="blend" />
                <widget name="data" position="155,59" zPosition="4" size="610,243" font="Regular;21" foregroundColor="#76addc" transparent="1" halign="left" valign="top" />
                <widget name="ping" position="190,29" zPosition="4" size="157,40" font="Regular;21" foregroundColor="white" transparent="1" halign="left" valign="top" />
                <widget name="host" position="673,453" zPosition="4" size="196,56" font="Regular;21" foregroundColor="white" transparent="1" halign="left" valign="top" />
                <widget name="ip" position="63,452" zPosition="4" size="204,53" font="Regular;21" foregroundColor="white" transparent="1" halign="left" valign="top" />
                <widget name="download" position="398,30" zPosition="4" size="156,53" font="Regular;21" foregroundColor="white" transparent="1" halign="left" valign="top" />
                <widget name="upload" position="597,30" zPosition="4" size="161,53" font="Regular;21" foregroundColor="white" transparent="1" halign="left" valign="top" />
                                                       
		</screen>'''
             
    def __init__(self, session):
        Screen.__init__(self, session)
        self.color = '#800080'
        
        self['data'] = Label("Testing net speed,please wait......")
        self['ping'] = Label(" ")
        self['host'] = Label(" ")
        self['ip'] = Label(" ")
        self['download'] = Label(" ")

        self['upload'] = Label(" ")
        self['actions'] = ActionMap(['OkCancelActions','ColorActions'],{'cancel': self.exit,'green': self.testagain}, -1)
        
        cmd="python "+PLUGIN_PATH+"/speedtest.py"
        self.finished=False
        self.data=''
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.action)
        self.container.dataAvail.append(self.dataAvail)
        
        self.container.execute(cmd)
    def testagain(self):
        if  self.finished==False:
            return
        self['data'].setText("Testing net speed......")
        self['ping'].setText("")
        cmd="python "+PLUGIN_PATH+"/speedtest.py"
        self.container.execute(cmd)
    def action(self, retval):
        print "retval",retval
        print "finished test"
        self.finished=True
    def dataAvail(self, rstr):
            
            if rstr:
               
                self.data=self.data+rstr
                parts=rstr.split("\n")
                for part in parts:
                    if 'Hosted by' in part:
                        try:host=part.split("Hosted by")[1].split("[")[0].strip()
                        except:host=''
                        self['host'].setText(str(host))
                    if 'Testing from' in part:
                        ip=part.split("Testing from")[1].split(")")[0].replace("(","").strip()
                        self['ip'].setText(str(ip))                        
                if  "Ping" in rstr:
                    
                    try:ping =rstr.split("Ping")[1].split("\n")[0].strip()
                    except:ping=''
                    
                   
                    self['ping'].setText(str(ping))
                    
                if  "Download:" in rstr:
                    
                    try:download =rstr.split(":")[1].split("\n")[0].strip()
                    except:download =''
                    
                    self['download'].setText(str(download))
                    self.data=''
                    self.data='Testing upload speed....'    
                if  "Upload:" in rstr:
                   
                    try:upload =rstr.split(":")[1].split("\n")[0].strip()
                    except:upload =''
                    
                    self['upload'].setText(str(upload))
                    self['data'].setText(" Test completed,to test again press green")
                    return
                       
                    
                self['data'].setText(self.data)
                
                                
               
                     
                     
                
    def exit(self):
        
            self.container.appClosed.remove(self.action)
            self.container.dataAvail.remove(self.dataAvail)
            self.close()


    def updateTitle(self):
        self.newtitle='Net speed test'
        self.setTitle(self.newtitle)

