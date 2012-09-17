#!/usr/bin/env python
"""
"""

import MySQLdb
from hon.honutils import normalize_nick
from hon.packets import ID

class Banlist:
	def __init__(self, bot):
		self.host = bot.config.db_host
		self.user = bot.config.db_user
		self.password = bot.config.db_pass
		self.database = bot.config.db_db
	def Connect(self):
		try:
			conn = MySQLdb.connect(
					host=self.host,
					user=self.user,
					passwd=self.password,
					db=self.database)
			return {"db": conn, "cursor": conn.cursor()}
		except:
			return False
	def Add(self, accountid, username):
		if not self.IsBanlisted(username):
			conn = self.Connect()
			if not conn: return False
			conn['cursor'].execute( "INSERT INTO banlist (accountid, nick) VALUES (%s, %s)", [accountid, username] )
			conn['db'].commit()
			return True
		else:
			return False
	def Remove(self, username):
		if not self.IsBanlisted(username):
			return False
		else:
			conn = self.Connect()
			if not conn: return False
			conn['cursor'].execute( "DELETE FROM banlist WHERE nick = %s", [username] )
			conn['db'].commit()
			return True
	def IsBanlisted(self, value):
		conn = self.Connect()
		if not conn: return False
		conn['cursor'].execute( "SELECT * FROM banlist WHERE accountid = %s OR nick = %s", [value, value] )
		return (conn['cursor'].fetchone() is not None)

def bot_join_ban(bot, origin, data):
	for m in data[-1]:
		nick = normalize_nick(m[0]).lower()
		if bot.banlist.IsBanlisted(nick):
			for chan in bot.channel_channels.keys():
				bot.write_packet(ID.HON_CS_CHANNEL_BAN, chanid, nick)
bot_join_ban.event = [ID.HON_SC_CHANGED_CHANNEL]

def ply_join_ban(bot, origin, data):
	nick = normalize_nick(data[0])
	if bot.banlist.IsBanlisted(nick):
		for chan in bot.channel_channels.keys():
			bot.write_packet(ID.HON_CS_CHANNEL_BAN, chanid, nick)
ply_join_ban.event = [ID.HON_SC_JOINED_CHANNEL]

def ban(bot, input):
	if not input.admin: return
	if not input.group(2): return
	nick = input.group(2)
	id = bot.nick2id[nick]
	if bot.banlist.Add(id, nick):
		bot.reply("Banlisted {0}".format(nick))
		bot.write_packet(ID.HON_CS_CHANNEL_BAN, input.origin[2], nick)
	else:
		bot.reply("{0} is already banlisted".format(nick))
ban.commands = ['ban']
ban.thread = True

def unban(bot, input):
	if not input.admin: return
	if not input.group(2): return
	nick = input.group(2)
	if bot.banlist.Remove(nick):
		bot.reply("Removed {0} from banlist".format(nick))
		for chan in bot.channel_channels.keys():
			if bot.id2chan[chan].find("Group") > 0: continue
			bot.write_packet(ID.HON_CS_CHANNEL_UNBAN, chan, nick)
	else:
		bot.reply("{0} is not banlisted".format(nick))
unban.commands = ['unban']
unban.thread = True

def migrate(bot, input):
	if not input.owner: return
	print("Starting")
	for ban in bot.config.banlist:
		if not bot.banlist.Add('imported', ban):
			print("{0} already in list".format(ban))
	print("Finished")
migrate.commands = ['migrate']
migrate.thread = True


def setup(bot):
	bot.config.module_config('db_host', ['localhost', 'Database host'])
	bot.config.module_config('db_user', ['honbot', 'Database user'])
	bot.config.module_config('db_pass', ['', 'Database password'])
	bot.config.module_config('db_db', ['honbot', 'Database... database!'])

	bot.banlist = Banlist(bot)