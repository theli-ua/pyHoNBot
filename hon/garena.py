import socket,struct

def get_garena_token(user,password,region):
    if region == 'cis':
        GARENA_AUTH_SERVER = 'Honsng_cs.mmoauth.garena.com'
    else:
        GARENA_AUTH_SERVER = 'hon.auth.garenanow.com'
    PORT = 8005
    ip_region = 'XX'.encode('utf8')

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((GARENA_AUTH_SERVER, PORT))

    user = user.encode('utf8')
    password = password.encode('utf8')

    data = struct.pack('<IHHB16s33s5s',0x3b,0x0101,0x80,0,user,password,ip_region)
    s.send(data)
    data = s.recv(42)
    s.close()
    parsed = struct.unpack('<IB32sBI',data)
    return parsed[2]
