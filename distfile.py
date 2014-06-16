import sys
import subprocess

# this python program copy [filepath] to [destdir] on nodes

# in file configuration
prefix = 'h'
#suffix = '.noloop.plfs'

if len(sys.argv) != 5:
    print "usage:", sys.argv[0], "filepath nodes suffix destdir"
    print "the format of nodes is 0,2,.. or 1-10, or the mix"
    print "I don't do much checking, you'd better be reasonable"
    exit(1)


filepath = sys.argv[1]
nodes = sys.argv[2]
suffix = sys.argv[3]
destdir = sys.argv[4]

print filepath, nodes, destdir

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

for node in nodelist:
    cmd = ['scp', filepath, node + ':' + destdir]
    print cmd
    subprocess.call(cmd)


