import os
from Tools.HardwareInfo import HardwareInfo
from Tools.Directories import SCOPE_SKIN, resolveFilename

class RcModel:
    RcModels = {}

    def __init__(self):
        self.model = HardwareInfo().get_device_model()
        self.device_name = open('/etc/hostname').read().strip()
		# cfg files has modelname  rcname entries.
		# modelname is boxname optionally followed by .rctype	   
        for line in open(resolveFilename(SCOPE_SKIN, 'rc_models/rc_models.cfg'), 'r'):
            if line.startswith(self.model):
                m, r = line.strip().split()
                self.RcModels[m] = r

    def rcIsDefault(self):
		# Default RC can only happen with DMM type remote controls...															   
        return self.model.startswith('dm')

    def getRcFile(self, ext):
		# check for rc/type every time so rctype changes will be noticed																  
        if os.path.exists('/proc/stb/ir/rc/type'):
            rc = open('/proc/stb/ir/rc/type').read().strip()
            modeltype = '%s.%s' % (self.model, rc)
        else:
            modeltype = None
        if modeltype is not None and modeltype in self.RcModels.keys():
            remote = self.RcModels[modeltype]
        elif self.model in self.RcModels.keys():
            remote = self.RcModels[self.model]
        else:
            remote = 'dmm'
        f = resolveFilename(SCOPE_SKIN, 'rc_models/' + remote + '.' + ext)
        if self.device_name.startswith('xpeedlx3'):
            f = resolveFilename(SCOPE_SKIN, 'rc_models/xpeedlx3.' + ext)
        elif self.device_name.startswith('atemionemesis'):
            f = resolveFilename(SCOPE_SKIN, 'rc_models/atemionemesis.' + ext)
        elif self.device_name.startswith('sezammarvel'):
            f = resolveFilename(SCOPE_SKIN, 'rc_models/sezammarvel.' + ext)
        elif self.device_name.startswith('mbultra'):
            f = resolveFilename(SCOPE_SKIN, 'rc_models/mbultra.' + ext)
        elif self.device_name.startswith('ventonhdx'):
            f = resolveFilename(SCOPE_SKIN, 'rc_models/ventonhdx.' + ext)
        elif self.device_name.startswith('mbmini'):
            f = resolveFilename(SCOPE_SKIN, 'rc_models/mbmini.' + ext)
        elif self.device_name.startswith('dinobot4kse'):
            f = resolveFilename(SCOPE_SKIN, 'rc_models/dinobot4kse.' + ext)			
        elif not os.path.exists(f):
            f = resolveFilename(SCOPE_SKIN, 'rc_models/dmm.' + ext)
        return f

    def getRcImg(self):
        return self.getRcFile('png')

    def getRcPositions(self):
        return self.getRcFile('xml')


rc_model = RcModel()