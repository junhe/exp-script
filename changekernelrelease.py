import sys

argv = sys.argv

if len(argv) != 3:
    print "usage:", argv[0], 'conf-path new-releasename'
    exit(1)

confpath = argv[1]
newname  = argv[2]

f = open(confpath, 'r')
lines = f.readlines()
f.close()

# backup
f2 = open(confpath+'.bak', 'w')
f2.writelines(lines)
f2.close()

prefix = "CONFIG_LOCALVERSION="
f = open(confpath, 'w')
for line in lines:
    if line.startswith(prefix):
        line = prefix + '"' + newname + '"' + '\n'
    f.write(line)
f.close()

print 'success to', newname


