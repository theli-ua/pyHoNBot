#!/usr/bin/env python
# (c) 2011 Anton Romanov
#
#

import os, sys
import socket, asyncore, asynchat
from hon import masterserver,packets
 
class Bot( asynchat.async_chat ):
    def __init__( self ):
        asynchat.async_chat.__init__( self )   
        self.buffer = ''

 
    def write( self, data ):
        self.push(data)
 
    #def handle_close( self ):
        #print 'disconnected'

    def handle_connect( self ):
        print 'connected'
        self.set_terminator( 2 )
        self.got_len = False
        self.write(packets.packet_factory.pack(packets.ID.HON_CS_AUTH_INFO,self.account_id,
            self.cookie,self.ip,self.auth_hash,packets.ID.HON_PROTOCOL_VERSION,
            5,0))
        pass

    def collect_incoming_data( self, data ):
        print 'incoming data'
        self.buffer += data
 
    def found_terminator( self ):
        print 'xxxxxxx'
        print self.buffer
        #exit(1)

    def run( self, login, password ):
        auth_data = masterserver.auth(login,password)
        self.create_socket( socket.AF_INET, socket.SOCK_STREAM )
        self.ip = auth_data['ip']
        self.cookie = auth_data['cookie']
        self.account_id = int(auth_data['account_id'])
        self.auth_hash = auth_data['auth_hash']
        self.got_len = False
        self.nick = auth_data['nickname']
        self.connect( ( auth_data['chat_url'], packets.ID.HON_CHAT_PORT ) )
        asyncore.loop()
 
# attemptfork is thanks to phenny irc bot ( http://inamidst.com/phenny/ )
def attemptfork(): 
    try: 
        pid = os.fork()
        if pid > 0:
            sys.exit( 0 )
    except OSError, e: 
        raise OSError( 'Could not daemonize process: %d ( %s )' % ( e.errno, e.strerror ) )
    os.setsid()
    os.umask( 0 )
    try: 
        pid = os.fork()
        if pid > 0: 
            sys.exit( 0 )
    except OSError, e: 
        raise OSError( 'Could not daemonize process: %d ( %s )' % ( e.errno, e.strerror ) )
 
# load our config
#conf = irc_config.config
 
#if conf.d == 0 and conf.b == 1 and hasattr( os, 'fork' ): 
    #attemptfork()
 
# initialize
#mypybot = Bot( conf )
 
# and run
#mypybot.run( conf.s, conf.p )
import sys
mybot = Bot()
mybot.run(sys.argv[1],sys.argv[2])
