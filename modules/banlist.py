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
			return conn.cursor()
		except:
			return False
	def Add(self, accountid, username):
		if not self.IsBanlisted(username):
			cursor = self.Connect()
			if not cursor: return False
			cursor.execute( "INSERT INTO banlist VALUES ('', '{0}', '{1}')".format( accountid, username ) )
			return True
		else:
			return False
	def Remove(self, username):
		if not self.IsBanlisted(username):
			return False
		else:
			cursor = self.Connect()
			if not cursor: return False
			cursor.execute( "DELETE FROM banlist WHERE nick = '{0}'".format( username ) )
			return True
	def IsBanlisted(self, value):
		cursor = self.Connect()
		if not cursor: return False
		q = "SELECT * FROM banlist WHERE accountid = '{0}' OR nick = '{0}'".format( value )
		cursor.execute( q )
		return (cursor.fetchone() is not None)

def bot_join_ban(bot, origin, data):
	for m in data[-1]:
		nick = normalize_nick(m[0]).lower()
		if bot.banlist.IsBanlisted(nick):
			for chan in bot.config.channels:
				chanid = bot.chan2id[chan.lower()]
				bot.write_packet(ID.HON_CS_CHANNEL_BAN, chanid, nick)
bot_join_ban.event = [ID.HON_SC_CHANGED_CHANNEL]
bot_join_ban.thread = True

def ply_join_ban(bot, origin, data):
	nick = normalize_nick(data[0])
	if bot.banlist.IsBanlisted(nick):
		for chan in bot.config.channels:
			chanid = bot.chan2id[chan.lower()]
			bot.write_packet(ID.HON_CS_CHANNEL_BAN, chanid, nick)
ply_join_ban.event = [ID.HON_SC_JOINED_CHANNEL]
ply_join_ban.thread = True

def ban(bot, input):
	if not input.admin: return
	if not input.group(2): return
	nick = input.group(2)
	id = bot.nick2id[nick]
	if bot.banlist.Add(id, nick):
		bot.reply("Banlisted {0}".format(nick))
		for chan in bot.config.channels:
			chanid = bot.chan2id[chan.lower()]
			bot.write_packet(ID.HON_CS_CHANNEL_BAN, chanid, nick)
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
		for chan in bot.config.channels:
			chanid = bot.chan2id[chan.lower()]
			bot.write_packet(ID.HON_CS_CHANNEL_UNBAN, chanid, nick)
	else:
		bot.reply("{0} is not banlisted".format(nick))
unban.commands = ['unban']
unban.Thread = True

def setup(bot):
	bot.config.module_config('db_host', ['localhost', 'Database host'])
	bot.config.module_config('db_user', ['honbot', 'Database user'])
	bot.config.module_config('db_pass', ['', 'Database password'])
	bot.config.module_config('db_db', ['honbot', 'Database... database!'])

	bot.banlist = Banlist(bot)