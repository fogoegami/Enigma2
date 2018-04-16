#!/usr/bin/python
##by mfaraj57 https://www.tunisia-sat.com/forums/forums/272/
from Plugins.Plugin import PluginDescriptor
plugin_path='/usr/lib/enigma2/python/Plugins/Extensions/NetSpeedTest'



def main(session,**kwargs):

    from default import NetSpeedTestScreen
    session.open(NetSpeedTestScreen)
    
def speedSetup(menuid, **kwargs):
	if menuid == "information":
		return [(_("Test Conexion a Internet"), main, "Net_speed", None)]
	else:
		return []

def Plugins(**kwargs):
	return PluginDescriptor(name="NetSpeedTest", description="Test your net speed", where = PluginDescriptor.WHERE_MENU, needsRestart = False, fnc=speedSetup)

