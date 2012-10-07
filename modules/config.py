import sqlite3
import json

import pickle # Legacy purposes
import os

class ConfigClass(object):
	def __init__(self,config,defaults,filename):
		self.config = config
		self.defaults = defaults
		self.filename = filename
		self.InitDB()
	def InitDB(self):
		self.conn = sqlite3.connect("{0}.db".format(self.filename), check_same_thread=False)
		c = self.conn.cursor()
		c.execute("CREATE TABLE IF NOT EXISTS config (item TEXT, value TEXT)")
		self.conn.commit()
	def doc(self,item):
		if item not in self.defaults:
			return "No such configuration key"
		return self.defaults[item][1]
	def Get(self, item):
		c = self.conn.cursor()
		c.execute("SELECT value FROM config WHERE item = ?", [item])
		row = c.fetchone()
		if row is None: return row
		try:
			js = json.loads(row[0])
			return js
		except:
			return row[0]
	def GetItems(self):
		c = self.conn.cursor()
		out = {}
		for row in c.execute("SELECT * FROM config"):
			out[row[0]] = row[1]
		return out
	def Exists(self, item):
		c = self.conn.cursor()
		c.execute("SELECT value FROM config WHERE item = ?", [item])
		return c.fetchone() is not None
	def Set(self, item, value, append=False, remove=False):
		if append:
			CurrVal = self.Get(item)
			if type(CurrVal) in [list,dict]:
				if isinstance(CurrVal, dict) and not isinstance(value, dict): return False
				CurrVal.append(value)
				value = CurrVal
			elif type(CurrVal) in [unicode,str]:
				value = [CurrVal, value]
			elif CurrVal is None:
				value = [value]
		elif remove:
			CurrVal = self.Get(item)
			if not CurrVal: return False
			if type(CurrVal) in [list,dict] and value in CurrVal:
				CurrVal.remove(value)
				value = CurrVal
		try:
			c = self.conn.cursor()
			if type(value) in [dict,list]:
				value = json.dumps(value)
			if not self.Exists(item):
				c.execute("INSERT INTO config VALUES (?, ?)", [item, value])
			else:
				c.execute("UPDATE config SET value = ? WHERE item = ?", [value, item])
			self.conn.commit()
			return True
		except:
			return False
	def __getattr__(self, item):
		if item in ['config','defaults']:
			raise AttributeError, item
		if hasattr(self.config, item):
			return getattr(self.config, item)
		elif self.Get(item) is not None:
			return self.Get(item)
		elif item in self.defaults:
			return self.defaults[item][0]
		return None
	def module_config(self, item, value):
		self.defaults[item] = value
	def set(self, key, value):
		return self.Set(key, value)
	def set_add(self, key, value):
		return self.Set(key, value, append=True)
	def set_del(self, key, value):
		return self.Set(key, value, remove=True)
def config(bot, input):
	if not input.admin:
		return False
	if not input.group(2):
		items = str( bot.config.GetItems() )
		bot.reply( items )
		print( items )
	else:
		try:
			item, value = input.group(2).split(' ', 1)
			bot.config.Set( item, value )
			bot.reply( "OK" )
		except:
			value = bot.config.__getattr__( input.group(2) )
			bot.reply( str(value) )
config.commands = ['config']
def configmigrate(bot, input):
	if not input.owner: return False
	confpath = os.path.splitext(bot.config.__file__)[0] + 'db'
	if os.path.exists(confpath):
		legacy = pickle.load(open(confpath,'r'))
		for key in legacy:
			if key in ['banlist', 'db_pass']: continue
			print("Adding {0}".format(key))
			bot.config.Set(key, legacy[key])
	else:
		bot.reply("No config file to migrate!")
configmigrate.commands = ['configmigrate']

def setup(bot):
	defaults = {
		'officer_admin'		: [1 , "If set bot's clan officers/leaders will be treated as admins"],
		'cooldown'			: [3 , "Per-user cooldown in seconds"],
		'channel_cooldown'	: [30, "Channel answer cooldown"],
		'channels'			: [[], "Set of channels to join, use part/join commands to conveniently modify it"],
		'admins'			: [[bot.config.owner], "Set of nicks for admin status, use admin add/del commands to conveniently modify it"],
		'ignore'			: [[], "Set of nicks to ignore. Use ignore add/dell to modify"],
		'banlist'			: [[], "Set of nicks to ban on sight. Use ban/unban to modify"]
	}
	bot.config = ConfigClass(bot.config, defaults, bot.config.nick)