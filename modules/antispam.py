#!/usr/bin/env python
"""
"""
from hon.packets import ID
from time import time

def silence(bot, chanid, nick):
	if bot.config.spam_silence == 0:
		return
	bot.write_packet(ID.HON_CS_CHANNEL_SILENCE_USER, chanid, nick, ((60 * bot.config.spam_silence) * 1000))

def checkSpam(bot, origin, data):
	chanid = origin[2]
	nick = bot.id2nick[origin[1]].lower()
	t = time()
	if nick in bot.spamcd:
		if len(bot.spamcd[nick]) >= 4:
			shouldSilence = True
			for times in bot.spamcd[nick]:
				if times < (t - 10):
					shouldSilence = False
			if shouldSilence:
				silence(bot, chanid, nick)
			del(bot.spamcd[nick])
		else:
			bot.spamcd[nick].append(t)
	else:
		bot.spamcd[nick] = [t]
checkSpam.event = [ID.HON_SC_CHANNEL_MSG]
checkSpam.thread = True

def setup(bot):
	bot.spamcd = {}
	bot.config.module_config('spam_silence', [10, 'Silence for x minutes when spam detected, 0 = disabled'])