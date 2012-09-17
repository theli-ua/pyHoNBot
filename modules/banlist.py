#!/usr/bin/env python
"""
"""

import MySQLdb
from hon.honutils import normalize_nick

class Banlist:
	def __init__(self, bot):
		self.Yes = self.Connect(bot.config.db_host, bot.config.db_user, bot.config.db_pass, bot.config.db_db)
		if not self.Yes:
			print("SQL connection failed")
		else:
			print("SQL connected")
	def Connect(self, host, username, password, database, Port=3306):
		try:
			self.conn = MySQLdb.connect(
					host=host,
					user=username,
					passwd=password
					db=database)
			self.db = self.conn.cursor()
			return True
		except:
			return False
	def Escape(self, str):
		return _mysql.escape_string(str)
	def Add(self, accountid, username):
		if not self.Yes: return False
		if not self.IsBanlisted(username):
			self.db.execute( "INSERT INTO banlist VALUES ('', '{0}', '{1}')".format( accountid, username ) )
			return True
		else:
			return False
	def Remove(self, username):
		if not self.Yes: return False
		if not self.IsBanlisted(username):
			return False
		else:
			self.db.execute( "DELETE FROM banlist WHERE nick = '{0}'".format( username ) )
			return True
	def IsBanlisted(self, value):
		if not self.Yes: return False
		self.db.execute( "SELECT * FROM banlist WHERE accountid = '{0}' OR nick = '{0}'".format( accountid ) )
		return ( self.db.rowcount() > 0 )
	def Close(self):
		self.db.close()
		self.conn.close()

def bot_join_ban(bot, origin, data):
	for m in data[-1]:
        nick = normalize_nick(m[0]).lower()
        if bot.banlist.IsBanlisted(nick):
			for chan in bot.config.channels:
				chanid = bot.chan2id[chan.lower()]
				bot.write_packet(ID.HON_CS_CHANNEL_BAN, chanid, nick)
bot_join_ban.event = [ID.HON_SC_CHANGED_CHANNEL]

def ply_join_ban(bot, origin, data):
	nick = normalize_nick(data[0])
	if bot.banlist.IsBanlisted(nick):
		for chan in bot.config.channels:
			chanid = bot.chan2id[chan.lower()]
			bot.write_packet(ID.HON_CS_CHANNEL_BAN, chanid, nick)
ply_join_ban.event = [ID.HON_SC_JOINED_CHANNEL]

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

def setup(bot):
	bot.config.module_config('db_host', ['localhost', 'Database host'])
	bot.config.module_config('db_user', ['honbot', 'Database user'])
	bot.config.module_config('db_pass', ['', 'Database password'])
	bot.config.module_config('db_db', ['honbot', 'Database... database!'])

	bot.banlist = Banlist(bot)