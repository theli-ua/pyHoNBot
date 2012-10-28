#!/usr/bin/env python
"""
"""
import sqlite3
from hon.honutils import normalize_nick
from hon.packets import ID
from datetime import datetime

class Banlist:
	def __init__(self, bot, filename=None):
		self.mode = bot.config.db_mode
		if filename is not None:
			self.database = filename
		else:
			self.database = bot.nick
		self.Connect()
	def Connect(self):
		try:
			self.conn = sqlite3.connect(self.database+".db")
			tmpc = self.conn.cursor()
			tmpc.execute("CREATE TABLE IF NOT EXISTS banlist ( accountid TEXT, nick TEXT, admin TEXT, date TEXT )")
			self.conn.commit()
			self.AddAdminColumn() # Backwards compatibility
		except Exception, inst:
			print(inst)
			return False
	def AddAdminColumn(self):
		if not self.conn: return
		try:
			c = self.conn.cursor()
			c.execute("ALTER TABLE banlist ADD COLUMN admin TEXT")
			c.execute("ALTER TABLE banlist ADD COLUMN date TEXT")
			self.conn.commit()
		except: pass
	def Add(self, accountid, username, adminName='Unknown'):
		if not self.IsBanlisted(username):
			if not self.conn: return False
			c = self.conn.cursor()
			theDate = str(datetime.now()).split(" ")[0]
			c.execute( "INSERT INTO banlist (accountid, nick, admin, date) VALUES (?, ?, ?, ?)", [accountid, username, adminName, theDate] )
			self.conn.commit()
			return True
		else:
			return False
	def Remove(self, username):
		if not self.IsBanlisted(username):
			return False
		else:
			if not self.conn: return False
			c = self.conn.cursor()
			c.execute( "DELETE FROM banlist WHERE lower(nick) = ?", [username.lower()] )
			self.conn.commit()
			return True
	def IsBanlisted(self, value):
		if not self.conn: return False
		c = self.conn.cursor()
		c.execute( "SELECT * FROM banlist WHERE lower(nick) = ?", [value.lower()] )
		return (c.fetchone() is not None)
	def GetBan(self, value):
		if not self.conn: return False
		c = self.conn.cursor()
		c.execute( "SELECT * FROM banlist WHERE lower(nick) = ?", [value.lower()] )
		row = c.fetchone()
		if row is not None:
			return c.fetchone()
		else:
			return False
	def Count(self):
		if not self.conn: return False
		c = self.conn.cursor()
		c.execute("SELECT COUNT(*) FROM banlist")
		return c.fetchone()[0]


def bot_join_ban(bot, origin, data):
	for m in data[-1]:
		nick = normalize_nick(m[0]).lower()
		if bot.banlist.IsBanlisted(nick):
			for chan in bot.channel_channels.keys():
				bot.write_packet(ID.HON_CS_CHANNEL_BAN, chan, nick)
bot_join_ban.event = [ID.HON_SC_CHANGED_CHANNEL]
bot_join_ban.thread = False

def ply_join_ban(bot, origin, data):
	nick = normalize_nick(data[0])
	if bot.banlist.IsBanlisted(nick):
		for chan in bot.channel_channels.keys():
			bot.write_packet(ID.HON_CS_CHANNEL_BAN, chan, nick)
ply_join_ban.event = [ID.HON_SC_JOINED_CHANNEL]
ply_join_ban.thread = False

def ban(bot, input):
	if not input.admin: return False
	if not input.group(2): return
	nick = input.group(2).lower()
	id = "unknown"
	if nick in bot.nick2id:
		id = bot.nick2id[nick]
	if bot.banlist.Add(id, nick, input.nick):
		bot.reply("Banlisted {0}".format(nick))
		bot.write_packet(ID.HON_CS_CHANNEL_BAN, input.origin[2], nick)
	else:
		bot.reply("{0} is already banlisted".format(nick))
ban.commands = ['ban']
ban.thread = False

def unban(bot, input):
	if not input.admin: return False
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
unban.thread = False

def bancount(bot, input):
	bot.reply("There are {0} banned users".format(bot.banlist.Count()))
bancount.commands = ['bancount']
bancount.thread = False

def baninfo(bot, input):
	if not input.admin: return False
	if not input.group(2): return
	nick = input.group(2)
	if bot.banlist.IsBanlisted(nick):
		info = bot.banlist.GetBan(nick)
		if info:
			bot.reply("{0} was banned by {1} on {2}".format(info[1], info[2], info[3]))
		else:
			bot.reply("There was an error fetching the ban info.")
	else:
		bot.reply("{0} is not banlisted".format(nick))
baninfo.commands = ['baninfo']
baninfo.thread = False

def migrate(bot, input):
	if not input.owner: return
	print("Starting")
	for ban in bot.config.banlist:
		if not bot.banlist.Add('imported', ban):
			print("{0} already in list".format(ban))
	print("Finished")
migrate.commands = ['migrate']
migrate.thread = False

def setup(bot):
	bot.config.module_config('db_mode', ['sqlite', 'Database Mode'])
	bot.banlist = Banlist(bot)