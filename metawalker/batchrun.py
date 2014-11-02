#!/usr/bin/python
import sys
import subprocess

#hostsuf = 'ubt8n.plfs'
#np = 8
#hostsuf = 'noloop32n.plfs'
if len(sys.argv) != 4:
    print "usage: hostsuf np command"
    print "for example: ME noloop32n 32 hostname"
    exit(1)

hostsuf = sys.argv[1] + ".plfs"
np = int(sys.argv[2])
command = sys.argv[3]

hostlist = []

for i in range(np):
    prefix = 'h'+str(i)
    hname = '.'.join( [prefix, hostsuf] )
    hostlist.append(hname)

print hostlist

cmd = ['mpirun', 
       '-np', np,
       '-H', ','.join(hostlist),
       'sudo',
       'bash',
       '-c',
       command]
#cmd = ['mpirun', 
       #'-np', np,
       #'-H', ','.join(hostlist),
       #'sudo',
       #'hostname']

cmd = [str(x) for x in cmd]
subprocess.call( cmd )



