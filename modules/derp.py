from random import randint
from hon.packets import ID
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
    if not hasattr( bot, 'stringtables' ):
    	bot.say("Derp")
    	return
    bot.say (bot.stringtables[ derps[ randint( 0, len( derps ) - 1 ) ] ].replace( "\n", " " ) )
derp.commands = ['derp']

def roll(bot, input):
	if not input.admin:
		return
	if not input.group(2):
		return
	if input.origin[0] == ID.HON_SC_CHANNEL_MSG:
		bot.write_packet(ID.HON_CS_CHANNEL_ROLL, input.group(2), input.origin[2])
	else:
		chan = input.group(3)
		if chan is not None:
			if chan.lower() in bot.chan2id:
				chan = bot.chan2id[chan.lower()]
			else:
				chan = None
		elif input.origin[0] == ID.HON_SC_CHANNEL_MSG:
			chan = input.origin[2]
		if chan is not None:
			bot.write_packet(ID.HON_CS_CHANNEL_ROLL, input.group(2), chan)
roll.rule = (['roll'],'(.*?)\\ "([a-zA-Z\\ ]+)"')