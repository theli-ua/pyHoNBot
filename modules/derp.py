from random import randint
depend = ['honstringtables']
derps = []
def setup(bot):
    global derps
    derps = []
    if not hasattr(bot,'stringtables'):
        return
    for k,v in bot.stringtables.iteritems():
        if k.endswith('_flavor') and k.startswith('Ability') and len(v.strip()) > 0 and v.strip() != 'None':
            derps.append(k)


def derp(bot,*args):
    """Derp"""
    bot.say(bot.stringtables[derps[randint(0,len(derps) - 1)]])
derp.commands = ['derp']
