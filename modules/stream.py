from urllib import urlopen
import json
import time
from hon.packets import ID

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
	bot.write_packet(ID.HON_CS_CLAN_MESSAGE, "Stream: ^r{0}^* has come online! ^gtwitch.tv/{0}^*".format(stream))

def setup(bot):
	bot.lastStream = 0
	bot.upStreams = []
	bot.config.module_config('streams', [[], 'Streams for clan notification'])
	bot.config.module_config('stream_interval', [30, 'Stream checking interval'])