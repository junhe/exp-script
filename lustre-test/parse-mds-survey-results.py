import sys,re

fpat = sys.argv[1]

resulttable = []
with open(fpat) as f:
    for line in f:
        line = line.replace('[', '')
        line = line.replace(']', '')

        items = line.split()
        d = {}
        for i,item in enumerate(items):
            if re.match(r'[a-zA-Z]+', item):
                d[item] = items[i+1]
            else:
                pass
        resulttable.append(d)

header = resulttable[0].keys()
headershow = [x.ljust(10) for x in header]
print ' '.join(headershow)
for row in resulttable:
    values = [str(row[e]) for e in header]
    values = [x.ljust(10) for x in values]
    print ' '.join(values)









