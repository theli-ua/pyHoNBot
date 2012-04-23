import os
import pickle
from time import sleep

class ConfigClass(object):
    def __init__(self,config,defaults,disk_config_path):
        self.config = config
        self.defaults = defaults
        self.disk_config_path = disk_config_path
        if os.path.exists(disk_config_path):
            self.disk_config = pickle.load(open(disk_config_path,'r'))
        else:
            self.disk_config = {}

    def dump(self):
        pickle.dump(self.disk_config,open(self.disk_config_path,'w'))

    def doc(self,item):
        return self.defaults[item][1]

    def __getattr__(self,item):
        if item in ['config','disk_config','defaults','disk_config_path']:
            raise AttributeError, item
        if hasattr(self.config,item):
            return getattr(self.config,item)
        elif item in self.disk_config:
            return self.disk_config[item]
        elif item in self.defaults:
            return self.defaults[item][0]
        else:
            return None

    def module_config(self,key,value):
        self.defaults[key] = value

    def set(self,item,value):
        if isinstance(self.defaults[item][0],int):
            value = int(value)
        elif isinstance(self.defaults[item][0],list) and not isinstance(value,list):
            return
        self.disk_config[item] = value
        self.dump()


    def set_del(self,item,value):
        cur = set(self.__getattr__(item))
        cur -= set([value])
        self.set(item,list(cur))

    def set_add(self,item,value):
        cur = set(self.__getattr__(item))
        cur |= set([value])
        self.set(item,list(cur))

    def info(self):
        return str(self.defaults.keys())

def setup(bot):
    _config_path = os.path.splitext(bot.config.__file__)[0] + 'db'

    default_config = {
            # 'key' : ['default_value' , 'doc'],
            'officer_admin' : [1 , "If set bot's clan officers/leaders will be treated as admins"],
            'cooldown'      : [3 , "Per-user cooldown in seconds"],
            'channel_cooldown': [30, "Channel answer cooldown"],
            'channels'      : [[], "Set of channels to join, use part/join commands to conveniently modify it"],
            'admins'        : [[bot.config.owner], "Set of nicks for admin status, use admin add/del commands to conveniently modify it"],
            'ignore'        : [[], "Set of nicks to ignore. Use ignore add/dell to modify"],
            'banlist'       : [[], "Set of nicks to ban on sight. Use ban/unban to modify"],
            }

    bot.config = ConfigClass(bot.config,default_config,_config_path)

def config(bot,input):
    """ config - list config keys, config key - show doc and value, config key value - set key to value, whisper to set global(will be set for channel otherwise) """
    if not input.admin:
        return
    if not input.group(2):
        bot.say(bot.config.info())
    else:
        try:
            key,value = input.group(2).split(' ',1)
            bot.config.set(key,value)
            bot.reply('OK')
        except:
            key = input.group(2)
            msg = '{0},{1}'.format(bot.config.doc(key),bot.config.__getattr__(key))
            for line in [msg[i:i+245] for i in range(0, len(msg), 245)]:
                bot.say(line)
                sleep(1)
    
config.commands = ['config']
            
