#!/usr/bin/env python
"""
"""

def applycheck(bot, input):
	"""Check if you application has been successful"""
	if not input.admin: return
	try:
		bot.reply('Please wait, checking...')
		if not bot.vb.Login(bot.config.forumuser,bot.config.forumpassword):
			bot.reply('Error: Unable to check application at this time')
			print("Forum credentials are invaid")
			return
		traineeApps = bot.vb.GetThreads(36, 30)
		for threadinfo in traineeApps:
			thread = threadinfo['thread']
			if thread['preview'].lower().find(input.nick.lower()) > 0:
				bot.reply("Welcome to Project Epoch, %s! Inviting now." % input.nick)
				bot.vb.NewReply( thread['threadid'], "Invited", "Player has been invited to the clan.")
				return
		mentorApps = bot.vb.GetThreads(38, 30)
		for threadinfo in mentorApps:
			thread = threadinfo['thread']
			if thread['preview'].lower().find(input.nick.lower()) > 0:
				bot.reply("Welcome to Project Epoch, %s! Inviting now." % input.nick)
				bot.vb.NewReply( thread['threadid'], "Invited", "Player has been invited to the clan.")
				return
		bot.reply("Error: No application found for your username.")
	except:
		bot.reply('Error: Unable to check application at this time')
applycheck.commands = ['apply']

if __name__ == '__main__': 
    print __doc__.strip()