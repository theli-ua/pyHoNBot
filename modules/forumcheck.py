#!/usr/bin/env python
"""
"""

def applycheck(bot, input):
	"""Check if you application has been successful"""
	if not input.admin: return
	if not 'vb' in bot:
		bot.reply('Error: Unable to check application')
		return
	bot.reply('Please wait, checking...')
	if not bot.vb.Login(bot.config.forumuser,bot.config.forumpassword):
		bot.reply('Error: Unable to check application')
		print("Forum credentials are invaid")
		return
	traineeApps = bot.vb.GetThreads(36, 30)
	for threadinfo in traineeApps:
		thread = threadinfo['thread']
		if thread['preview'].lower().find(input.nick.lower()) > 0:
			bot.reply("Welcome to Project Epoch, %s! Inviting now." % input.nick)
			return
	mentorApps = bot.vb.GetThreads(38, 30)
	for threadinfo in mentorApps:
		thread = threadinfo['thread']
		if thread['preview'].lower().find(input.nick.lower()) > 0:
			bot.reply("Welcome to Project Epoch, %s! Inviting now." % input.nick)
			return
applycheck.commands = ['apply']

if __name__ == '__main__': 
    print __doc__.strip()