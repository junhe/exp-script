import socket

hname = socket.gethostname()
print '.'.join( hname.split('.')[0:2] )
