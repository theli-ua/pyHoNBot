from urllib import urlopen
import json
import time
from hon.packets import ID

lastAnnounced = {}

def on_user_status(bot, origin, data):
	currTime = time.mktime(time.gmtime())
	if currTime > (bot.lastStream + bot.config.stream_interval):
		bot.lastStream = currTime
		GetOnlineStreams(bot)
on_user_status.event = [ID.HON_SC_UPDATE_STATUS, ID.HON_SC_JOINED_CHANNEL]
on_user_status.thread = True

def streams(bot, input):
	out = "Online Streams: "
	if len(bot.upStreams) == 0:
		out += "None."
	else:
		for stream in bot.upStreams:
			out += "{0}, ".format(stream)
	bot.reply(out)
streams.commands = ['streams']

def addstream(bot, input):
	"""Add a stream from the notify list"""
	if not input.admin: return False
	if not input.group(2): return
	stream = input.group(2).lower()
	if not stream in bot.config.streams:
		bot.config.set_add('streams', stream)
		bot.reply("Added {0} to stream list".format(stream))
	else:
		bot.reply("{0} is already in the stream list".format(stream))
addstream.commands = ['addstream']

def delstream(bot, input):
	"""Delete a stream from the notify list"""
	if not input.admin: return False
	if not input.group(2): return
	stream = input.group(2).lower()
	if stream in bot.config.streams:
		bot.config.set_del('streams', stream)
		bot.reply("Removed {0} from the stream list".format(stream))
		for k, v in enumerate(bot.upStreams):
			if v == stream:
				del(bot.upStreams[k])
	else:
		bot.reply("{0} isn't in the stream list".format(stream))
delstream.commands = ['delstream']

def addStreamChannel(bot, input):
	if not input.admin: return False
	if not input.group(2): return
	chan = input.group(2).lower()
	if chan in bot.config.stream_announce:
		bot.reply("Already announcing to that channel")
	else:
		bot.config.set_add('stream_announce', chan)
		bot.reply("Added channel to announce list")
addStreamChannel.commands = ['addstreamchan']

def delStreamChannel(bot, input):
	if not input.admin: return False
	if not input.group(2): return
	chan = input.group(2).lower()
	if chan in bot.config.stream_announce:
		bot.config.set_del('stream_announce', chan)
		bot.reply("Removed channel from announce list")
	else:
		bot.reply("Channel not in announce list")
delStreamChannel.commands = ['delstreamchan']

def GetOnlineStreams(bot):
	for stream in bot.config.streams:
		url = "http://api.justin.tv/api/stream/list.json?channel={0}".format(stream)
		try:
			jstr = json.loads(urlopen(url).read())
			if len(jstr) > 0:
				if stream not in bot.upStreams:
					bot.upStreams.append(stream)
					Broadcast(bot, stream)
			else:
				for k, v in enumerate(bot.upStreams):
					if v == stream:
						del(bot.upStreams[k])
		except: pass

def Broadcast(bot, stream):
	if stream in lastAnnounced and ( lastAnnounced[stream] + bot.config.stream_announce_interval ) > time.time():
		return

	lastAnnounced[stream] = time.time()

	string = "Stream: ^r{0}^* has come online! ^gtwitch.tv/{0}^*".format(stream)

	if bot.config.stream_announce_clan and 'name' in bot.clan_info:
		channame = "clan {0}".format(bot.clan_info['name'].lower())
		if channame in bot.chan2id:
			chanid = bot.chan2id[channame]
			bot.write_packet(ID.HON_SC_CHANNEL_EMOTE, string, chanid)
		bot.write_packet(ID.HON_CS_CLAN_MESSAGE, string)

	for chanName in bot.config.stream_announce:
		if chanName.lower() in bot.chan2id:
			chanid = bot.chan2id[chanName.lower()]
			bot.write_packet(ID.HON_SC_CHANNEL_EMOTE, string, chanid)
Broadcast.commands = ['streamtest']

def setup(bot):
	bot.lastStream = 0
	bot.upStreams = []
	bot.config.module_config('streams', [[], 'Streams for clan notification'])
	bot.config.module_config('stream_interval', [30, 'Stream checking interval'])
	bot.config.module_config('stream_announce', [[], 'Stream announcing channels'])
	bot.config.module_config('stream_announce_clan', [1, 'Announce stream in clan message/channel'])
	bot.config.module_config('stream_announce_interval', [600, 'Stream announce interval, added to prevent spam'])