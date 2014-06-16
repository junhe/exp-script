import sys
import time
import subprocess

# this program keeps looping until all commands
# are success


# in file configuration
prefix = 'h'
#suffix = '.noloop.plfs'

if len(sys.argv) != 4:
    print "usage:", sys.argv[0], "nodes suffix 'cmd'"
    print "the format of nodes is 0,2,.. or 1-10, or the mix"
    print "I don't do much checking, you'd better be reasonable"
    print "example:"
    print " python runall.ssh.py 0-4 .noloop.plfs 'sleep 2'"
    exit(1)

nodes = sys.argv[1]
suffix = sys.argv[2]
bashcmd = sys.argv[3]

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

while True:
    goodcnt = 0
    print '***********'
    for node in nodelist:
        cmd = ['ssh',
                '-o', 'ConnectTimeout=10',
                '-o', 'BatchMode=yes',
                node, 'exit']
        print cmd
        ret = subprocess.call(cmd)
        print node, 'returned', ret
        if ret == 0:
            goodcnt += 1
    if goodcnt == len(nodelist):
        break
    time.sleep(1)

