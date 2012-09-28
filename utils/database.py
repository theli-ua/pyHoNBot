#!/usr/bin/env python
"""Mysql Connector"""

try:
	import MySQLdb
except:
	pass

import json

class DB:
	def __init__(self, bot):
		try:
			test = MySQLdb
		except:
			print("MySQLdb Module missing")
			return
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
		except Exception, inst:
			print(inst)
			return False
	def Config(self, item, value=None, append=False):
		conn = self.Connect()
		if not conn: return None
		if value is None:
			conn['cursor'].execute( "SELECT value FROM config WHERE name = %s", [item] )
			ret = conn['cursor'].fetchone()
			if ret is None: return None
			return json.loads(ret[0])
		else:
			try:
				conn['cursor'].execute( "SELECT value FROM config WHERE name = %s", [item] )
				curr = conn['cursor'].fetchone()
				if curr is not None:
					if isinstance(value, dict) and append:
						curr = json.loads(curr[0])
						for key in curr.keys():
							value[key] = curr[key]
					value = json.dumps(value)
					conn['cursor'].execute( "UPDATE config SET value = %s WHERE name = %s", [value, item] )
					conn['db'].commit()
				else:
					item = str(item)
					value = json.dumps(value)
					conn['cursor'].execute( "INSERT INTO config (name, value) VALUES (%s, %s)", [item, value] )
					conn['db'].commit()
				return True
			except Exception, inst:
				print(inst)
				return False