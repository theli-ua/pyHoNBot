#!/usr/bin/env python
"""
"""

from hon.packets import ID
import re
from time import time
from utils.forum import VB
import sys
import traceback

check_time = {}
appForums = {
	34: "C",
	35: "C",
	# 36: "A", # What if they got kicked out? They could use this to get back in. So accepted subforum is ignored
	37: "D",
	# 38: "A", # What if they got kicked out? They could use this to get back in. So accepted subforum is ignored
	39: "D",
	50: "H",
	51: "D",
	52: "H",
	53: "D"
}

def __cooldown(accountid):
	if accountid in check_time:
		if (check_time[accountid] + 60) > time():
			return False
		else:
			check_time[accountid] = time()
			return True
	else:
		check_time[accountid] = time()
		return True

def apply(bot, input):
	"""Check if you application has been successful, Once every minute"""
	try:
		vb = VB(bot.config.forumurl,bot.config.forumapikey)
		if not vb.Login(bot.config.forumuser,bot.config.forumpassword):
			bot.reply('Unable to check application at this time')
			print("Forum credentials are invaid")
			return
		if input.admin and input.group(2):
			nick = input.group(2).lower()
			aid = bot.nick2id[nick]
		else:
			nick = input.nick
			aid = input.account_id
		if not input.admin and not __cooldown(aid):
			return
		if aid in bot.clan_roster:
			bot.reply("You're already in {0}, silly.".format( bot.clan_info['name'] ))
			return
		bot.write_packet( ID.HON_SC_WHISPER, input.nick, "Fetching application status, please wait..." )
		searchid = vb.Search( 1, "in-game username?: {0}".format(nick) )
		if searchid:
			print("Search ID for {0} is {1}".format( nick, searchid ))
			results = vb.ProcessSearch(searchid)
			if not results or len(results) == 0:
				bot.reply("No application found for your username.")
				return
			print("Search results: {0}".format(len(results)))
			for result in results:
				thread = result['thread']
				if int(thread['forumid']) in appForums and thread['preview'].lower().find(nick) > 0:
					state = appForums[ int(thread['forumid']) ]
					if state == "C":
						if len(thread['prefix_rich']) > 0:
							if thread['prefix_rich'].find("APPROVED") > 0:
								state = "A"
							elif thread['prefix_rich'].find("DENIED") > 0:
								state = "D"
							elif thread['prefix_rich'].find("CHECK") > 0:
								state = "H"
						else:
							state = "H"
					if state == "A":
						bot.reply("Welcome to Project Epoch, %s!" % nick)
						bot.write_packet(ID.HON_CS_CLAN_ADD_MEMBER, nick)
						bot.reply("Invited!")

						if thread['forumid'] == 34:
							vb.NewPost( thread['threadid'], "Invited", "Player has been invited to the clan.")
							vb.MoveThread( thread['threadid'], 36 )
						elif thread['forumid'] == 35:
							vb.NewPost( thread['threadid'], "Invited", "Player has been invited to the clan.")
							vb.MoveThread( thread['threadid'], 38 )
					elif state == "D":
						bot.reply("Sorry, your application was denied.")
					elif state == "H":
						bot.reply("Your application is pending.")
					return
		else:
			bot.reply('Unable to check application at this time')
			print("SearchID not returned")
	except Exception as inst:
		traceback.print_exc()
		bot.reply('Unable to check application at this time')
apply.commands = ['apply']
if __name__ == '__main__': 
    print __doc__.strip()