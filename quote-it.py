import sys,os

argv = sys.argv

items = []
for line in sys.stdin:
    #words = line.split(' ')
    elems = line.split()
    items.extend(elems)

s = '",\n"'.join(items)
s = '"' + s + '"'
print s
    
exit(1)

if len(argv) != 3:
    print 'Usage:', argv[0], 'string sep'
    print 'Example:', argv[0], 'a,b,c', ','
    print '  output: "a","b","c"'
    exit(1)

s = argv[1]
sep = argv[2]

s = '"' + s + '"'
items = s.split(sep)
squote = '","'.join(items)
print squote


