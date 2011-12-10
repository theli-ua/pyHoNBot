import os
import sys
import tempfile
from datetime import timedelta

from hon.honutils import normalize_nick
from hon.packets import ID

import Ice
import IcePy

_server = None
_meta = None
def setup(bot):
    global _server,_meta
    if not hasattr(bot.config,'mumble_host') or not hasattr(bot.config,"mumble_port"):
        return
    prxstr = "s/1 -t:tcp -h %s -p %d -t 1000" % (bot.config.mumble_host,bot.config.mumble_port)
    meta_prxstr = "Meta:tcp -h %s -p %d -t 1000" % (bot.config.mumble_host,bot.config.mumble_port)
    props = Ice.createProperties()
    props.setProperty("Ice.ImplicitContext", "Shared")
    idata = Ice.InitializationData()
    idata.properties = props
    ice = Ice.initialize(idata)
    prx = ice.stringToProxy(prxstr)
    prx_meta = ice.stringToProxy(meta_prxstr)
    try:
        slice = IcePy.Operation('getSlice', Ice.OperationMode.Idempotent, Ice.OperationMode.Idempotent, True, (), (), (), IcePy._t_string, ()).invoke(prx_meta, ((), None))
        (dynslicefiledesc, dynslicefilepath)  = tempfile.mkstemp(suffix = '.ice')
        dynslicefile = os.fdopen(dynslicefiledesc, 'w')
        dynslicefile.write(slice)
        dynslicefile.flush()
        Ice.loadSlice('', ['-I' + Ice.getSliceDir(), dynslicefilepath])
        dynslicefile.close()
        os.remove(dynslicefilepath)

        import Murmur
        if hasattr(bot.config,'mumble_secret'):
            ice.getImplicitContext().put("secret", bot.config.mumble_secret)
        _server = Murmur.ServerPrx.checkedCast(prx)
        _meta = Murmur.MetaPrx.checkedCast(prx_meta)
        bot.mumbleannounce = lambda msg: _server.sendMessageChannel(0,True,msg)
    except Exception, e:
        print str(e)

def mumble(bot,input):
    if input.account_id not in bot.clan_roster:
        return
    global _server,_meta
    if not _meta or not _server:
        return
    command = input.group(2)
    if not command:
        #uptime, users
        uptime = _meta.getUptime()
        uptime = str(timedelta(seconds=uptime))
        usernames = [u.name for u in _server.getUsers().values()]
        msg = 'uptime: {0}, online [{1}]'.format(uptime,','.join(usernames))
        bot.say(msg)
    elif command == 'info':
        conf = _meta.getDefaultConf()
        msg = '{0}:{1},password "{2}"'.format(bot.config.mumble_host,conf['port'],conf['password'])
        bot.write_packet(ID.HON_SC_WHISPER,input.nick,msg)
        



mumble.commands = ['mumble']
