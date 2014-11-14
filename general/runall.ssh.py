import sys
import time
import subprocess

# this python program copy [filepath] to [destdir] on nodes

# in file configuration
#suffix = '.noloop.plfs'

if len(sys.argv) != 6:
    print "usage:", sys.argv[0], "nodes prefix suffix 'cmd' sync/async"
    print "the format of nodes is 0,2,.. or 1-10, or the mix"
    print "I don't do much checking, you'd better be reasonable"
    print "example:"
    print " python runall.ssh.py 0-4 h .noloop.plfs 'sleep 2' async"
    exit(1)

nodes = sys.argv[1]
prefix = sys.argv[2]
suffix = sys.argv[3]
bashcmd = sys.argv[4]
syncmode = sys.argv[5]

def generate_node_names(prefix, suffix, nodestr):
    # get all node names
    numbers = nodestr.split(",")
    nlist = []
    for n in numbers:
        if '-' in n:
            a,b = n.split('-')
            a = int(a)
            b = int(b)
            for i in range(a, b+1):
                nlist.append(i)
        else:
            nlist.append(n)

    nlist = [str(x) for x in nlist]
    nlist = [ prefix + x + suffix for x in nlist ] 

    return nlist


nodelist = generate_node_names(prefix, suffix, nodes)

bashcmd = "'" + bashcmd + "'"
proclist = []
for node in nodelist:
    cmd = ['ssh', node, 'bash', '-c', bashcmd]
    print cmd
    proc = subprocess.Popen(cmd)
    if syncmode == 'sync':
        proc.wait()
    else:
        dict = { 'node': node,
                 'proc': proc }
        proclist.append( dict )

if syncmode == 'async':
    # wait for subprocess to finish
    unfinished_nodes = [ proc['node'] for proc in proclist ]

    while len( unfinished_nodes ) > 0:
        print '*******************'
        for proc in proclist:
            ret = proc['proc'].poll()
            print proc['node'], 'return', ret, '(None means not terminated)', bashcmd
            if ret != None and proc['node'] in unfinished_nodes:
                unfinished_nodes.remove(proc['node'])
        time.sleep(1)

